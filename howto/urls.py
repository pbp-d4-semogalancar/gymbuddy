from django.urls import path
from . import views

app_name = 'howto'

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('detail/<int:pk>/', views.exercise_detail, name='exercise_detail'),
]
