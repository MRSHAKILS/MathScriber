import os
import random
from PIL import Image

def process_image_to_latex(image_path, task_type):
    """
    Mock OCR function that simulates converting images to LaTeX.
    Replace this with your actual OCR implementation.
    """
    
    # Mock LaTeX outputs for demonstration
    equation_samples = [
        r"E = mc^2",
        r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
        r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}",
        r"F(x) = \int_{-\infty}^{x} f(t) dt",
        r"\lim_{x \to 0} \frac{\sin x}{x} = 1"
    ]
    
    table_samples = [
        r"\begin{array}{|c|c|c|}\hline x & y & z \\ \hline 1 & 2 & 3 \\ 4 & 5 & 6 \\ \hline \end{array}",
        r"\begin{array}{cc} a & b \\ c & d \end{array}",
        r"\begin{array}{|l|r|}\hline \text{Name} & \text{Value} \\ \hline \text{Alpha} & 0.05 \\ \text{Beta} & 0.95 \\ \hline \end{array}"
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