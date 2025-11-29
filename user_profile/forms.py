from django import forms
from .models import Profile
from howto.models import Exercise

class ProfileForm(forms.ModelForm):

    favorite_workouts = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Profile
        fields = [
            'display_name',
            'bio',
            'profile_picture',
            'favorite_workouts',
        ]

        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 focus:border-gray-800',
                'placeholder': 'Masukkan display name kamu...',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 resize-none h-64 focus:border-gray-800',
                'placeholder': 'Tulis bio kamu...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tampilkan label = exercise_name, value = ID
        self.fields['favorite_workouts'].label_from_instance = lambda obj: obj.exercise_name