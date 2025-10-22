from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.thread_list_view, name='thread_list'),
    path('create_ajax/', views.create_thread_ajax, name='create_thread_ajax'),
    path('thread/<int:thread_id>/', views.thread_detail_view, name='thread_detail'),
    path('thread/<int:thread_id>/edit/', views.edit_thread_ajax, name='edit_thread'),
    path('thread/<int:thread_id>/delete/', views.delete_thread_ajax, name='delete_thread'),
    path('thread/<int:thread_id>/add_reply/', views.add_reply_ajax, name='add_reply_ajax'),
    path('reply/<int:reply_id>/edit/', views.edit_reply_ajax, name='edit_reply'),
    path('reply/<int:reply_id>/delete/', views.delete_reply_ajax, name='delete_reply'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
]