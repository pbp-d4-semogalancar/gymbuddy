from django.db import models
from django.conf import settings
# Correctly import the Exercise model from the 'howto' app
from howto.models import Exercise 

class WorkoutPlan(models.Model):
    """
    Represents a specific exercise planned by a user,
    linking to an Exercise and adding sets and reps.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="workout_plans",
        help_text="The user who created this workout plan."
    )
    exercise = models.ForeignKey(
        Exercise, 
        on_delete=models.CASCADE,
        related_name="plans",
        help_text="The exercise chosen for this plan."
    )
    sets = models.PositiveIntegerField(
        help_text="Number of sets to perform."
    )
    reps = models.PositiveIntegerField(
        help_text="Number of repetitions per set."
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time this plan was created."
    )
    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.user.username}'s plan: {self.exercise.exercise_name} ({self.sets}x{self.reps})"
