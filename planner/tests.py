import json
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from planner.models import WorkoutPlan 

from howto.models import Exercise

# Get the User model
User = get_user_model()


class PlannerAppTestCase(TestCase):
    
    def setUp(self):
        """
        Set up the necessary data for all tests.
        This runs once before every test function.
        """
        
        # 1. Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword123'
        )
        
        # 2. Create some test exercises (from the 'howto' app)
        self.exercise1 = Exercise.objects.create(exercise_name='Test Bench Press')
        self.exercise2 = Exercise.objects.create(exercise_name='Test Squat')
        
        # 3. Create a test workout plan item
        self.today = datetime.date.today()
        self.plan1 = WorkoutPlan.objects.create(
            user=self.user,
            exercise=self.exercise1,
            sets=3,
            reps=10,
            plan_date=self.today
        )
        
        # 4. Create a client and log in
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')

    # ----------------------------------------
    # Model Tests
    # ----------------------------------------

    def test_workout_plan_str(self):
        """Test the string representation of the WorkoutPlan model."""
        expected_str = f"testuser - Test Bench Press (3 sets x 10 reps) on {self.today}"
        self.assertEqual(str(self.plan1), expected_str)

    # ----------------------------------------
    # Page View Tests (Checking HTML pages)
    # ----------------------------------------

    def test_plan_creator_view_logged_in(self):
        """Test that the planner creator page loads for a logged-in user."""
        url = reverse('planner:plan_creator') # /planner/
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planner/create_plan.html')

    def test_plan_creator_view_logged_out(self):
        """Test that the planner creator page redirects if logged out."""
        self.client.logout()
        url = reverse('planner:plan_creator') # /planner/
        response = self.client.get(url)
        # Should redirect (302) to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_workout_log_view_logged_in(self):
        """Test that the log page loads for a logged-in user."""
        url = reverse('workout_log') # /log/
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planner/workout_log.html')
        # Check that our plan is in the context
        self.assertIn('grouped_plans', response.context)
        self.assertIn(str(self.today), response.context['grouped_plans'])

    def test_workout_log_view_logged_out(self):
        """Test that the log page redirects if logged out."""
        self.client.logout()
        url = reverse('workout_log') # /log/
        response = self.client.get(url)
        # Should redirect (302) to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    # ----------------------------------------
    # API View Tests (Checking JSON endpoints)
    # ----------------------------------------

    def test_exercise_search_api_success(self):
        """Test the exercise search API for a successful search."""
        url = reverse('planner:search_exercises') + '?q=Bench'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 1)
        self.assertEqual(data['exercises'][0]['name'], 'Test Bench Press')

    def test_exercise_search_api_no_results(self):
        """Test the exercise search API for a query with no results."""
        url = reverse('planner:search_exercises') + '?q=nonexistent'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 0)

    def test_add_plan_api_success(self):
        """Test successfully adding a new plan item via the API."""
        url = reverse('planner:add_plan_api')
        post_data = {
            'exercise_id': self.exercise2.id,
            'sets': 5,
            'reps': 5,
            'plan_date': str(self.today)
        }
        
        # Check that a new object is created
        initial_count = WorkoutPlan.objects.count()
        response = self.client.post(
            url, 
            data=json.dumps(post_data), 
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 201) # 201 = Created
        self.assertEqual(WorkoutPlan.objects.count(), initial_count + 1)
        
        # Check the response data
        data = response.json()
        self.assertEqual(data['name'], 'Test Squat')
        self.assertEqual(data['sets'], 5)

    def test_add_plan_api_invalid_data(self):
        """Test that the add plan API returns an error for invalid data."""
        url = reverse('planner:add_plan_api')
        post_data = {
            'exercise_id': self.exercise2.id,
            'sets': 0, # Invalid!
            'reps': 5,
            'plan_date': str(self.today)
        }
        
        initial_count = WorkoutPlan.objects.count()
        response = self.client.post(
            url, 
            data=json.dumps(post_data), 
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400) # 400 = Bad Request
        self.assertEqual(WorkoutPlan.objects.count(), initial_count) # No object created
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid data: Sets and reps must be positive numbers.')

    def test_get_plans_for_date_api(self):
        """Test getting all plans for a specific date via the API."""
        url = reverse('planner:get_plans_for_date') + f'?date={self.today}'
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('plans', data)
        self.assertEqual(len(data['plans']), 1)
        self.assertEqual(data['plans'][0]['name'], 'Test Bench Press')

