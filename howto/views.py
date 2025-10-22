from django.shortcuts import render
from .models import Exercise

def exercise_list(request):
    # Ambil parameter filter (misalnya ?muscle=Chest)
    muscle_filter = request.GET.get('muscle')
    equipment_filter = request.GET.get('equipment')

    # Ambil semua data latihan
    exercises = Exercise.objects.all()

    # Terapkan filter jika ada
    if muscle_filter:
        exercises = exercises.filter(main_muscle__icontains=muscle_filter)
    if equipment_filter:
        exercises = exercises.filter(equipment__icontains=equipment_filter)

    # buat jadi unik terhadap nama 
    unique_exercises = {}
    for ex in exercises:
        if ex.exercise_name not in unique_exercises:
            unique_exercises[ex.exercise_name] = ex

    exercises = unique_exercises.values()


    # Ambil daftar otot dan alat unik
    muscles = Exercise.objects.values_list('main_muscle', flat=True).distinct()
    equipments = Exercise.objects.values_list('equipment', flat=True).distinct()

    return render(request, 'howto/exercise_list.html', {
        'exercises': exercises,
        'muscles': muscles,
        'equipments': equipments,
        'selected_muscle': muscle_filter,
        'selected_equipment': equipment_filter,
    })

