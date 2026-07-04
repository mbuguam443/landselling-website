from django import forms
from .models import CompanySetting, PageContent


class CompanySettingForm(forms.ModelForm):
    class Meta:
        model = CompanySetting
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'input-field'}),
            'tagline': forms.TextInput(attrs={'class': 'input-field'}),
            'email': forms.EmailInput(attrs={'class': 'input-field'}),
            'phone': forms.TextInput(attrs={'class': 'input-field'}),
            'address': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'input-field'}),
            'favicon': forms.FileInput(attrs={'class': 'input-field'}),
            'google_maps_api_key': forms.TextInput(attrs={'class': 'input-field'}),
            'about_text': forms.Textarea(attrs={'class': 'input-field', 'rows': 5}),
            'mission_text': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'vision_text': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'social_facebook': forms.URLInput(attrs={'class': 'input-field'}),
            'social_twitter': forms.URLInput(attrs={'class': 'input-field'}),
            'social_instagram': forms.URLInput(attrs={'class': 'input-field'}),
            'social_linkedin': forms.URLInput(attrs={'class': 'input-field'}),
            'deposit_percentage_default': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'installment_months_default': forms.NumberInput(attrs={'class': 'input-field'}),
            'interest_rate_default': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'receipt_prefix': forms.TextInput(attrs={'class': 'input-field'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'input-field'}),
            'mpesa_callback_url': forms.URLInput(attrs={'class': 'input-field'}),
            'commission_percentage': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
        }


class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field'}),
            'content': forms.Textarea(attrs={'class': 'input-field', 'rows': 15}),
        }
