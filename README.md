# MathScriber - LaTeX OCR Converter

A Django web application that converts images containing mathematical equations and tables to LaTeX code using OCR technology.

## Features

### Frontend Features

- **Multiple Image Upload**: Upload multiple images at once with drag-and-drop support
- **Image Preview**: Preview selected images before submission with ability to remove individual images
- **Task Selection**: Choose between "Equation" and "Table" OCR processing
- **Real-time LaTeX Rendering**: View rendered LaTeX output using MathJax
- **Copy to Clipboard**: Easily copy generated LaTeX code
- **Responsive Design**: Bootstrap-based responsive UI that works on all devices

### Backend Features

- **Multiple File Processing**: Handle multiple image uploads simultaneously
- **Database Storage**: Save all uploaded images and generated LaTeX in SQLite database
- **Image Validation**: Validate file types and image integrity
- **OCR Integration**: Supports integration with existing OCR modules
- **Error Handling**: Comprehensive error handling and user feedback
- **Media Management**: Proper handling of uploaded files with Django's media system

## Project Structure

```
MathScriber/
├── MathScriber/                # Django project settings
│   ├── settings.py            # Database, media, static files configuration
│   ├── urls.py               # Main URL configuration with media serving
│   └── ...
├── converter/                 # Main Django app
│   ├── models.py             # UploadedImage model
│   ├── views.py              # Upload and results views
│   ├── forms.py              # Multiple image upload form
│   ├── urls.py               # App URL patterns
│   ├── admin.py              # Admin interface configuration
│   ├── ocr_utils.py          # OCR processing utilities
│   └── migrations/           # Database migrations
├── templates/                # HTML templates
│   ├── base.html             # Base template with MathJax integration
│   └── converter/
│       ├── upload.html       # Image upload interface
│       └── results.html      # Results display with LaTeX rendering
├── static/                   # Static files
│   └── css/
│       └── style.css         # Custom CSS for UI styling
├── media/                    # User uploaded files
│   └── uploads/              # Uploaded images storage
├── Notebooks/                # OCR modules (your existing code)
│   ├── latexocr.py           # Equation OCR module
│   ├── table_to_latex.py     # Table OCR module
│   └── ocr_pipeline.py       # OCR pipeline
└── db.sqlite3               # SQLite database
```

## Installation & Setup

1. **Install Dependencies**:

   ```bash
   pip install Django Pillow
   ```

2. **Run Migrations**:

   ```bash
   python manage.py migrate
   ```

3. **Create Superuser** (optional):

   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**:

   ```bash
   python manage.py runserver
   ```

5. **Access Application**:
   - Main App: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Usage

### Uploading Images

1. Navigate to the upload page (home page)
2. Select content type: "Equation" or "Table"
3. Upload images by:
   - Clicking the upload area and selecting files
   - Dragging and dropping images onto the upload area
4. Preview selected images and remove any unwanted ones
5. Click "Convert to LaTeX" to process the images

### Viewing Results

- After processing, view results immediately on the results page
- See both raw LaTeX code and rendered mathematical output
- Copy LaTeX code to clipboard using the copy button
- Access all previous results through the "Results" navigation link

### Admin Interface

- Manage uploaded images and LaTeX outputs
- View processing history and statistics
- Delete or modify existing records

## Technical Implementation

### Database Model

```python
class UploadedImage(models.Model):
    TASK_CHOICES = [
        ('equation', 'Equation'),
        ('table', 'Table'),
    ]
    image = models.ImageField(upload_to='uploads/')
    task = models.CharField(max_length=10, choices=TASK_CHOICES)
    latex_output = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### File Upload Handling

- Multiple file uploads using `request.FILES.getlist('images')`
- Client-side file validation and preview with JavaScript
- Server-side image validation using Pillow
- Proper error handling for invalid files

### OCR Integration

The application supports integration with your existing OCR modules:

- **Equation OCR**: Integrates with `Notebooks/latexocr.py`
- **Table OCR**: Integrates with `Notebooks/table_to_latex.py`
- **Fallback**: Uses mock LaTeX samples when OCR modules are unavailable

### Frontend Technologies

- **Bootstrap 5**: Responsive UI components and styling
- **Bootstrap Icons**: Icon set for UI elements
- **MathJax 3**: Real-time LaTeX rendering
- **JavaScript**: File handling, drag-and-drop, preview functionality

## Configuration

### Settings (MathScriber/settings.py)

```python
# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files configuration
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
```

### URL Configuration

- `/` - Image upload page
- `/results/` - View all processed results
- `/admin/` - Django admin interface
- `/media/` - Serve uploaded media files (development only)

## Customization

### Adding New OCR Modules

1. Create your OCR function in a separate module
2. Update `converter/ocr_utils.py` to import and use your module
3. Add new task choices to the model if needed

### Styling Customization

- Modify `static/css/style.css` for custom styling
- Update templates in `templates/converter/` for layout changes
- Customize Bootstrap theme by overriding CSS variables

### Database Customization

- Add new fields to the `UploadedImage` model
- Create and run migrations: `python manage.py makemigrations && python manage.py migrate`
- Update forms and templates accordingly

## Troubleshooting

### Common Issues

1. **File Upload Issues**: Check `MEDIA_ROOT` permissions and configuration
2. **Static Files Not Loading**: Run `python manage.py collectstatic` for production
3. **OCR Errors**: Ensure OCR dependencies are installed and configured
4. **Database Issues**: Delete `db.sqlite3` and re-run migrations for a fresh start

### Migration Issues

If you encounter migration problems:

```bash
python manage.py showmigrations
python manage.py migrate
```

## Development Notes

### Current OCR Implementation

- The application currently uses mock LaTeX samples for demonstration
- Real OCR integration is implemented but depends on your existing modules
- You can easily switch between mock and real OCR by modifying `ocr_utils.py`

### Production Considerations

- Configure proper static file serving (nginx/Apache)
- Use production database (PostgreSQL/MySQL)
- Set up proper media file handling
- Configure environment variables for sensitive settings
- Enable HTTPS and security middleware

## API for Integration

The application can be extended to provide REST API endpoints:

```python
# Future API endpoint examples
POST /api/upload/          # Upload images
GET  /api/results/         # Get all results
GET  /api/results/{id}/    # Get specific result
DELETE /api/results/{id}/  # Delete result
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the MathScriber OCR system for educational and research purposes.
