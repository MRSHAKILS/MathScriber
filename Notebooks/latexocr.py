from PIL import Image
from pix2tex.cli import LatexOCR
import os
import re

def clean_latex_code(latex_code):
    """Clean and fix common LaTeX errors from OCR output"""
    # Fix \left. \right| patterns
    latex_code = re.sub(r'\\left\.(.*?)\\right\|', r'\\left|\1\\right|', latex_code)
    
    # Remove extra curly braces
    latex_code = re.sub(r'\{\{(.*?)\}\}', r'\1', latex_code)
    
    # Remove unnecessary tildes
    latex_code = latex_code.replace('~', ' ')
    
    # Ensure proper display math format
    if not latex_code.startswith('\\['):
        latex_code = f"\\[ {latex_code} \\]"
    
    # Clean extra spaces
    latex_code = re.sub(r'\s+', ' ', latex_code).strip()
    
    return latex_code

def process_images_to_latex(input_dir="./test_images", output_dir=None):
    """
    Main function to process all images in directory to LaTeX
    
    Args:
        input_dir: Path to folder containing images
        output_dir: Path to save LaTeX files (default: same as input_dir)
    
    Returns:
        dict: Processing results with filenames and LaTeX codes
    """
    if output_dir is None:
        output_dir = input_dir
    
    # Initialize model
    model = LatexOCR()
    
    # Get all images
    image_files = [f for f in os.listdir(input_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'))]
    
    if not image_files:
        return {"error": "No images found in directory"}
    
    results = {}
    
    for filename in image_files:
        image_path = os.path.join(input_dir, filename)
        
        try:
            # Process image
            img = Image.open(image_path)
            raw_latex = model(img)
            
            # Clean LaTeX output
            cleaned_latex = clean_latex_code(raw_latex)
            
            # Save to file
            output_filename = f"{os.path.splitext(filename)[0]}_latex.tex"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_latex)
            
            results[filename] = {
                'status': 'success',
                'latex_code': cleaned_latex,
                'output_file': output_filename,
                'error': None
            }
            
        except Exception as e:
            results[filename] = {
                'status': 'error',
                'latex_code': None,
                'output_file': None,
                'error': str(e)
            }
    
    return results

# Production usage example
if __name__ == "__main__":
    # Simple one-line execution
    results = process_images_to_latex("./test_images")
    
    # Print summary
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    print(f"Processing complete: {success_count}/{len(results)} successful")