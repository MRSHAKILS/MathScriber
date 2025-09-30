from django import forms
from .models import UploadedImage

class MultipleImageUploadForm(forms.Form):
    task = forms.ChoiceField(
        choices=UploadedImage.TASK_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'task-select'
        }),
        initial='equation',
        help_text='Choose the type of content to extract'
    )

class SingleImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image', 'task']
        widgets = {
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'task': forms.Select(attrs={
                'class': 'form-select'
            }),
        }