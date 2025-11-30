from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    path('create/', views.create_profile, name='create_profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('<int:user_id>/<str:username>/', views.detail_profile, name='detail_profile'),
    path('<int:user_id>/<str:username>/delete/', views.delete_profile, name='delete_profile'),
    path('json/', views.show_json, name='show_json'),
    path('json/<int:user_id>/', views.show_json_by_id, name='show_json_by_id'),
    path('create/api/', views.create_profile_api, name='create_profile_api'),
    path('edit/api/', views.edit_profile_api, name='edit_profile_api'),
]