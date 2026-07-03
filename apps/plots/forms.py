from django import forms
from django.forms import inlineformset_factory
from .models import Plot, PlotImage


class PlotImageForm(forms.ModelForm):
    class Meta:
        model = PlotImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'input-field'}),
            'caption': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Optional caption'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'w-4 h-4'}),
        }


PlotImageFormSet = inlineformset_factory(Plot, PlotImage, form=PlotImageForm, extra=3, can_delete=True)


class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = '__all__'
        widgets = {
            'plot_number': forms.TextInput(attrs={'class': 'input-field'}),
            'project': forms.Select(attrs={'class': 'input-field'}),
            'phase': forms.Select(attrs={'class': 'input-field'}),
            'size_sqm': forms.NumberInput(attrs={'class': 'input-field'}),
            'price': forms.NumberInput(attrs={'class': 'input-field'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'input-field'}),
            'max_installment_months': forms.NumberInput(attrs={'class': 'input-field'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'input-field'}),
            'status': forms.Select(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
            'coordinates': forms.TextInput(attrs={'class': 'input-field'}),
            'amenities': forms.SelectMultiple(attrs={'class': 'input-field'}),
        }


class PlotFilterForm(forms.Form):
    project = forms.ChoiceField(choices=[], required=False, widget=forms.Select(attrs={'class': 'input-field'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Min Price'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Max Price'}))
    min_size = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Min Size'}))
    max_size = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Max Size'}))
    status = forms.ChoiceField(choices=[('', 'All Status')] + Plot.STATUS_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'input-field'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.projects.models import Project
        self.fields['project'].choices = [('', 'All Projects')] + [(p.id, p.name) for p in Project.objects.all()]
