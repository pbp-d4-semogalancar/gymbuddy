from django.urls import path
from . import views

app_name = 'landing_page'

urlpatterns = [
    path('', views.landing_page_view, name='landing_page'),
    path('how-to/', views.how_to_view, name='how_to'),
]