from django import forms
from .models import Document
from django.core.exceptions import ValidationError
import mimetypes
import os

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'pdf_file', 'mfo', 'message']

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError('Пожалуйста, загрузите файл с расширением .pdf.')

            mime_type, _ = mimetypes.guess_type(pdf.name)
            if mime_type != 'application/pdf':
                raise ValidationError('Загруженный файл не является PDF.')
        else:
            raise ValidationError('Это поле обязательно для заполнения.')
        return pdf