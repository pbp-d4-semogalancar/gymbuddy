from django.core.management.base import BaseCommand
from howto.utils.data_processor import load_dataset
from howto.models import Exercise

class Command(BaseCommand):
    help = 'Import exercise data from gym_exercises.csv into the database'

    def handle(self, *args, **options):
        df = load_dataset("howto/utils/gym_exercises.csv")

        imported = 0
        skipped = 0

        for _, row in df.iterrows():
            obj, created = Exercise.objects.get_or_create(
                exercise_name=row['exercise_name'],
                defaults={
                    'main_muscle': row['main_muscle'],
                    'equipment': row['equipment'],
                    'instructions': row['instructions'],
                }
            )
            if created:
                imported += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Imported {imported} new exercises, skipped {skipped} duplicates (total: {len(df)})"
            )
        )
#untuk jalanin:
#python manage.py import_exercises (lewat terminal)
