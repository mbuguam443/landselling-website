from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['sale', 'customer', 'amount', 'payment_method', 'transaction_code',
                  'bank_name', 'cheque_number', 'mpesa_code', 'mpesa_phone', 'payment_date', 'notes']
        widgets = {
            'sale': forms.Select(attrs={'class': 'input-field'}),
            'customer': forms.Select(attrs={'class': 'input-field'}),
            'amount': forms.NumberInput(attrs={'class': 'input-field'}),
            'payment_method': forms.Select(attrs={'class': 'input-field'}),
            'transaction_code': forms.TextInput(attrs={'class': 'input-field'}),
            'bank_name': forms.TextInput(attrs={'class': 'input-field'}),
            'cheque_number': forms.TextInput(attrs={'class': 'input-field'}),
            'mpesa_code': forms.TextInput(attrs={'class': 'input-field'}),
            'mpesa_phone': forms.TextInput(attrs={'class': 'input-field'}),
            'payment_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }
