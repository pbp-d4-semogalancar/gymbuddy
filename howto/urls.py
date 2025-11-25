from django.urls import path
from . import views

app_name = 'howto'

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('detail/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('api/list/', views.exercise_list_api, name='exercise_list_api'),
    path('api/detail/<int:pk>/', views.exercise_detail_api, name='exercise_detail_api'),
]
