from .models import Exercise

def exercise_to_dict(ex: Exercise):
    return {
        "id": ex.id,
        "exercise_name": ex.exercise_name,
        "main_muscle": ex.main_muscle,
        "equipment": ex.equipment,
        "instructions": ex.instructions,
        "image": ex.image.url if ex.image else None,
    }
