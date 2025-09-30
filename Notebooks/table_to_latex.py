# table_ocr.py
import os
import pytesseract
from PIL import Image

# Set Tesseract path and tessdata prefix
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

test_folder = "./test_tables"
output_file = "tables_output.txt"

def image_to_latex_table(img_path):
    """Convert a table image → LaTeX tabular (basic version)."""
    img = Image.open(img_path)

    # OCR using pytesseract
    text = pytesseract.image_to_string(img)
    print(f"Extracted Text:\n{text}\n")
    # Split into rows
    rows = text.strip().split("\n")
    latex_rows = []

    for row in rows:
        # Convert spaces/tabs into LaTeX column separator "&"
        cols = row.split()
        latex_row = " & ".join(cols) + r" \\"
        latex_rows.append(latex_row)

    # Wrap in LaTeX tabular environment
    num_cols = max(len(r.split("&")) for r in latex_rows)
    col_format = "|c" * num_cols + "|"
    latex_table = "\\begin{tabular}{" + col_format + "}\n"
    latex_table += "\n".join(latex_rows)
    latex_table += "\n\\end{tabular}"

    return latex_table


def process_tables():
    print("🚀 Starting Table OCR Processing\n")
    results = []

    for file in os.listdir(test_folder):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            try:
                img_path = os.path.join(test_folder, file)
                latex_result = image_to_latex_table(img_path)

                results.append((file, latex_result))

                print(f"📄 FILE: {file}")
                print("─" * 60)
                print(f"📊 LaTeX Table Output:\n{latex_result}")
                print("─" * 60, "\n")

            except Exception as e:
                print(f"❌ Error with {file}: {e}\n")

    # Save all results
    with open(output_file, "w", encoding="utf-8") as f:
        for file, latex in results:
            f.write(f"{file}:\n{latex}\n\n")

    print(f"✅ Results saved to {output_file}")

if __name__ == "__main__":
    process_tables()
