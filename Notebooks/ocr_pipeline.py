"""
Unified OCR pipeline for:
1. Handwritten Equations (pix2tex)
2. Handwritten Tables (pytesseract)

Usage:
  python ocr_pipeline.py
"""

import os
import re
import argparse
from PIL import Image

# Equation OCR (pix2tex)
from pix2tex.cli import LatexOCR

# Table OCR (pytesseract)
import pytesseract

# Optional: adjust if Tesseract not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------- EQUATION FUNCTIONS ----------
def clean_latex_code(latex_code):
    """Clean common LaTeX issues from pix2tex output"""
    latex_code = re.sub(r'\\left\.(.*?)\\right\|', r'\\left|\1\\right|', latex_code)
    latex_code = re.sub(r'\{\{(.*?)\}\}', r'\1', latex_code)
    latex_code = latex_code.replace('~', ' ')
    if not latex_code.startswith('\\['):
        latex_code = f"\\[ {latex_code} \\]"
    return re.sub(r'\s+', ' ', latex_code).strip()


def process_equations(input_dir="./test_images"):
    """Process all images in the equations folder and generate LaTeX files"""
    print("🚀 Starting Equation OCR Processing")
    print("=" * 50)
    
    # Check if directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Directory '{input_dir}' not found. Skipping equation processing.")
        return {}
    
    model = LatexOCR()
    results = {}
    processed_count = 0

    for file in os.listdir(input_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")):
            try:
                img_path = os.path.join(input_dir, file)
                img = Image.open(img_path)
                raw_latex = model(img)
                cleaned = clean_latex_code(raw_latex)

                # Save output alongside image
                output_file = os.path.join(input_dir, f"{os.path.splitext(file)[0]}_equation.tex")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(cleaned)

                results[file] = {"status": "success", "latex": cleaned, "output": output_file}
                print(f"✅ {file} → {output_file}")
                processed_count += 1

            except Exception as e:
                results[file] = {"status": "error", "error": str(e)}
                print(f"❌ Error on {file}: {e}")

    print(f"📊 Equations: Processed {processed_count} images")
    return results


# ---------- TABLE FUNCTIONS ----------
def image_to_latex_table(img_path):
    """Convert a table image → LaTeX tabular (basic OCR version)."""
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img)
    rows = text.strip().split("\n")
    if not rows:
        return ""

    latex_rows = []
    for row in rows:
        cols = row.split()
        latex_rows.append(" & ".join(cols) + r" \\")

    num_cols = max(len(r.split("&")) for r in latex_rows)
    col_format = "|c" * num_cols + "|"
    latex_table = "\\begin{tabular}{" + col_format + "}\n"
    latex_table += "\n".join(latex_rows)
    latex_table += "\n\\end{tabular}"
    return latex_table


def process_tables(input_dir="./test_tables"):
    """Process all images in the tables folder and generate LaTeX files"""
    print("\n🚀 Starting Table OCR Processing")
    print("=" * 50)
    
    # Check if directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Directory '{input_dir}' not found. Skipping table processing.")
        return {}
    
    results = {}
    processed_count = 0

    for file in os.listdir(input_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                img_path = os.path.join(input_dir, file)
                latex = image_to_latex_table(img_path)

                output_file = os.path.join(input_dir, f"{os.path.splitext(file)[0]}_table.tex")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(latex)

                results[file] = {"status": "success", "latex": latex, "output": output_file}
                print(f"✅ {file} → {output_file}")
                processed_count += 1

            except Exception as e:
                results[file] = {"status": "error", "error": str(e)}
                print(f"❌ Error on {file}: {e}")

    print(f"📊 Tables: Processed {processed_count} images")
    return results


def process_all_tasks():
    """Process both equations and tables automatically"""
    print("🔍 Starting Unified OCR Pipeline")
    print("=" * 60)
    
    # Process equations
    equation_results = process_equations("./test_images")
    
    # Process tables  
    table_results = process_tables("./test_tables")
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 PROCESSING SUMMARY")
    print("=" * 60)
    
    eq_success = sum(1 for r in equation_results.values() if r["status"] == "success")
    eq_errors = sum(1 for r in equation_results.values() if r["status"] == "error")
    
    table_success = sum(1 for r in table_results.values() if r["status"] == "success")
    table_errors = sum(1 for r in table_results.values() if r["status"] == "error")
    
    print(f"📝 Equations: {eq_success} successful, {eq_errors} errors")
    print(f"📊 Tables: {table_success} successful, {table_errors} errors")
    print(f"🎯 Total: {eq_success + table_success} files processed successfully")
    
    return {
        "equations": equation_results,
        "tables": table_results
    }


# ---------- MAIN ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified OCR Pipeline for Equations and Tables")
    parser.add_argument("--task", choices=["equations", "tables", "all"], default="all", 
                       help="Which OCR task to run (default: all)")
    args = parser.parse_args()

    if args.task == "equations":
        process_equations("./test_images")
    elif args.task == "tables":
        process_tables("./test_tables")
    else:  # "all" - default
        process_all_tasks()