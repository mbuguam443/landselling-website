from django import forms
from .models import SubscriptionPlan


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
