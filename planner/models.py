from django.db import models
from django.conf import settings
from howto.models import Exercise
import datetime
from django.utils import timezone 

class WorkoutPlan(models.Model):
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
    description = models.TextField(
        blank=True, null=True, 
        help_text="Catatan atau deskripsi setelah latihan diselesaikan."
    )
    is_completed = models.BooleanField(
        default=False, 
        help_text="Apakah rencana latihan ini sudah diselesaikan?"
    )
    completed_at = models.DateTimeField(
        blank=True, null=True, 
        help_text="Waktu ketika latihan ditandai selesai."
    )

    def __str__(self):
        status = "COMPLETED" if self.is_completed else "PLANNED"
        return f"{self.user.username} - {self.exercise.exercise_name} ({self.sets} sets x {self.reps} reps) on {self.plan_date} [{status}]"

    class Meta:
        ordering = ['-plan_date', 'is_completed', 'id']