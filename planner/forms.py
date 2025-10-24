from django import forms
from .models import WorkoutPlan

tailwind_textarea_class = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-gray-900 focus:border-gray-900 text-gray-900"

class LogCompletionForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': tailwind_textarea_class,
                'rows': 4,
                'placeholder': 'Masukkan catatan latihanmu (opsional)...'
            }),
        }