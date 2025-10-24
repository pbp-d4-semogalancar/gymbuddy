from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_page_view, name='community_page'),
    path('create_ajax/', views.create_thread_ajax, name='create_thread_ajax'),
    path('thread/<int:thread_id>/', views.thread_detail_view, name='thread_detail'),
    path('create_ajax/', views.create_thread_ajax, name='create_thread_ajax'), # [C] AJAX
    path('edit/<int:thread_id>/', views.edit_thread_user, name='edit_thread_user'), # [U]
    path('delete/<int:thread_id>/', views.delete_thread_user, name='delete_thread_user'), # [D]
    path('thread/<int:thread_id>/reply/', views.add_reply_ajax, name='add_reply_ajax'),
    path('reply/<int:reply_id>/edit/', views.edit_reply_ajax, name='edit_reply'),
    path('reply/<int:reply_id>/delete/', views.delete_reply_ajax, name='delete_reply'),
]
