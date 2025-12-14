from django.urls import path
from . import views

app_name = 'howto'

urlpatterns = [
    path('', views.exercise_list, name='exercise_list'),
    path('detail/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('api/list/', views.exercise_list_api, name='exercise_list_api'),
    path('api/detail/<int:pk>/', views.exercise_detail_api, name='exercise_detail_api'),
    path('api/muscles/', views.muscle_list_api, name='muscle_list_api'),
    path('api/equipments/', views.equipment_list_api, name='equipment_list_api'),
    path("api/options/", views.exercise_options_api, name="exercise_options_api"),

    path("api/favorites/", views.favorite_ids_api, name="favorite_ids_api"),
    path("api/favorites/toggle/<int:pk>/", views.toggle_favorite_api, name="toggle_favorite_api"),

]
