from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
import os
import json

from .models import UploadedImage
from .forms import MultipleImageUploadForm
from .ocr_utils import process_image_to_latex, validate_image, is_pdf_file, validate_pdf, process_pdf_to_latex

def upload_view(request):
    """
    Main view for handling image uploads and displaying results.
    """
    if request.method == 'POST':
        form = MultipleImageUploadForm(request.POST)
        images = request.FILES.getlist('images')  # Get multiple files
        
        if form.is_valid() and images:
            task = form.cleaned_data['task']
            processed_images = []
            
            for image in images:
                try:
                    # Validate file type - now supports images and PDFs
                    valid_image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
                    is_image = any(image.name.lower().endswith(ext) for ext in valid_image_extensions)
                    is_pdf = image.name.lower().endswith('.pdf')
                    
                    if not (is_image or is_pdf):
                        messages.error(request, f"File {image.name} is not a valid image or PDF format.")
                        continue
                    
                    # Save the uploaded file
                    uploaded_image = UploadedImage.objects.create(
                        image=image,
                        task=task,
                        latex_output=""  # Will be updated after processing
                    )
                    
                    # Process the file to get LaTeX output
                    file_path = uploaded_image.image.path
                    
                    if is_pdf:
                        # Handle PDF processing
                        if validate_pdf(file_path):
                            print(f"📄 Processing PDF: {image.name}")
                            latex_outputs = process_pdf_to_latex(file_path, task)
                            
                            # Combine all pages into one output
                            combined_latex = "\n\n".join(latex_outputs)
                            uploaded_image.latex_output = combined_latex
                            uploaded_image.save()
                            
                            processed_images.append({
                                'id': uploaded_image.id,
                                'image_url': uploaded_image.image.url,
                                'latex_output': combined_latex,
                                'filename': uploaded_image.image.name,
                                'task': task,
                                'file_type': 'PDF',
                                'page_count': len(latex_outputs)
                            })
                        else:
                            messages.error(request, f"Invalid PDF file: {image.name}")
                            uploaded_image.delete()
                    else:
                        # Handle image processing (existing logic)
                        if validate_image(file_path):
                            latex_output = process_image_to_latex(file_path, task)
                            uploaded_image.latex_output = latex_output
                            uploaded_image.save()
                            
                            processed_images.append({
                                'id': uploaded_image.id,
                                'image_url': uploaded_image.image.url,
                                'latex_output': latex_output,
                                'filename': uploaded_image.image.name,
                                'task': task,
                                'file_type': 'Image'
                            })
                        else:
                            messages.error(request, f"Invalid image file: {image.name}")
                            uploaded_image.delete()
                        
                except Exception as e:
                    messages.error(request, f"Error processing {image.name}: {str(e)}")
            
            if processed_images:
                messages.success(request, f"Successfully processed {len(processed_images)} image(s)!")
                return render(request, 'converter/results.html', {
                    'processed_images': processed_images,
                    'form': MultipleImageUploadForm()  # Fresh form for new uploads
                })
            else:
                messages.error(request, "No images were successfully processed.")
        elif not images:
            messages.error(request, "Please select at least one image or PDF file.")
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        form = MultipleImageUploadForm()
    
    # Get recent uploads for display
    recent_uploads = UploadedImage.objects.order_by('-created_at')[:10]
    
    return render(request, 'converter/upload.html', {
        'form': form,
        'recent_uploads': recent_uploads
    })

def results_view(request):
    """
    View to display all processed results.
    """
    uploads = UploadedImage.objects.order_by('-created_at')
    return render(request, 'converter/results.html', {
        'processed_images': [
            {
                'id': upload.id,
                'image_url': upload.image.url,
                'latex_output': upload.latex_output,
                'filename': upload.image.name,
                'task': upload.task,
                'created_at': upload.created_at
            }
            for upload in uploads
        ],
        'form': MultipleImageUploadForm()
    })

@require_POST
def delete_upload_view(request, upload_id):
    """
    Delete a specific upload and its associated file.
    """
    try:
        upload = get_object_or_404(UploadedImage, id=upload_id)
        
        # Delete the file from storage
        if upload.image:
            if os.path.exists(upload.image.path):
                os.remove(upload.image.path)
        
        # Delete the database record
        upload.delete()
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Upload deleted successfully'})
        else:
            messages.success(request, 'Upload deleted successfully!')
            return redirect('converter:upload')
            
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            messages.error(request, f'Error deleting upload: {str(e)}')
            return redirect('converter:upload')
