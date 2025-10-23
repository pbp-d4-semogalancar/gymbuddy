from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views  

from django.contrib.auth.views import LogoutView, LoginView


app_name = 'community'

urlpatterns = [
    # --- SISI USER URLS (Public) ---
    path('', views.show_community, name='show_community'), 
    
    # CRUD User
    path('create_ajax/', views.create_thread_ajax, name='create_thread_ajax'), # [C] AJAX
    path('edit/<int:thread_id>/', views.edit_thread_user, name='edit_thread_user'), # [U]
    path('delete/<int:thread_id>/', views.delete_thread_user, name='delete_thread_user'), # [D]
    
    # Login / Logout (pakai halaman custom login)
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Logout redirect ke login page
    path('logout/', LogoutView.as_view(next_page='/community/login/'), name='logout'),

    # Signup
    path('signup/', views.SignUpView.as_view(template_name='registration/signup.html'), name='signup'),
]
