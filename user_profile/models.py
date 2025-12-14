from django.db import models
from django.contrib.auth.models import User
from howto.models import Exercise

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='user_profile', primary_key=True)
    display_name = models.CharField(max_length=40, unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(blank=True,null=True)
    favorite_workouts = models.ManyToManyField(Exercise, blank=True)

    def __str__(self):
        return self.display_name or self.user.username
    
    def profile_picture_upload_to(instance, filename):
        return f"profile_pictures/{filename}"