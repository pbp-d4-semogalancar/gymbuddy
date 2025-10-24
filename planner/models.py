from django.db import models
from django.conf import settings
from howto.models import Exercise 
import datetime 

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
    
    plan_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        # Updated __str__ to be more descriptive!
        return f"{self.user.username} - {self.exercise.exercise_name} ({self.sets} sets x {self.reps} reps) on {self.plan_date}"

    class Meta:
        ordering = ['plan_date', 'id']


