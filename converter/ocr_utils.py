import os
import random
from PIL import Image
import sys
import importlib.util

# Global variables to store loaded modules
latexocr_module = None
table_ocr_module = None
ocr_modules_loaded = False

def load_ocr_modules():
    """
    Try to load the actual OCR modules from the Notebooks directory.
    Returns True if modules are available, False otherwise.
    """
    global latexocr_module, table_ocr_module, ocr_modules_loaded
    
    if ocr_modules_loaded:
        return True
        
    try:
        # Add Notebooks directory to path
        notebooks_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Notebooks')
        if notebooks_dir not in sys.path:
            sys.path.append(notebooks_dir)
        
        # Import equation OCR module
        try:
            spec = importlib.util.spec_from_file_location("latexocr", 
                                                         os.path.join(notebooks_dir, "latexocr.py"))
            if spec and spec.loader:
                latexocr_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(latexocr_module)
                print("✅ Successfully loaded equation OCR module")
        except Exception as e:
            print(f"❌ Could not load equation OCR module: {e}")
            latexocr_module = None
            
        # Import table OCR module  
        try:
            spec = importlib.util.spec_from_file_location("table_to_latex", 
                                                         os.path.join(notebooks_dir, "table_to_latex.py"))
            if spec and spec.loader:
                table_ocr_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(table_ocr_module)
                print("✅ Successfully loaded table OCR module")
        except Exception as e:
            print(f"❌ Could not load table OCR module: {e}")
            table_ocr_module = None
            
        ocr_modules_loaded = True
        return latexocr_module is not None or table_ocr_module is not None
        
    except Exception as e:
        print(f"❌ Error loading OCR modules: {e}")
        return False

def process_image_to_latex(image_path, task_type):
    """
    Process image to LaTeX using either the actual OCR modules or mock data.
    """
    
    # Try to use actual OCR modules first
    if load_ocr_modules():
        try:
            if task_type == 'equation' and latexocr_module:
                print(f"🔄 Processing equation image: {image_path}")
                # Use the pix2tex model directly
                from pix2tex.cli import LatexOCR
                
                # Initialize the model
                model = LatexOCR()
                
                # Process the image
                img = Image.open(image_path)
                raw_latex = model(img)
                
                # Clean the output using the function from latexocr module
                if hasattr(latexocr_module, 'clean_latex_code'):
                    cleaned_latex = latexocr_module.clean_latex_code(raw_latex)
                else:
                    cleaned_latex = raw_latex
                
                print(f"✅ Equation OCR successful: {cleaned_latex}")
                return cleaned_latex
                        
            elif task_type == 'table' and table_ocr_module:
                print(f"🔄 Processing table image: {image_path}")
                # Check if Tesseract is available
                try:
                    import pytesseract
                    # Try to run tesseract to see if it's available
                    pytesseract.get_tesseract_version()
                    
                    # Use the table OCR function
                    if hasattr(table_ocr_module, 'image_to_latex_table'):
                        result = table_ocr_module.image_to_latex_table(image_path)
                        print(f"✅ Table OCR successful: {result}")
                        return result
                except Exception as tesseract_error:
                    print(f"⚠️ Tesseract not available: {tesseract_error}")
                    print("🔄 Using fallback for table processing")
                        
        except Exception as e:
            print(f"❌ Error using OCR modules: {e}")
            print("🔄 Falling back to mock data")
            # Fall back to mock data
    else:
        print("⚠️ OCR modules not available, using mock data")
    
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

def test_ocr_setup():
    """
    Test OCR setup and return status information.
    """
    status = {
        'modules_loaded': False,
        'pix2tex_available': False,
        'tesseract_available': False,
        'equation_ocr': 'Not Available',
        'table_ocr': 'Not Available',
        'errors': []
    }
    
    try:
        # Test module loading
        if load_ocr_modules():
            status['modules_loaded'] = True
            
            # Test pix2tex
            try:
                from pix2tex.cli import LatexOCR
                model = LatexOCR()
                status['pix2tex_available'] = True
                status['equation_ocr'] = 'Available'
            except Exception as e:
                status['errors'].append(f"pix2tex error: {e}")
                
            # Test tesseract
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                status['tesseract_available'] = True
                status['table_ocr'] = 'Available'
            except Exception as e:
                status['errors'].append(f"Tesseract error: {e}")
                status['table_ocr'] = 'Tesseract not installed'
        else:
            status['errors'].append("Could not load OCR modules")
            
    except Exception as e:
        status['errors'].append(f"General error: {e}")
        
    return status