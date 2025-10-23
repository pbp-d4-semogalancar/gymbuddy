from django.urls import path
from . import views

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
]
