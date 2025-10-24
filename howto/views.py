from django.shortcuts import render
from .models import Exercise

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
