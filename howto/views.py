from django.http import JsonResponse
from .models import Exercise, ExerciseFavorite
from .serializers import exercise_to_dict
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import re
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST



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






ZERO_WIDTH = r"[\u200B-\u200D\uFEFF]"

def _clean_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(ZERO_WIDTH, "", s)          # buang zero-width chars
    s = re.sub(r"\s+", " ", s).strip()     # rapihin spasi
    return s

def _equipment_category(raw: str) -> str:
    s = _clean_text(raw)
    low = s.lower()

    # urutan penting (Self-Assisted jangan ketangkep Assisted)
    if low.startswith("self-assisted"):
        return "Self-Assisted"
    if low.startswith("assisted"):
        return "Assisted"
    if low.startswith("band"):
        return "Band"
    if low.startswith("body"):
        return "Body Weight"
    if low.startswith("cable"):
        return "Cable"
    if low.startswith("barbell"):
        return "Barbell"
    if low.startswith("dumbbell"):
        return "Dumbbell"
    if low.startswith("lever"):
        return "Lever"
    if low.startswith("sled"):
        return "Sled"
    if low.startswith("smith"):
        return "Smith"
    if low.startswith("plyometric"):
        return "Plyometric"
    if low.startswith("isometric"):
        return "Isometric"
    if low.startswith("suspension") or low.startswith("suspended"):
        return "Suspension"
    if low.startswith("weighted"):
        return "Weighted"

    # fallback: kembalikan versi yang sudah dibersihin
    return s

def _apply_equipment_filter(qs, equipment_param: str):
    cat = _equipment_category(equipment_param)

    # Group filter ke semua varian di DB
    if cat == "Assisted":
        # Assisted* tapi bukan Self-Assisted*
        return qs.filter(equipment__istartswith="Assisted").exclude(equipment__istartswith="Self-Assisted")
    if cat == "Self-Assisted":
        return qs.filter(equipment__istartswith="Self-Assisted")
    if cat == "Band":
        return qs.filter(equipment__icontains="Band")
    if cat == "Body Weight":
        return qs.filter(Q(equipment__icontains="Body") | Q(equipment__icontains="Body Weight"))
    if cat == "Cable":
        return qs.filter(equipment__icontains="Cable")
    if cat == "Lever":
        return qs.filter(equipment__icontains="Lever")
    if cat == "Sled":
        return qs.filter(equipment__icontains="Sled")
    if cat == "Smith":
        return qs.filter(equipment__icontains="Smith")
    if cat == "Suspension":
        return qs.filter(Q(equipment__icontains="Suspension") | Q(equipment__icontains="Suspended"))
    if cat in {"Barbell", "Dumbbell", "Plyometric", "Isometric", "Weighted"}:
        return qs.filter(equipment__icontains=cat)

    # kalau user kirim value spesifik, coba exact match juga
    return qs.filter(equipment__iexact=_clean_text(equipment_param))

@require_GET
def exercise_options_api(request):
    muscles_raw = Exercise.objects.values_list("main_muscle", flat=True).distinct()
    equipments_raw = Exercise.objects.values_list("equipment", flat=True).distinct()

    muscles = sorted({ _clean_text(m) for m in muscles_raw if m })
    equipment_categories = sorted({ _equipment_category(e) for e in equipments_raw if e })

    return JsonResponse({
        "muscles": muscles,
        "equipments": equipment_categories,  # << unik (kategori)
    })

@require_GET
def exercise_list_api(request):
    qs = Exercise.objects.all()

    muscle = request.GET.get("muscle")
    equipment = request.GET.get("equipment")

    if muscle:
        qs = qs.filter(main_muscle=_clean_text(muscle))

    if equipment:
        qs = _apply_equipment_filter(qs, equipment)

    data = [exercise_to_dict(ex) for ex in qs]
    return JsonResponse(data, safe=False)

@csrf_exempt
def exercise_detail_api(request, pk):
    ex = get_object_or_404(Exercise, pk=pk)
    return JsonResponse(exercise_to_dict(ex), safe=False)


@require_GET
def favorite_ids_api(request):
    # PENTING: jangan pakai @login_required (itu redirect HTML)
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    ids = list(
        ExerciseFavorite.objects.filter(user=request.user)
        .values_list("exercise_id", flat=True)
    )
    return JsonResponse({"ids": ids})


@csrf_exempt
@require_POST
def toggle_favorite_api(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    ex = get_object_or_404(Exercise, pk=pk)

    fav = ExerciseFavorite.objects.filter(user=request.user, exercise=ex).first()
    if fav:
        fav.delete()
        return JsonResponse({"bookmarked": False})

    ExerciseFavorite.objects.create(user=request.user, exercise=ex)
    return JsonResponse({"bookmarked": True})