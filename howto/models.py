from django.db import models


class Exercise(models.Model):
    """
    Model untuk menyimpan data latihan dari dataset gym_exercises.csv
    """
    exercise_name = models.CharField(max_length=120)
    main_muscle = models.CharField(max_length=100)  # contoh: Chest, Back, Legs
    target_muscle = models.TextField(blank=True, null=True)  # contoh: Pectoralis Major
    synergist_muscle = models.TextField(blank=True, null=True)  # contoh: Triceps Brachii, Deltoid
    equipment = models.CharField(max_length=100, blank=True, null=True)  # contoh: Barbell, Dumbbell
    instructions = models.TextField(blank=True, null=True)  # gabungan preparation + execution
    image = models.ImageField(upload_to='howto/images/', blank=True, null=True)  # opsional, jika nanti ingin menampilkan gambar latihan
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.exercise_name

    class Meta:
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"
        ordering = ['main_muscle', 'exercise_name']
