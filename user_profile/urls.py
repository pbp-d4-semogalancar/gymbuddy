from django.urls import path
from . import views

urlpatterns = [
    path('profile/create/', views.create_profile, name='create_profile'),
]