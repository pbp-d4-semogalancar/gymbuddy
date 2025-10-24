from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from .forms import ProfileForm
from .models import Profile

@login_required
def create_profile(request):
    if hasattr(request.user, 'user_profile'):
        return redirect('user_profile:detail_profile',
                        user_id=request.user.id, username=request.user.username)

    profile = None

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
@require_POST
def delete_profile(request, user_id, username):
    profile = get_object_or_404(Profile, user__id=user_id, user__username=username)

    if request.user != profile.user:
        return HttpResponseForbidden("Kamu tidak boleh menghapus profil orang lain!")

    profile.delete()
    messages.success(request, "Profil berhasil dihapus.")
    return redirect('landing_page:landing_page')

def show_json_by_id(request, user_id):
    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        raise Http404("Profile tidak ditemukan")

    data = {
        "id": profile.user.id,
        "username": profile.user.username,
        "display_name": profile.display_name,
        "bio": profile.bio,
        "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
        "favorite_workouts": profile.favorite_workouts,
    }
    return JsonResponse(data)

@login_required
@csrf_exempt
@require_POST
def create_profile_ajax(request):
    user = request.user

    if hasattr(user, 'user_profile'):
        return JsonResponse({"error": "Profile already exists."}, status=400)

    display_name = request.POST.get("display_name")
    bio = request.POST.get("bio", "")
    favorite_workouts = request.POST.getlist("favorite_workouts")
    profile_picture = request.FILES.get("profile_picture")

    new_profile = Profile(
        user=user,
        display_name=display_name,
        bio=bio,
        profile_picture=profile_picture,
        favorite_workouts=favorite_workouts
    )
    new_profile.save()

    return HttpResponse(b"CREATED", status=201)
    
@login_required
@require_POST
@csrf_exempt
def edit_profile_ajax(request):
    if not hasattr(request.user, 'user_profile'):
        return JsonResponse({"success": False, "message": "Profil belum dibuat."})

    profile = request.user.user_profile
    form = ProfileForm(request.POST, request.FILES, instance=profile)

    if form.is_valid():
        form.save()
        data = {
            "success": True,
            "message": "Profil berhasil diperbarui!",
            "profile": {
                "display_name": profile.display_name,
                "bio": profile.bio,
                "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
                "favorite_workouts": profile.favorite_workouts,
            }
        }
        return JsonResponse(data)
    else:
        errors = form.errors.as_json()
        return JsonResponse({"success": False, "errors": errors})