from django.test import SimpleTestCase
from django.urls import reverse, resolve
from planner.views import (
    PlanCreatorView,
    ExerciseSearchJSONView,
    AddPlanAPIView,
    GetPlansForDateAPIView,
    load_completion_form,
    ajax_complete_log
)

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