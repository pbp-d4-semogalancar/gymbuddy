from django.urls import path
from . import views
from .views import ThreadListCreateAPIView, api_thread_detail, api_add_reply, api_delete_reply, api_edit_reply
app_name = 'community'

urlpatterns = [
    path('api/threads/', ThreadListCreateAPIView.as_view(), name='api_thread_list_create'),
    path('api/thread/<int:id>/', api_thread_detail, name='api_thread_detail'),
    path('api/thread/<int:thread_id>/add_reply/', api_add_reply, name='api_add_reply'),
    path('api/reply/<int:reply_id>/delete/', api_delete_reply, name='api_delete_reply'),
    path('api/reply/<int:reply_id>/edit/', api_edit_reply, name='api_edit_reply'),
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
