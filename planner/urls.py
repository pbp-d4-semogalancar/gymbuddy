from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.PlanCreatorView.as_view(),name='plan_creator'),

    path('search-exercises/', views.ExerciseSearchJSONView.as_view(), name='search_exercises'),

    path('api/add-plan/', views.AddPlanAPIView.as_view(), name='api_add_plan'
    ),
]

