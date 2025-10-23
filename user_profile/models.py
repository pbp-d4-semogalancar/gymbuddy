from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

# Create your models here.

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

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    display_name = models.CharField(max_length=40, unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='images/', blank=True, null=True)  
    favorite_workouts = MultiSelectField(choices=CATEGORY_CHOICES, blank=True)
    

    def __str__(self):
        return self.display_name or self.user.username