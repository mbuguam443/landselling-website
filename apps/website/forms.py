from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'input-field', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'input-field'}),
            'subject': forms.TextInput(attrs={'class': 'input-field', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'input-field', 'rows': 5, 'required': True}),
        }
