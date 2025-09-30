from django.db import models

class UploadedImage(models.Model):
    TASK_CHOICES = [
        ('equation', 'Equation'),
        ('table', 'Table'),
    ]

    image = models.ImageField(upload_to='uploads/')
    task = models.CharField(max_length=10, choices=TASK_CHOICES)
    latex_output = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} - {self.image.name}"
