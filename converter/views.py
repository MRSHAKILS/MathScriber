from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
import json

from .models import UploadedImage
from .forms import MultipleImageUploadForm
from .ocr_utils import process_image_to_latex, validate_image

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
                    # Validate file type
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
                    if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                        messages.error(request, f"File {image.name} is not a valid image format.")
                        continue
                    
                    # Save the uploaded image
                    uploaded_image = UploadedImage.objects.create(
                        image=image,
                        task=task,
                        latex_output=""  # Will be updated after processing
                    )
                    
                    # Process the image to get LaTeX output
                    image_path = uploaded_image.image.path
                    if validate_image(image_path):
                        latex_output = process_image_to_latex(image_path, task)
                        uploaded_image.latex_output = latex_output
                        uploaded_image.save()
                        
                        processed_images.append({
                            'id': uploaded_image.id,
                            'image_url': uploaded_image.image.url,
                            'latex_output': latex_output,
                            'filename': uploaded_image.image.name,
                            'task': task
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
            messages.error(request, "Please select at least one image.")
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
