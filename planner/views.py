import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Make sure Exercise is imported
from howto.models import Exercise 
from .models import WorkoutPlan

class PlanCreatorView(LoginRequiredMixin, TemplateView):
    """
    This is our main view (Task 1).
    It just loads and displays the 'plan_list.html' template.
    The LoginRequiredMixin ensures only logged-in users can access it.
    """
    template_name = 'planner/plan_list.html'


class ExerciseSearchJSONView(LoginRequiredMixin, View):
    """
    This is our first AJAX endpoint (Live Search).
    Handles AJAX GET requests for searching exercises.
    Returns a JSON list of matching exercises.
    """
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        
        # Don't search if the query is too short
        if len(query) < 2:
            return JsonResponse({'exercises': []})
            
        try:
            # Get the first 10 matching exercise *objects*
            exercises = Exercise.objects.filter(
                exercise_name__icontains=query
            )[:10] 

            # Manually build the list of dictionaries. 
            # This is safer than using .values() if there is bad data.
            exercise_list = [
                {'id': ex.id, 'name': ex.exercise_name} 
                for ex in exercises
            ]
            
            data = {
                'exercises': exercise_list
            }
            
            # This should now succeed
            return JsonResponse(data)
            
        except Exception as e:
            # If ANY error happens during the query or serialization,
            # catch it and return a 500 error with the message.
            # Our new JavaScript will display this error.
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


class AddPlanAPIView(LoginRequiredMixin, View):
    """
    This is our second AJAX endpoint (Form Submission).
    
    It handles POST requests from our JavaScript "Add" button.
    It expects the data to be sent as a JSON string in the request body.
    
    It saves the new WorkoutPlan item and returns the created item as JSON.
    """
    def post(self, request, *args, **kwargs):
        # The frontend will send a JSON string. We need to parse it.
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        # Get the data from the parsed JSON
        exercise_id = data.get('exercise_id')
        sets = data.get('sets')
        reps = data.get('reps')

        # --- Validation ---
        if not all([exercise_id, sets, reps]):
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        try:
            # Check if the exercise actually exists
            exercise = Exercise.objects.get(id=exercise_id)
            # Ensure sets and reps are valid positive numbers
            sets = int(sets)
            reps = int(reps)
            if sets <= 0 or reps <= 0:
                raise ValueError("Sets and reps must be positive.")
        
        except Exercise.DoesNotExist:
            return JsonResponse({'error': 'Exercise not found.'}, status=404)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid data for sets or reps.'}, status=400)
        
        # --- Create the "Log" Item ---
        # If all validation passes, create the WorkoutPlan item
        # This is where we create the "log" for your teammates
        plan_item = WorkoutPlan.objects.create(
            user=request.user,  # Assign the item to the logged-in user
            exercise=exercise,
            sets=sets,
            reps=reps
        )

        # --- Send Success Response ---
        # Return a JSON object of the item we just created.
        # The frontend JavaScript will use this to add it to the page.
        # status=201 means "Created".
        return JsonResponse({
            'id': plan_item.id,
            'exercise_name': plan_item.exercise.exercise_name,
            'sets': plan_item.sets,
            'reps': plan_item.reps,
        }, status=201)

