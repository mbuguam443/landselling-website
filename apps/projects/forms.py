from django import forms
from django.forms import inlineformset_factory
from .models import Project, ProjectPhase, ProjectImage


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'input-field'}),
            'coordinates': forms.TextInput(attrs={'class': 'input-field'}),
            'total_plots': forms.NumberInput(attrs={'class': 'input-field'}),
            'image': forms.FileInput(attrs={'class': 'input-field'}),
            'status': forms.Select(attrs={'class': 'input-field'}),
            'start_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
        }


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'input-field'}),
            'caption': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Optional caption'}),
        }


ProjectImageFormSet = inlineformset_factory(Project, ProjectImage, form=ProjectImageForm, extra=3, can_delete=True)


class ProjectPhaseForm(forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'input-field'}),
            'total_plots': forms.NumberInput(attrs={'class': 'input-field'}),
        }
