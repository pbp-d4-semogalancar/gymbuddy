from django.urls import path
from . import views

app_name = 'workoutlog' 

urlpatterns = [
    path('my-log/', views.gym_log_page, name='gym_log_page'),
    path('load-add-form/', views.load_add_target_form, name='load_add_target_form'),
    path('ajax/add-target/', views.ajax_add_target, name='ajax_add_target'),
    path('load-update-form/<int:target_id>/', views.load_update_log_form, name='load_update_log_form'),
    path('ajax/submit-log/<int:target_id>/', views.ajax_submit_log, name='ajax_submit_log'),
    path('ajax/filter-activities/', views.ajax_filter_activities, name='ajax_filter_activities'),
]