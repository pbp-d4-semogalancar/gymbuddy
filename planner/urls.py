from django.urls import path
from . import views


app_name = 'planner'

urlpatterns = [
    path('', views.PlanCreatorView.as_view(),name='plan_creator'),
    path('search-exercises/', views.ExerciseSearchJSONView.as_view(), name='search_exercises'),
    path('api/add-plan/', views.AddPlanAPIView.as_view(), name='api_add_plan'),
    path('api/get-plans-for-date/', views.GetPlansForDateAPIView.as_view(), name='get_plans_for_date'),
    path('log/load-form/<int:plan_id>/', views.load_completion_form, name='load_completion_form'),
    path('log/complete/<int:plan_id>/', views.ajax_complete_log, name='ajax_complete_log'),
    path('api/get-logs/', views.get_workout_logs_api, name='api_get_logs'),
    path('api/log/complete/<int:plan_id>/', views.api_complete_log, name='api_complete_log'),
]

