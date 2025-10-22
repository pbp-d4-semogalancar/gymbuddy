from django.shortcuts import render
import json
from django.shortcuts import render, redirect
from .models import Profile, SportTag
from .forms import ProfileForm

# Create your views here.

def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # pastikan user login

            # ambil data tag dari Tagify
            raw_data = request.POST.get('favorite_sports', '[]')
            try:
                tags_data = json.loads(raw_data)
            except json.JSONDecodeError:
                tags_data = []

            # simpan profile dulu
            profile.save()

            # proses tag
            tags = []
            for tag in tags_data:
                name = tag.get('value') if isinstance(tag, dict) else str(tag)
                if name:
                    sport_tag, _ = SportTag.objects.get_or_create(name=name)
                    tags.append(sport_tag)

            profile.favorite_sports.set(tags)
            return redirect('profile_detail', username=profile.user.username)
    else:
        form = ProfileForm()

    all_tags = list(SportTag.objects.values_list('name', flat=True))
    return render(request, 'create_profile.html', {'form': form, 'tags': all_tags})