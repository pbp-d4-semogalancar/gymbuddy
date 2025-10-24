from django.shortcuts import render, get_object_or_404
from .models import Exercise
from django.http import HttpResponse

def exercise_list(request):
    # Ambil semua data exercise
    exercises = Exercise.objects.all()

    # Filter muscle & equipment dari parameter GET
    selected_muscle = request.GET.get('muscle')
    selected_equipment = request.GET.get('equipment')

    if selected_muscle:
        exercises = exercises.filter(main_muscle=selected_muscle)
    if selected_equipment:
        exercises = exercises.filter(equipment=selected_equipment)

    # Ambil hanya nilai unik untuk dropdown
    muscles = Exercise.objects.values_list('main_muscle', flat=True).distinct().order_by('main_muscle')
    equipments = Exercise.objects.values_list('equipment', flat=True).distinct().order_by('equipment')

    return render(request, 'howto/exercise_list.html', {
        'exercises': exercises,
        'muscles': muscles,
        'equipments': equipments,
        'selected_muscle': selected_muscle,
        'selected_equipment': selected_equipment,
    })

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    return render(request, 'howto/exercise_detail.html', {'exercise': exercise})

