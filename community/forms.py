# community/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Thread

# ====================================================================
# 1. THREAD FORM (Untuk membuat dan mengedit diskusi)
# ====================================================================
class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content'] 
        
        # Penambahan widget untuk styling dan placeholder
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Judul Thread Anda (Max 255 karakter)',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tulis isi diskusi di sini...',
                'rows': 4,
            }),
        }

# ====================================================================
# 2. CUSTOM USER CREATION FORM (Untuk Registrasi/Signup)
# ====================================================================
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # FIX: Hanya meminta 'username'. Password ditangani otomatis.
        fields = ('username',)