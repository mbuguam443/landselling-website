from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['customer', 'sale', 'document_type', 'title', 'file', 'description']
        widgets = {
            'customer': forms.Select(attrs={'class': 'input-field'}),
            'sale': forms.Select(attrs={'class': 'input-field'}),
            'document_type': forms.Select(attrs={'class': 'input-field'}),
            'title': forms.TextInput(attrs={'class': 'input-field'}),
            'file': forms.FileInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }
