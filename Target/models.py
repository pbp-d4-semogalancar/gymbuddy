from django.db import models
from django.contrib.auth.models import User

class Activity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    target_muscle = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.target_muscle})"

class Target(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    reps = models.PositiveIntegerField()
    planned_date = models.DateField(help_text="Tanggal rencana latihan")
    is_completed = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True, help_text="Catatan latihan")
    completed_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    time_spent = models.PositiveIntegerField(blank=True, null=True, help_text="Durasi (menit)")

    class Meta:
        ordering = ['-planned_date', 'is_completed']

    def __str__(self):
        status = "COMPLETED" if self.is_completed else "PLANNED"
        return f"{self.user.username} - {self.activity.name} ({status})"