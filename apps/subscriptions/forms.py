from django import forms
from .models import SubscriptionPlan, SubscriptionPayment, Subscription


class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'plan_type': forms.Select(attrs={'class': 'input-field'}),
            'price': forms.NumberInput(attrs={'class': 'input-field'}),
            'commission_percentage': forms.NumberInput(attrs={'class': 'input-field'}),
            'duration_days': forms.NumberInput(attrs={'class': 'input-field'}),
        }


class SubscriptionPaymentForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPayment
        fields = ['user', 'subscription', 'amount', 'payment_method', 'transaction_ref', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'input-field'}),
            'subscription': forms.Select(attrs={'class': 'input-field'}),
            'amount': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'input-field'}),
            'transaction_ref': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'M-Pesa code, bank ref, etc.'}),
            'notes': forms.Textarea(attrs={'class': 'input-field', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subscription'].queryset = Subscription.objects.filter(is_active=True)
        self.fields['subscription'].empty_label = 'Select active subscription'
        self.fields['notes'].required = False
        self.fields['transaction_ref'].required = False
