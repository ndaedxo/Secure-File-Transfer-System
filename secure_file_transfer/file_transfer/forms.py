# secure_file_transfer\file_transfer\forms.py
from django import forms
from .models import FileTransfer

class FileUploadForm(forms.ModelForm):
    """
    Form for file uploads with additional validation
    """
    class Meta:
        model = FileTransfer
        fields = ['file']
    
    def clean_file(self):
        """
        Add custom file validation
        """
        file = self.cleaned_data.get('file')
        
        # Maximum file size (10MB)
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 10MB")
        
        return file