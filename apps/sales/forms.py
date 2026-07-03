from django import forms
from .models import Sale, Reservation


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'plot', 'selling_price', 'deposit_amount', 'installment_months',
                  'interest_rate', 'grace_period_days', 'penalty_rate', 'notes', 'status']
        widgets = {
            'customer': forms.Select(attrs={'class': 'input-field'}),
            'plot': forms.Select(attrs={'class': 'input-field'}),
            'selling_price': forms.NumberInput(attrs={'class': 'input-field'}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'input-field'}),
            'installment_months': forms.NumberInput(attrs={'class': 'input-field'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'input-field'}),
            'grace_period_days': forms.NumberInput(attrs={'class': 'input-field'}),
            'penalty_rate': forms.NumberInput(attrs={'class': 'input-field'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'input-field'}),
        }


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['customer', 'plot', 'expiry_date', 'amount', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'input-field'}),
            'plot': forms.Select(attrs={'class': 'input-field'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'input-field', 'type': 'datetime-local'}),
            'amount': forms.NumberInput(attrs={'class': 'input-field'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_staff_or_above():
            from apps.customers.models import Customer
            self.fields['customer'].queryset = Customer.objects.filter(user=self.user)
            self.fields['customer'].empty_label = None
            self.fields['expiry_date'].required = False
            self.fields['expiry_date'].widget = forms.HiddenInput()
            self.fields['amount'].required = False
            self.fields['amount'].widget = forms.HiddenInput()
