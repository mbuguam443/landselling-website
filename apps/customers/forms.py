from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['user']
        widgets = {
            'national_id': forms.TextInput(attrs={'class': 'input-field'}),
            'phone': forms.TextInput(attrs={'class': 'input-field'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'address': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'input-field'}),
            'postal_code': forms.TextInput(attrs={'class': 'input-field'}),
            'passport_photo': forms.FileInput(attrs={'class': 'input-field'}),
            'id_front': forms.FileInput(attrs={'class': 'input-field'}),
            'id_back': forms.FileInput(attrs={'class': 'input-field'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'input-field'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'input-field'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'national_id', 'phone', 'alternate_phone', 'address', 'city',
            'postal_code', 'passport_photo', 'id_front', 'id_back',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation',
        ]
        widgets = {
            'national_id': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'National ID number'}),
            'phone': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Phone number'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Alternate phone'}),
            'address': forms.Textarea(attrs={'class': 'input-field', 'rows': 2, 'placeholder': 'Physical address'}),
            'city': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Postal code'}),
            'passport_photo': forms.FileInput(attrs={'class': 'input-field'}),
            'id_front': forms.FileInput(attrs={'class': 'input-field'}),
            'id_back': forms.FileInput(attrs={'class': 'input-field'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Emergency contact name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Emergency contact phone'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Relation'}),
        }
