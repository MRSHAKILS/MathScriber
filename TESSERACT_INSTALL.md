# Installing Tesseract OCR for Table Recognition

## What's Currently Working ✅
- **Equation OCR**: Fully functional using pix2tex
- **Django Server**: Running successfully
- **Image Upload**: Working properly

## What Needs Tesseract 📋
- **Table OCR**: Converting table images to LaTeX

## Install Tesseract on Windows

### Method 1: Direct Download (Recommended)
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer
3. Run the installer and choose the default installation path: `C:\Program Files\Tesseract-OCR\`
4. Add to your PATH or the system will find it automatically

### Method 2: Using Chocolatey
```powershell
choco install tesseract
```

### Method 3: Using Scoop
```powershell
scoop install tesseract
```

## Verify Installation
After installation, restart VS Code and run this test:
```python
D:/HP/D/MathScriber/venv/Scripts/python.exe -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## Test Your Setup
Once Tesseract is installed, test the complete OCR system:
```python
D:/HP/D/MathScriber/venv/Scripts/python.exe -c "import sys; sys.path.append('d:/HP/D/MathScriber'); from converter.ocr_utils import test_ocr_setup; import json; print(json.dumps(test_ocr_setup(), indent=2))"
```

## Current Status Summary
- ✅ **Equation OCR**: Ready to use
- ⚠️ **Table OCR**: Needs Tesseract installation
- ✅ **Web Interface**: http://127.0.0.1:8000/
- ✅ **File Upload**: Working
- ✅ **Dependencies**: pix2tex installed and working