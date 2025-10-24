from django.test import TestCase, Client
from django.urls import reverse
from .models import Exercise


class ExerciseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # buat contoh data dummy
        self.exercise1 = Exercise.objects.create(
            exercise_name="Push-Up",
            main_muscle="Chest",
            equipment="Body Weight",
            instructions="Place hands on floor, push body up and down."
        )
        self.exercise2 = Exercise.objects.create(
            exercise_name="Squat",
            main_muscle="Legs",
            equipment="Barbell",
            instructions="Keep back straight, bend knees, and push up."
        )

    def test_exercise_list_status_code(self):
        """Pastikan halaman /howto/ bisa diakses (status 200)."""
        response = self.client.get(reverse('howto:exercise_list'))
        self.assertEqual(response.status_code, 200)

    def test_exercise_list_content(self):
        """Pastikan semua latihan muncul di template list."""
        response = self.client.get(reverse('howto:exercise_list'))
        self.assertContains(response, "Push-Up")
        self.assertContains(response, "Squat")

    def test_exercise_list_filter_by_muscle(self):
        """Filter by main_muscle harus menampilkan data yang sesuai."""
        response = self.client.get(reverse('howto:exercise_list'), {'muscle': 'Chest'})
        self.assertContains(response, "Push-Up")
        self.assertNotContains(response, "Squat")

    def test_exercise_list_filter_by_equipment(self):
        """Filter by equipment harus menampilkan data yang sesuai."""
        response = self.client.get(reverse('howto:exercise_list'), {'equipment': 'Barbell'})
        self.assertContains(response, "Squat")
        self.assertNotContains(response, "Push-Up")

    def test_exercise_detail_view(self):
        """Pastikan halaman detail latihan bisa diakses."""
        url = reverse('howto:exercise_detail', args=[self.exercise1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Push-Up")
        self.assertContains(response, "Chest")
        self.assertContains(response, "Body Weight")

    def test_exercise_detail_404(self):
        """Pastikan latihan yang tidak ada menghasilkan 404."""
        url = reverse('howto:exercise_detail', args=[9999])  # id fiktif
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
