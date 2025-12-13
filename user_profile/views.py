import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
import requests
from .forms import ProfileForm
from .models import Profile
from django.views.decorators.csrf import csrf_exempt


@login_required
def create_profile(request):
    if hasattr(request.user, 'user_profile'):
        return redirect('user_profile:detail_profile',
                        user_id=request.user.id, username=request.user.username)

    profile = None

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()  
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
        form = ProfileForm(request.POST, instance=profile)
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
    form = ProfileForm()
    workout_ids = list(profile.favorite_workouts.values_list('id', flat=True))

    context = {
        'user_profile': profile,
        'title': f'Profil {profile.display_name}',
        'form': form,
        'workout_ids': workout_ids
    }
    return render(request, 'show_user_profile.html', context)

@login_required
@require_http_methods(["DELETE", "POST"])
def delete_profile(request, user_id, username):
    profile = get_object_or_404(Profile, user__id=user_id, user__username=username)

    if request.user != profile.user:
        return JsonResponse({
            "success": False, 
            "message": "Kamu tidak bisa menghapus profil orang lain!"
        }, status=403)

    user = profile.user
    user.delete()

    return JsonResponse({
        "success": True, 
        "message": "Profil berhasil dihapus."
    }, status=200)

def show_json(request):
    try:
        profile_list = Profile.objects.all()
    except Profile.DoesNotExist:
        raise Http404("Profile tidak ditemukan")

    data = [ 
        {
            "id": profile.user.id,
            "username": profile.user.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "profile_picture": profile.profile_picture if profile.profile_picture else None,
            "favorite_workouts": list(profile.favorite_workouts.values("id", "exercise_name")),
        }
        for profile in profile_list
    ]
    return JsonResponse(data, safe=False)


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
        "profile_picture": profile.profile_picture if profile.profile_picture else None,
        "favorite_workouts": list(profile.favorite_workouts.values("id", "exercise_name")),
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
@require_POST
def create_profile_api(request):
    if hasattr(request.user, 'user_profile'):
        return JsonResponse({"success": False, "error": "Profile already exists"}, status=400)

    display_name = request.POST.get("display_name")
    bio = request.POST.get("bio", "")
    profile_picture = request.POST.get("profile_picture")

    try:
        workout_ids = json.loads(request.POST.get("favorite_workouts", "[]"))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid workout data"}, status=400)

    if not display_name:
        return JsonResponse({"success": False, "error": "Display name is required"}, status=400)

    profile = Profile.objects.create(
        user=request.user,
        display_name=display_name,
        bio=bio,
        profile_picture=profile_picture
    )

    profile.favorite_workouts.set(workout_ids)

    return JsonResponse({"success": True}, status=201)

    
@csrf_exempt
@login_required
@require_POST
def edit_profile_api(request):
    if not hasattr(request.user, 'user_profile'):
        return JsonResponse({"success": False, "error": "Profile belum dibuat"}, status=400)

    profile = request.user.user_profile

    display_name = request.POST.get("display_name")
    bio = request.POST.get("bio", "")
    profile_picture = request.POST.get("profile_picture")

    try:
        workout_ids = json.loads(request.POST.get("favorite_workouts", "[]"))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid workout data"}, status=400)

    if not display_name:
        return JsonResponse({"success": False, "error": "Display name is required"}, status=400)

    profile.display_name = display_name
    profile.bio = bio
    profile.profile_picture = profile_picture
    profile.save()

    profile.favorite_workouts.set(workout_ids)

    return JsonResponse({
        "success": True,
        "profile": {
            "display_name": profile.display_name,
            "bio": profile.bio,
            "profile_picture": profile.profile_picture,
            "favorite_workouts": list(
                profile.favorite_workouts.values("id", "exercise_name")
            )
        }
    })


def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)