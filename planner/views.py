import json
import datetime
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

# Import your models
from howto.models import Exercise
from .models import WorkoutPlan

class PlanCreatorView(LoginRequiredMixin, TemplateView):
    """
    Renders the main planner page ('create_plan.html').
    """
    # We renamed this file to 'create_plan.html' to fix the cache bug
    template_name = 'planner/create_plan.html'

class ExerciseSearchJSONView(LoginRequiredMixin, View):
    """
    Responds to AJAX GET requests to search for exercises.
    Called by the 'Cari Latihan' search bar.
    URL: /planner/search-exercises/
    """
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        # We check for a query length again just to be safe
        if len(query) < 2:
            return JsonResponse({'exercises': []}, status=400)
            
        try:
            # Find exercises matching the query
            # We limit to 10 results for performance
            matching_exercises = Exercise.objects.filter(
                exercise_name__icontains=query
            )[:10]
            
            # Manually build the list to avoid serialization errors
            # This is safer than using .values()
            exercises_list = []
            for exercise in matching_exercises:
                exercises_list.append({
                    'id': exercise.id,
                    'name': exercise.exercise_name
                })
            
            return JsonResponse({'exercises': exercises_list})
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error in ExerciseSearchJSONView: {e}") 
            return JsonResponse({'error': 'Failed to search exercises.'}, status=500)

class AddPlanAPIView(LoginRequiredMixin, View):
    """
    Responds to AJAX POST requests to add a new workout item.
    Called by the 'Tambahkan ke Rencana' button.
    URL: /planner/api/add-plan/
    """
    def post(self, request, *args, **kwargs):
        try:
            # Load data from the request body
            data = json.loads(request.body)
            exercise_id = data.get('exercise_id')
            sets = data.get('sets')
            reps = data.get('reps')
            plan_date_str = data.get('plan_date') # e.g., "2025-10-24"

            # --- Validation ---
            if not all([exercise_id, sets, reps, plan_date_str]):
                return JsonResponse({'error': 'Data tidak lengkap.'}, status=400)
            
            # Check if exercise exists
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                return JsonResponse({'error': 'Latihan tidak ditemukan.'}, status=404)
            
            # Check for valid numbers
            if not (isinstance(sets, int) and sets > 0 and isinstance(reps, int) and reps > 0):
                 return JsonResponse({'error': 'Sets dan Reps harus angka positif.'}, status=400)
            
            # Check for valid date format
            try:
                plan_date = datetime.date.fromisoformat(plan_date_str)
            except ValueError:
                return JsonResponse({'error': 'Format tanggal tidak valid.'}, status=400)
            
            # --- Create and Save the Object ---
            plan_item = WorkoutPlan.objects.create(
                user=request.user,
                exercise=exercise,
                sets=sets,
                reps=reps,
                plan_date=plan_date
            )
            
            # --- Return the created object as JSON ---
            # This is what the JavaScript uses to update the list
            return JsonResponse({
                'id': plan_item.id,
                'exercise_name': plan_item.exercise.exercise_name,
                'sets': plan_item.sets,
                'reps': plan_item.reps
            }, status=201) # 201 = Created

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(f"Error in AddPlanAPIView: {e}")
            return JsonResponse({'error': 'Terjadi kesalahan di server.'}, status=500)


class GetPlansForDateAPIView(LoginRequiredMixin, View):
    """
    Responds to AJAX GET requests to fetch all plan items for a specific date.
    Called when the page loads and when the date picker changes.
    URL: /planner/api/get-plans-for-date/
    """
    def get(self, request, *args, **kwargs):
        date_str = request.GET.get('date', None)
        
        if not date_str:
            return JsonResponse({'error': 'Tanggal tidak diberikan.'}, status=400)
            
        try:
            plan_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return JsonResponse({'error': 'Format tanggal tidak valid.'}, status=400)
            
        try:
            # Find all plans for the logged-in user for that date
            plans = WorkoutPlan.objects.filter(
                user=request.user, 
                plan_date=plan_date
            )
            
            # Build the list of plans
            plans_list = []
            for plan_item in plans:
                plans_list.append({
                    'id': plan_item.id,
                    'exercise_name': plan_item.exercise.exercise_name,
                    # This was the bug fix! It was 'plan.reps' before.
                    'sets': plan_item.sets,
                    'reps': plan_item.reps 
                })
                
            return JsonResponse({'plans': plans_list})
            
        except Exception as e:
            print(f"Error in GetPlansForDateAPIView: {e}")
            return JsonResponse({'error': 'Gagal mengambil data rencana.'}, status=500)
        
class WorkoutLogView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/workout_log.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all plans for the logged-in user, newest first
        all_plans = WorkoutPlan.objects.filter(user=self.request.user).order_by('-plan_date')
        
        # Group the plans by date for the template
        # We'll create a dictionary like: {'2025-10-24': [plan1, plan2], '2025-10-23': [plan3]}
        grouped_plans = {}
        for plan in all_plans:
            # .isoformat() gives "YYYY-MM-DD"
            date_str = plan.plan_date.isoformat()
            
            if date_str not in grouped_plans:
                # If this is the first time we see this date, create an entry
                grouped_plans[date_str] = {
                    'date_obj': plan.plan_date, # Store the date object for formatting
                    'plans': [] # Start an empty list for its plans
                }
            
            # Add the current plan to its date's list
            grouped_plans[date_str]['plans'].append(plan)
            
        context['grouped_plans'] = grouped_plans
        return context



