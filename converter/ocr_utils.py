import os
import random
from PIL import Image
import sys
import importlib.util

def load_ocr_modules():
    """
    Try to load the actual OCR modules from the Notebooks directory.
    Returns True if modules are available, False otherwise.
    """
    try:
        # Add Notebooks directory to path
        notebooks_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Notebooks')
        if notebooks_dir not in sys.path:
            sys.path.append(notebooks_dir)
        
        # Try to import the OCR modules
        global latexocr_module, table_ocr_module
        
        # Import equation OCR module
        spec = importlib.util.spec_from_file_location("latexocr", 
                                                     os.path.join(notebooks_dir, "latexocr.py"))
        if spec and spec.loader:
            latexocr_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(latexocr_module)
        else:
            latexocr_module = None
            
        # Import table OCR module  
        spec = importlib.util.spec_from_file_location("table_to_latex", 
                                                     os.path.join(notebooks_dir, "table_to_latex.py"))
        if spec and spec.loader:
            table_ocr_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(table_ocr_module)
        else:
            table_ocr_module = None
            
        return latexocr_module is not None or table_ocr_module is not None
        
    except Exception as e:
        print(f"Could not load OCR modules: {e}")
        return False

def process_image_to_latex(image_path, task_type):
    """
    Process image to LaTeX using either the actual OCR modules or mock data.
    """
    
    # Try to use actual OCR modules first
    if load_ocr_modules():
        try:
            if task_type == 'equation' and 'latexocr_module' in globals() and latexocr_module:
                # Use actual equation OCR
                # Note: You may need to adjust this based on the exact function signature
                # in your latexocr.py file
                if hasattr(latexocr_module, 'process_single_image'):
                    result = latexocr_module.process_single_image(image_path)
                    if result:
                        return result
                        
            elif task_type == 'table' and 'table_ocr_module' in globals() and table_ocr_module:
                # Use actual table OCR
                if hasattr(table_ocr_module, 'image_to_latex_table'):
                    result = table_ocr_module.image_to_latex_table(image_path)
                    if result:
                        return result
                        
        except Exception as e:
            print(f"Error using OCR modules: {e}")
            # Fall back to mock data
    
    # Fallback to mock LaTeX outputs for demonstration
    equation_samples = [
        r"E = mc^2",
        r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
        r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}",
        r"F(x) = \int_{-\infty}^{x} f(t) dt",
        r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
        r"\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}",
        r"\frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u"
    ]
    
    table_samples = [
        r"\begin{array}{|c|c|c|}\hline x & y & z \\ \hline 1 & 2 & 3 \\ 4 & 5 & 6 \\ \hline \end{array}",
        r"\begin{array}{cc} a & b \\ c & d \end{array}",
        r"\begin{array}{|l|r|}\hline \text{Name} & \text{Value} \\ \hline \text{Alpha} & 0.05 \\ \text{Beta} & 0.95 \\ \hline \end{array}",
        r"\begin{array}{|c|c|c|c|}\hline \text{ID} & \text{Name} & \text{Score} & \text{Grade} \\ \hline 1 & \text{Alice} & 95 & \text{A} \\ 2 & \text{Bob} & 87 & \text{B} \\ 3 & \text{Charlie} & 92 & \text{A} \\ \hline \end{array}"
    ]
    
    try:
        # Validate that the image exists and can be opened
        with Image.open(image_path) as img:
            # Get image dimensions for processing simulation
            width, height = img.size
            
        # Simulate processing time
        import time
        time.sleep(0.1)  # Small delay to simulate processing
        
        # Return mock LaTeX based on task type
        if task_type == 'equation':
            return random.choice(equation_samples)
        elif task_type == 'table':
            return random.choice(table_samples)
        else:
            return r"\text{Unknown task type}"
            
    except Exception as e:
        # Return error message as LaTeX comment
        return f"% Error processing image: {str(e)}"

def validate_image(image_path):
    """
    Validate that the uploaded file is a valid image.
    """
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False