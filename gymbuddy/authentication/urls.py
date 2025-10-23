from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    # ==== WEB (render HTML biasa) ====
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('register/', register_user, name='register_user'),

    # ==== AJAX/API (JSON response) ====
    path('api/login/', login_user_ajax, name='login_api'),
    path('api/logout/', logout_user_ajax, name='logout_api'),
    path('api/register/', register_user_ajax, name='register_api'),
]