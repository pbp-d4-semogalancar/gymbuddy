from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
import os
from django.utils.crypto import get_random_string
from howto.models import Exercise

# Create your models here.

def profile_picture_upload_to(instance, filename):
    # Ambil ekstensi file
    ext = filename.split('.')[-1]
    
    # Buat nama file baru, pakai username + random string
    new_filename = f"{instance.user.username}_{get_random_string(6)}.{ext}"
    
    # Path folder upload di media root
    return os.path.join('images', new_filename)

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='user_profile', primary_key=True)
    display_name = models.CharField(max_length=40, unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=profile_picture_upload_to, blank=True, null=True)  
    favorite_workouts = models.ManyToManyField(Exercise, blank=True)

    def __str__(self):
        return self.display_name or self.user.username