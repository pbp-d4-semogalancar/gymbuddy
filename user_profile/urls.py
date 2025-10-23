from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    path('create/', views.create_profile, name='create_profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('<int:user_id>/<str:username>/', views.detail_profile, name='detail_profile'),
]