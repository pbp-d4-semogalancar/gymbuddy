from django.db import models
from django.conf import settings

class Exercise(models.Model):
    exercise_name = models.CharField(max_length=120)
    main_muscle = models.CharField(max_length=100)
    equipment = models.CharField(max_length=100, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='howto/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.exercise_name

    class Meta:
        ordering = ['main_muscle', 'exercise_name']


class ExerciseFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "exercise")
