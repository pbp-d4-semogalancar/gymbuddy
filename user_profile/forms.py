from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name',
            'bio',
            'profile_picture',
            'favorite_workouts'
        ]
        # Buat tampilan di forms
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:border-gray-800 focus:ring focus:ring-gray-700 focus:outline-none',
                'placeholder': 'Masukkan display name kamu...',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 resize-none h-64 focus:border-gray-800 focus:ring focus:ring-gray-700 focus:outline-none',
                'placeholder': 'Tulis bio kamu...',
            }),
        }