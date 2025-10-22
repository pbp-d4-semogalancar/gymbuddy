from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    CATEGORY_CHOICES = [
        # 🏃‍♂️ Individu
        ('atletik', 'Atletik'),
        ('renang', 'Renang'),
        ('bersepeda', 'Bersepeda'),
        ('panjat-tebing', 'Panjat Tebing'),
        ('golf', 'Golf'),
        ('tenis', 'Tenis'),
        ('badminton', 'Badminton'),
        ('panahan', 'Panahan'),
        ('bela-diri', 'Bela Diri'),

        # ⚽ Tim
        ('sepak-bola', 'Sepak Bola'),
        ('futsal', 'Futsal'),
        ('basket', 'Basket'),
        ('voli', 'Voli'),
        ('hoki', 'Hoki'),
        ('baseball', 'Baseball'),
        ('softball', 'Softball'),
        ('rugbi', 'Rugbi'),

        # 🧘 Kebugaran
        ('gym', 'Gym / Fitness'),

        # 🚵 Alam & Petualangan
        ('hiking', 'Hiking'),
        ('diving', 'Diving'),

        # ❄️ Musim Dingin
        ('ski', 'Ski'),
        ('snowboard', 'Snowboard'),
        ('ice-skating', 'Ice Skating'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    display_name = models.CharField(max_length=40, unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(blank=True, null=True)
    favorite_sports = models.CharField(max_length=255, blank=True, default='')
    

    def __str__(self):
        return self.display_name or self.user.username