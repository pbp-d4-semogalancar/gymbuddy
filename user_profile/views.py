from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm
from .models import Profile

# Create your views here.

@login_required()
def create_profile(request):
    if hasattr(request.user, 'profile'):
        messages.warning(request, "Kamu sudah memiliki profil. Silakan ubah lewat menu Edit.")
        return redirect('profile:edit_profile')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profil berhasil dibuat!")
            return redirect('profile:detail_profile')
    else:
        form = ProfileForm()

    context = {
        'form': form,
        'title': 'Buat Profil Baru',
        'button_label': 'Buat Profil'
    }
    return render(request, 'profile_form.html', context)

@login_required()
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil berhasil diperbarui!")
            return redirect('profile:detail_profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'title': 'Edit Profil',
        'button_label': 'Simpan Perubahan'
    }
    return render(request, 'profile_form.html', context)