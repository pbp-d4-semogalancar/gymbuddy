"""
URL configuration for gymbuddy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# gymbuddy/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView 
from community.views import SignUpView 

urlpatterns = [
    # Redirect root (/) ke /community/
    path('', RedirectView.as_view(url='community/', permanent=True)), 
    
    path('admin/', admin.site.urls),

    # Community app URLs
    path('community/', include('community.urls')), 

    # Signup di root supaya {% url 'signup' %} ditemukan
    path('accounts/signup/', SignUpView.as_view(), name='signup'),

    # Login / Logout custom (pakai template login.html)
    path('accounts/', include('django.contrib.auth.urls')), 
]

