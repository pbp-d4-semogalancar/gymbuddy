from django.http import JsonResponse
from .models import Exercise
from .serializers import exercise_to_dict
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


def exercise_list_api(request):
    # awalnya: ambil semua
    exercises = Exercise.objects.all()

    muscle = request.GET.get("muscle")
    equipment = request.GET.get("equipment")

    if muscle:
        exercises = exercises.filter(main_muscle=muscle)
    if equipment:
        exercises = exercises.filter(equipment=equipment)

    data = [exercise_to_dict(ex) for ex in exercises]
    return JsonResponse(data, safe=False)



@csrf_exempt
def exercise_detail_api(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    data = exercise_to_dict(exercise)
    return JsonResponse(data, safe=False)

# API untuk daftar otot dan peralatan unik
def muscle_list_api(request):
    muscles = (
        Exercise.objects.values_list('main_muscle', flat=True)
        .distinct()
        .order_by('main_muscle')
    )
    return JsonResponse(list(muscles), safe=False)

def equipment_list_api(request):
    equipments = (
        Exercise.objects.values_list('equipment', flat=True)
        .distinct()
        .order_by('equipment')
    )
    return JsonResponse(list(equipments), safe=False)


def exercise_options_api(request):
    muscles = Exercise.objects.order_by("main_muscle") \
                .values_list("main_muscle", flat=True).distinct()

    equipments = Exercise.objects.order_by("equipment") \
                .values_list("equipment", flat=True).distinct()

    return JsonResponse({
        "muscles": list(muscles),
        "equipments": list(equipments),
    }, safe=False)
