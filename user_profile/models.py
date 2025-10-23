from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
import os
from django.utils.crypto import get_random_string

# Create your models here.

def profile_picture_upload_to(instance, filename):
    # Ambil ekstensi file
    ext = filename.split('.')[-1]
    
    # Buat nama file baru, misal pakai username + random string
    new_filename = f"{instance.user.username}_{get_random_string(6)}.{ext}"
    
    # Path folder upload di media root
    return os.path.join('images', new_filename)

class Profile(models.Model):
    CATEGORY_CHOICES = [
        # Latihan Beban / Strength
        ('bench-press', 'Bench Press (Dada)'),
        ('push-up', 'Push-up (Dada / Lengan)'),
        ('pull-up', 'Pull-up (Punggung / Lengan)'),
        ('deadlift', 'Deadlift (Punggung / Kaki)'),
        ('squat', 'Squat'),
        ('lunges', 'Lunges'),
        ('shoulder-press', 'Shoulder Press'),
        ('bicep-curl', 'Bicep Curl'),
        ('tricep-dips', 'Tricep Dips'),

        # Kardio
        ('running', 'Lari (Running)'),
        ('treadmill', 'Treadmill'),
        ('cycling', 'Bersepeda (Cycling)'),
        ('rowing', 'Rowing'),
        ('jump-rope', 'Lompat Tali (Jump Rope)'),

        # Fungsional & Kalistenik
        ('plank', 'Plank'),
        ('mountain-climber', 'Mountain Climber'),
        ('box-jump', 'Box Jump'),
        ('kettlebell-swing', 'Kettlebell Swing'),

        # Fleksibilitas & Kelas
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('stretching', 'Peregangan (Stretching)'),
        ('zumba', 'Zumba / Aerobik'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='user_profile', primary_key=True)
    display_name = models.CharField(max_length=40, unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=profile_picture_upload_to, blank=True, null=True)  
    favorite_workouts = MultiSelectField(choices=CATEGORY_CHOICES, blank=True)
    

    def __str__(self):
        return self.display_name or self.user.username