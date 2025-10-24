from django import forms
from .models import Target, Activity

tailwind_form_class = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-gray-900 focus:border-gray-900"

class TargetCreateForm(forms.ModelForm):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.all(),
        widget=forms.Select(attrs={'class': tailwind_form_class, 'id': 'select-exercise'})
    )
        
    class Meta:
        model = Target
        fields = ['activity', 'reps', 'planned_date']
        widgets = {
            'reps': forms.NumberInput(attrs={'class': tailwind_form_class}),
            'planned_date': forms.DateInput(attrs={'type': 'date', 'class': tailwind_form_class}),
        }

class LogUpdateForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ['description', 'time_spent']
        widgets = {
            'description': forms.Textarea(attrs={'class': tailwind_form_class, 'rows': 3}),
            'time_spent': forms.NumberInput(attrs={'class': tailwind_form_class}),
        }