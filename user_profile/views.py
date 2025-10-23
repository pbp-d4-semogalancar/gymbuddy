from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from .forms import ProfileForm
from .models import Profile

@login_required
def create_profile(request):
    if hasattr(request.user, 'user_profile'):
        messages.warning(request, "Kamu sudah memiliki profil. Silakan ubah lewat menu Edit.")
        return redirect('user_profile:edit_profile')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profil berhasil dibuat!")
            return redirect('user_profile:detail_profile',
                            user_id=request.user.id, username=request.user.username)
    else:
        form = ProfileForm()

    context = {
        'form': form,
        'user_profile': profile
    }
    return render(request, 'create_user_profile.html', context)

@login_required
def edit_profile(request):
    if not hasattr(request.user, 'user_profile'):
        messages.warning(request, "Kamu belum memiliki profil. Silakan buat dulu.")
        return redirect('user_profile:create_profile')
    
    profile = request.user.user_profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil berhasil diperbarui!")
            return redirect('user_profile:detail_profile',
                            user_id=request.user.id, username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'user_profile': profile
    }
    return render(request, 'edit_user_profile.html', context)

@login_required
def detail_profile(request, user_id, username):
    user = get_object_or_404(User, id=user_id, username=username)

    if not hasattr(user, 'user_profile'):
        raise Http404("Profil belum dibuat.")

    profile = user.user_profile

    context = {
        'user_profile': profile,
        'title': f'Profil {profile.display_name}',
    }
    return render(request, 'show_user_profile.html', context)

@login_required
def delete_profile(request, user_id, username):
    profile = get_object_or_404(Profile, user__id=user_id, user__username=username)

    if request.user != profile.user:
        return HttpResponseForbidden("Kamu tidak boleh menghapus profil orang lain!")

    profile.delete()
    messages.success(request, "Profil berhasil dihapus.")
    return redirect('landing_page:landing_page')