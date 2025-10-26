import calendar
import datetime
from django.utils import timezone
import json
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse, resolve
from howto.models import Exercise
from planner.forms import LogCompletionForm
from planner.models import WorkoutPlan
from planner.views import (
    PlanCreatorView,
    ExerciseSearchJSONView,
    AddPlanAPIView,
    GetPlansForDateAPIView,
    load_completion_form,
    ajax_complete_log
)

from django.contrib.auth.models import User

class PlannerUrlsTests(SimpleTestCase):
    """
    Test suite untuk URL patterns di aplikasi planner.
    """

    def test_plan_creator_url_resolves(self):
        """Test URL path '/planner/' resolves ke PlanCreatorView."""
        url_path = '/planner/'
        resolver_match = resolve(url_path)
        self.assertEqual(resolver_match.func.view_class, PlanCreatorView)

    def test_plan_creator_url_name_reverses(self):
        """Test URL name 'planner:plan_creator' reverses ke path yang benar."""
        url_name = 'planner:plan_creator'
        resolved_url = reverse(url_name)
        self.assertEqual(resolved_url, '/planner/')

    def test_search_exercises_url_resolves(self):
        """Test URL path '/planner/search-exercises/' resolves ke ExerciseSearchJSONView."""
        url_path = '/planner/search-exercises/'
        resolver_match = resolve(url_path)
        self.assertEqual(resolver_match.func.view_class, ExerciseSearchJSONView)

    def test_search_exercises_url_name_reverses(self):
        """Test URL name 'planner:search_exercises' reverses ke path yang benar."""
        url_name = 'planner:search_exercises'
        resolved_url = reverse(url_name)
        self.assertEqual(resolved_url, '/planner/search-exercises/')

    def test_api_add_plan_url_resolves(self):
        """Test URL path '/planner/api/add-plan/' resolves ke AddPlanAPIView."""
        url_path = '/planner/api/add-plan/'
        resolver_match = resolve(url_path)
        self.assertEqual(resolver_match.func.view_class, AddPlanAPIView)

    def test_api_add_plan_url_name_reverses(self):
        """Test URL name 'planner:api_add_plan' reverses ke path yang benar."""
        url_name = 'planner:api_add_plan'
        resolved_url = reverse(url_name)
        self.assertEqual(resolved_url, '/planner/api/add-plan/')

    def test_get_plans_for_date_url_resolves(self):
        """Test URL path '/planner/api/get-plans-for-date/' resolves ke GetPlansForDateAPIView."""
        url_path = '/planner/api/get-plans-for-date/'
        resolver_match = resolve(url_path)
        self.assertEqual(resolver_match.func.view_class, GetPlansForDateAPIView)

    def test_get_plans_for_date_url_name_reverses(self):
        """Test URL name 'planner:get_plans_for_date' reverses ke path yang benar."""
        url_name = 'planner:get_plans_for_date'
        resolved_url = reverse(url_name)
        self.assertEqual(resolved_url, '/planner/api/get-plans-for-date/')

    def test_load_completion_form_url_resolves(self):
        """Test URL path '/planner/log/load-form/<plan_id>/' resolves ke load_completion_form."""
        url_path = '/planner/log/load-form/1/'
        resolver_match = resolve(url_path)
        self.assertEqual(resolver_match.func, load_completion_form)
        self.assertEqual(resolver_match.kwargs['plan_id'], 1)

    def test_load_completion_form_url_name_reverses(self):
        """Test URL name 'planner:load_completion_form' reverses ke path yang benar."""
        url_name = 'planner:load_completion_form'
        args = [1]
        resolved_url = reverse(url_name, args=args)
        self.assertEqual(resolved_url, '/planner/log/load-form/1/')

    def test_ajax_complete_log_url_resolves(self):
        """Test URL path '/planner/log/complete/<plan_id>/' resolves ke ajax_complete_log."""
        url_path = '/planner/log/complete/1/'
        resolver_match = resolve(url_path)
        self.assertEqual(resolver_match.func, ajax_complete_log)
        self.assertEqual(resolver_match.kwargs['plan_id'], 1)

    def test_ajax_complete_log_url_name_reverses(self):
        """Test URL name 'planner:ajax_complete_log' reverses ke path yang benar."""
        url_name = 'planner:ajax_complete_log'
        args = [1]
        resolved_url = reverse(url_name, args=args)
        self.assertEqual(resolved_url, '/planner/log/complete/1/')


class TestPlannerViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')
        
        cls.exercise1 = Exercise.objects.create(exercise_name='Push Up', main_muscle='Chest')
        cls.exercise2 = Exercise.objects.create(exercise_name='Squat', main_muscle='Legs')

        cls.today = timezone.now().date()
        cls.yesterday = cls.today - datetime.timedelta(days=1)
        cls.last_month_date = cls.today - datetime.timedelta(days=30)
        
        cls.plan_today_incomplete = WorkoutPlan.objects.create(
            user=cls.user,
            exercise=cls.exercise1,
            sets=3,
            reps=10,
            plan_date=cls.today
        )
        
        cls.plan_today_complete = WorkoutPlan.objects.create(
            user=cls.user,
            exercise=cls.exercise2,
            sets=5,
            reps=5,
            plan_date=cls.today,
            is_completed=True,
            completed_at=timezone.now(),
            description="Good form"
        )
        
        cls.plan_yesterday_late = WorkoutPlan.objects.create(
            user=cls.user,
            exercise=cls.exercise1,
            sets=2,
            reps=8,
            plan_date=cls.yesterday,
            is_completed=True,
            completed_at=timezone.now(),
            description="Done late"
        )
        
        cls.plan_last_month = WorkoutPlan.objects.create(
            user=cls.user,
            exercise=cls.exercise1,
            sets=4,
            reps=12,
            plan_date=cls.last_month_date
        )

        cls.other_user = User.objects.create_user(username='otheruser', password='password123')
        cls.other_user_plan = WorkoutPlan.objects.create(
            user=cls.other_user,
            exercise=cls.exercise1,
            sets=1,
            reps=1,
            plan_date=cls.today
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='password123')
        self.login_url = reverse('authentication:login_user')


class TestPlanCreatorView(TestPlannerViews):

    def setUp(self):
        super().setUp()
        self.url = reverse('planner:plan_creator')

    def test_plan_creator_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_plan_creator_get_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planner/create_plan.html')

    def test_plan_creator_default_filter_this_month(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        context_plans = response.context['plans']
        self.assertIn(self.plan_today_incomplete, context_plans)
        self.assertIn(self.plan_today_complete, context_plans)
        self.assertIn(self.plan_yesterday_late, context_plans)
        self.assertNotIn(self.plan_last_month, context_plans)
        self.assertNotIn(self.other_user_plan, context_plans)

    def test_plan_creator_filter_by_last_month(self):
        url = f"{self.url}?year={self.last_month_date.year}&month={self.last_month_date.month}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        context_plans = response.context['plans']
        self.assertIn(self.plan_last_month, context_plans)
        self.assertNotIn(self.plan_today_incomplete, context_plans)

    def test_plan_creator_filter_invalid_params(self):
        url = f"{self.url}?year=abcd&month=xyz"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        context_plans = response.context['plans']
        self.assertIn(self.plan_today_incomplete, context_plans)
        self.assertNotIn(self.plan_last_month, context_plans)
        self.assertEqual(str(response.context['selected_year']), str(self.today.year))
        self.assertEqual(str(response.context['selected_month']), str(self.today.month))


class TestWorkoutLogView(TestPlannerViews):

    def setUp(self):
        super().setUp()
        self.url = reverse('planner:workout_log') 

    def test_log_view_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_log_view_get_authenticated_default_month(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planner/workout_log.html')
        
        context_plans = response.context['plans']
        self.assertIn(self.plan_today_incomplete, context_plans)
        self.assertIn(self.plan_yesterday_late, context_plans)
        self.assertNotIn(self.plan_last_month, context_plans)
        self.assertEqual(response.context['filter_type'], 'month')
        self.assertIn(calendar.month_name[self.today.month], response.context['period_name'])

    def test_log_view_filter_by_last_month(self):
        url = f"{self.url}?year={self.last_month_date.year}&month={self.last_month_date.month}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        context_plans = response.context['plans']
        self.assertIn(self.plan_last_month, context_plans)
        self.assertNotIn(self.plan_today_incomplete, context_plans)
        self.assertEqual(response.context['selected_year'], self.last_month_date.year)
        self.assertEqual(response.context['selected_month'], self.last_month_date.month)

    def test_log_view_filter_by_week(self):
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        month_dates = cal.monthdatescalendar(self.today.year, self.today.month)
        week_start_date = None
        for week in month_dates:
            if self.today in week:
                week_start_date = week[0]
                break
        
        self.assertIsNotNone(week_start_date)

        url = f"{self.url}?year={self.today.year}&month={self.today.month}&week_start_date={week_start_date.isoformat()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_type'], 'week')
        self.assertIn(self.plan_today_incomplete, response.context['plans'])
        
        if self.yesterday >= week_start_date:
            self.assertIn(self.plan_yesterday_late, response.context['plans'])
        else:
            self.assertNotIn(self.plan_yesterday_late, response.context['plans'])
            
        self.assertNotIn(self.plan_last_month, response.context['plans'])

    def test_log_view_stats_this_month(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        plans_this_month_count = WorkoutPlan.objects.filter(
            user=self.user,
            plan_date__year=self.today.year,
            plan_date__month=self.today.month
        ).count()

        self.assertEqual(response.context['total_plans_period'], plans_this_month_count)
        self.assertEqual(response.context['completed_plans_period'], 2)
        self.assertEqual(response.context['on_time_completed_period'], 1) 
        
        expected_perc = round((1 / plans_this_month_count) * 100, 1)
        self.assertEqual(response.context['completion_percentage_period'], expected_perc)

    def test_log_view_context_filters_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.today.year, response.context['available_years'])
        self.assertEqual(len(response.context['available_months']), 12)
        self.assertGreater(len(response.context['available_weeks']), 3)
        self.assertEqual(response.context['selected_year'], self.today.year)
        self.assertEqual(response.context['selected_month'], self.today.month)\
        
    def test_log_view_filter_invalid_month(self):
        """GAP 5: Test get_queryset jika bulan tidak valid (cth: 13)."""
        url = f"{self.url}?year={self.today.year}&month=13"
        response = self.client.get(url)
        
        # View harusnya mengabaikan bulan tidak valid dan kembali ke default (bulan ini)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_month'], self.today.month)
        self.assertEqual(response.context['selected_year'], self.today.year)
        self.assertIn(self.plan_today_incomplete, response.context['plans'])

    def test_log_view_filter_invalid_week_format(self):
        """GAP 6: Test get_queryset jika format week_start_date salah."""
        url = f"{self.url}?year={self.today.year}&month={self.today.month}&week_start_date=ini-bukan-tanggal"
        response = self.client.get(url)
        
        # View harusnya gagal mem-parsing tanggal dan kembali ke filter 'month'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_type'], 'month')
        self.assertIsNone(response.context['selected_week_start'])
        self.assertIn(self.plan_today_incomplete, response.context['plans'])

    def test_log_view_stats_no_plans_in_period(self):
        """GAP 7: Test get_context_data jika tidak ada plan (total_plans = 0)."""
        # Filter untuk bulan depan yang pasti kosong
        future_date = self.today + datetime.timedelta(days=40)
        url = f"{self.url}?year={future_date.year}&month={future_date.month}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_plans_period'], 0)
        self.assertEqual(response.context['completed_plans_period'], 0)
        # Pastikan tidak ada ZeroDivisionError
        self.assertEqual(response.context['completion_percentage_period'], 0)

    def test_log_view_context_no_plans_at_all_new_user(self):
        """GAP 7: Test get_context_data jika user baru (if not years)."""
        # Buat user baru yang tidak punya plan sama sekali
        new_user = User.objects.create_user(username='newuser', password='password123')
        self.client.login(username='newuser', password='password123')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_plans_period'], 0)
        
        # Pastikan 'available_years' default ke tahun ini
        self.assertEqual(len(response.context['available_years']), 1)
        self.assertEqual(response.context['available_years'][0], self.today.year)


class TestPlannerAPIs(TestPlannerViews):

    def test_search_exercises_get_anonymous(self):
        self.client.logout()
        url = reverse('planner:search_exercises')
        response = self.client.get(url, {'q': 'Push'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_search_exercises_success(self):
        url = reverse('planner:search_exercises')
        response = self.client.get(url, {'q': 'Push'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 1)
        self.assertEqual(data['exercises'][0]['name'], 'Push Up')
        self.assertEqual(data['exercises'][0]['id'], self.exercise1.id)

    def test_search_exercises_multiple_results(self):
        url = reverse('planner:search_exercises')
        response = self.client.get(url, {'q': 's'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['exercises']), 2)

    def test_search_exercises_no_results(self):
        url = reverse('planner:search_exercises')
        response = self.client.get(url, {'q': 'NonExistentExercise'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['exercises']), 0)

    def test_search_exercises_query_too_short(self):
        url = reverse('planner:search_exercises')
        response = self.client.get(url, {'q': 'P'})
        self.assertEqual(response.status_code, 400)

    def test_add_plan_post_anonymous(self):
        self.client.logout()
        url = reverse('planner:api_add_plan')
        payload = {
            'exercise_id': self.exercise1.id,
            'sets': 3,
            'reps': 10,
            'plan_date': self.today.isoformat()
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_add_plan_success(self):
        url = reverse('planner:api_add_plan')
        plan_date = (self.today + datetime.timedelta(days=5)).isoformat()
        payload = {
            'exercise_id': self.exercise1.id,
            'sets': 3,
            'reps': 10,
            'plan_date': plan_date
        }
        
        initial_count = WorkoutPlan.objects.count()
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(WorkoutPlan.objects.count(), initial_count + 1)
        
        data = response.json()
        self.assertEqual(data['exercise_name'], self.exercise1.exercise_name)
        self.assertEqual(data['sets'], 3)
        
        new_plan = WorkoutPlan.objects.get(id=data['id'])
        self.assertEqual(new_plan.user, self.user)
        self.assertEqual(new_plan.plan_date.isoformat(), plan_date)

    def test_add_plan_missing_data(self):
        url = reverse('planner:api_add_plan')
        payload = { 'exercise_id': self.exercise1.id, 'sets': 3 }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Data tidak lengkap', response.json()['error'])

    def test_add_plan_invalid_json(self):
        url = reverse('planner:api_add_plan')
        response = self.client.post(url, 'not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON', response.json()['error'])

    def test_add_plan_exercise_not_found(self):
        url = reverse('planner:api_add_plan')
        payload = {
            'exercise_id': 9999,
            'sets': 3,
            'reps': 10,
            'plan_date': self.today.isoformat()
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Latihan tidak ditemukan', response.json()['error'])

    def test_add_plan_invalid_numbers(self):
        url = reverse('planner:api_add_plan')
        payload = {
            'exercise_id': self.exercise1.id,
            'sets': -1,
            'reps': 0,
            'plan_date': self.today.isoformat()
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Sets dan Reps', response.json()['error'])

    def test_get_plans_for_date_success(self):
        url = reverse('planner:get_plans_for_date')
        response = self.client.get(url, {'date': self.today.isoformat()})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('plans', data)
        self.assertEqual(len(data['plans']), 2)
        
        plan_names = {p['exercise_name'] for p in data['plans']}
        self.assertIn('Push Up', plan_names)
        self.assertIn('Squat', plan_names)

    def test_get_plans_for_date_no_plans(self):
        url = reverse('planner:get_plans_for_date')
        no_plan_date = '1999-01-01'
        response = self.client.get(url, {'date': no_plan_date})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['plans']), 0)

    def test_get_plans_for_date_no_date_param(self):
        url = reverse('planner:get_plans_for_date')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Tanggal tidak diberikan', response.json()['error'])

    def test_get_plans_for_date_invalid_date_format(self):
        url = reverse('planner:get_plans_for_date')
        response = self.client.get(url, {'date': '25-10-2025'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Format tanggal tidak valid', response.json()['error'])

    def test_add_plan_invalid_date_format(self):
        """GAP 1: Test AddPlanAPIView jika format tanggal salah."""
        url = reverse('planner:api_add_plan')
        payload = {
            'exercise_id': self.exercise1.id,
            'sets': 3,
            'reps': 10,
            'plan_date': '26-10-2025' # Format DD-MM-YYYY (salah)
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Format tanggal tidak valid', response.json()['error'])

    def test_get_plans_for_date_get_anonymous(self):
        """GAP 2: Test GetPlansForDateAPIView jika user anonim."""
        self.client.logout()
        url = reverse('planner:get_plans_for_date')
        response = self.client.get(url, {'date': self.today.isoformat()})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)


class TestLogCompletionViews(TestPlannerViews):

    def setUp(self):
        super().setUp()
        self.plan_to_complete = WorkoutPlan.objects.create(
            user=self.user,
            exercise=self.exercise1,
            sets=5,
            reps=5,
            plan_date=self.today,
            is_completed=False
        )
        
        self.load_form_url = reverse('planner:load_completion_form', args=[self.plan_to_complete.id])
        self.complete_log_url = reverse('planner:ajax_complete_log', args=[self.plan_to_complete.id])
        self.other_user_plan_url = reverse('planner:ajax_complete_log', args=[self.other_user_plan.id])

    def test_load_form_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.load_form_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_load_form_get_authenticated(self):
        response = self.client.get(self.load_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planner/partials/_completion_form.html')
        self.assertIsInstance(response.context['form'], LogCompletionForm)
        self.assertEqual(response.context['plan'], self.plan_to_complete)

    def test_load_form_get_not_own_plan(self):
        url = reverse('planner:load_completion_form', args=[self.other_user_plan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_complete_log_post_anonymous(self):
        self.client.logout()
        response = self.client.post(self.complete_log_url, {'description': 'Done'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_complete_log_get_not_allowed(self):
        response = self.client.get(self.complete_log_url)
        self.assertEqual(response.status_code, 405)

    def test_complete_log_success(self):
        description_text = "Selesai dengan baik"
        response = self.client.post(self.complete_log_url, {'description': description_text})
        
        self.assertEqual(response.status_code, 200)
        
        self.plan_to_complete.refresh_from_db()
        self.assertTrue(self.plan_to_complete.is_completed)
        self.assertEqual(self.plan_to_complete.description, description_text)
        self.assertIsNotNone(self.plan_to_complete.completed_at)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['plan_id'], self.plan_to_complete.id)
        self.assertEqual(data['description'], description_text)
        self.assertTrue(data['on_time'])

    def test_complete_log_update_existing(self):
        plan = WorkoutPlan.objects.create(
            user=self.user,
            exercise=self.exercise1,
            sets=1, reps=1,
            plan_date=self.yesterday,
            is_completed=True,
            completed_at=timezone.now() - datetime.timedelta(days=1),
            description="First entry"
        )
        url = reverse('planner:ajax_complete_log', args=[plan.id])
        new_description = "Updated entry"
        
        response = self.client.post(url, {'description': new_description})
        self.assertEqual(response.status_code, 200)
        
        plan.refresh_from_db()
        self.assertTrue(plan.is_completed)
        self.assertEqual(plan.description, new_description)
        
        data = response.json()
        self.assertEqual(data['description'], new_description)

    def test_complete_log_invalid_form(self):
        form = LogCompletionForm(instance=self.plan_to_complete)
        if 'description' in form.fields and form.fields['description'].required:
            response = self.client.post(self.complete_log_url, {'description': ''})
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertEqual(data['status'], 'error')
            self.assertIn('errors', data)
        else:
            self.skipTest("LogCompletionForm's 'description' is not required, cannot test invalid state easily.")

    def test_complete_log_not_own_plan(self):
        response = self.client.post(self.other_user_plan_url, {'description': 'Trying to hack'})
        self.assertEqual(response.status_code, 404)

    def test_load_form_get_non_existent_plan(self):
        """GAP 3: Test load_completion_form jika ID plan tidak ada."""
        url = reverse('planner:load_completion_form', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_complete_log_post_non_existent_plan(self):
        """GAP 4: Test ajax_complete_log jika ID plan tidak ada."""
        url = reverse('planner:ajax_complete_log', args=[99999])
        response = self.client.post(url, {'description': 'Test'})
        self.assertEqual(response.status_code, 404)

    def test_complete_log_late_on_time_false(self):
        """GAP 8: Test 'on_time' response jika log diselesaikan terlambat."""
        # Buat rencana untuk kemarin
        plan_yesterday = WorkoutPlan.objects.create(
            user=self.user,
            exercise=self.exercise1,
            sets=1, reps=1,
            plan_date=self.yesterday, # Dibuat untuk kemarin
            is_completed=False
        )
        url = reverse('planner:ajax_complete_log', args=[plan_yesterday.id])
        
        # Selesaikan hari ini
        response = self.client.post(url, {'description': 'Selesai terlambat'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['on_time'])