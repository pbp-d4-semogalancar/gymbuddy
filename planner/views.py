import json
import datetime
import calendar 
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_POST 
from django.utils import timezone 
from django.db.models.functions import ExtractMonth, ExtractYear 
from howto.models import Exercise
from .models import WorkoutPlan
from .forms import LogCompletionForm 

def get_weeks_in_month(year, month):
    """
    Menghasilkan list dictionary berisi minggu-minggu dalam bulan/tahun.
    Setiap dictionary berisi 'value' (tanggal awal minggu YYYY-MM-DD)
    dan 'display' (rentang tanggal, cth: 'Oct 20 - Oct 26').
    Minggu dimulai dari Minggu (Sunday).
    """
    weeks = []
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    month_days = cal.monthdatescalendar(year, month)

    for week_days in month_days:
        start_date = week_days[0]
        end_date = week_days[-1]
        if start_date.month == month or end_date.month == month:
             first_day_in_month = datetime.date(year, month, 1)
             last_day_month_num = calendar.monthrange(year, month)[1]
             last_date_in_month = datetime.date(year, month, last_day_month_num)
             actual_start = max(start_date, first_day_in_month)
             actual_end = min(end_date, last_date_in_month)

             if actual_start <= actual_end : 
                 weeks.append({
                     'value': start_date.strftime('%Y-%m-%d'),
                     'display': f"{actual_start.strftime('%b %d')} - {actual_end.strftime('%b %d')}"
                 })
    return weeks

class PlanCreatorView(LoginRequiredMixin, ListView): 
    model = WorkoutPlan
    template_name = 'planner/create_plan.html'
    context_object_name = 'plans' 

    def get_queryset(self):
        """Filter queryset berdasarkan user dan bulan/tahun."""
        queryset = super().get_queryset().filter(user=self.request.user)

        self.selected_year = self.request.GET.get('year')
        self.selected_month = self.request.GET.get('month')

        if self.selected_year and self.selected_month:
            try:
                queryset = queryset.filter(
                    plan_date__year=int(self.selected_year),
                    plan_date__month=int(self.selected_month)
                )
            except ValueError:
                pass
        else:
             today = timezone.now().date()
             self.selected_year = str(today.year)
             self.selected_month = str(today.month)
             queryset = queryset.filter(
                 plan_date__year=today.year,
                 plan_date__month=today.month
             )

        return queryset.order_by('-plan_date', 'is_completed', 'id') 

    def get_context_data(self, **kwargs):
        """Tambahkan data statistik dan filter ke context."""
        context = super().get_context_data(**kwargs)

        return context

class ExerciseSearchJSONView(LoginRequiredMixin, View):
    """
    Responds to AJAX GET requests to search for exercises.
    Called by the 'Cari Latihan' search bar.
    URL: /planner/search-exercises/
    """
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        # We check for a query length again just to be safe
        if len(query) < 2:
            return JsonResponse({'exercises': []}, status=400)
            
        try:
            # Find exercises matching the query
            # We limit to 10 results for performance
            matching_exercises = Exercise.objects.filter(
                exercise_name__icontains=query
            )[:10]
            
            # Manually build the list to avoid serialization errors
            # This is safer than using .values()
            exercises_list = []
            for exercise in matching_exercises:
                exercises_list.append({
                    'id': exercise.id,
                    'name': exercise.exercise_name
                })
            
            return JsonResponse({'exercises': exercises_list})
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error in ExerciseSearchJSONView: {e}") 
            return JsonResponse({'error': 'Failed to search exercises.'}, status=500)

class AddPlanAPIView(LoginRequiredMixin, View):
    """
    Responds to AJAX POST requests to add a new workout item.
    Called by the 'Tambahkan ke Rencana' button.
    URL: /planner/api/add-plan/
    """
    def post(self, request, *args, **kwargs):
        try:
            # Load data from the request body
            data = json.loads(request.body)
            exercise_id = data.get('exercise_id')
            sets = data.get('sets')
            reps = data.get('reps')
            plan_date_str = data.get('plan_date') # e.g., "2025-10-24"

            # --- Validation ---
            if not all([exercise_id, sets, reps, plan_date_str]):
                return JsonResponse({'error': 'Data tidak lengkap.'}, status=400)
            
            # Check if exercise exists
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                return JsonResponse({'error': 'Latihan tidak ditemukan.'}, status=404)
            
            # Check for valid numbers
            if not (isinstance(sets, int) and sets > 0 and isinstance(reps, int) and reps > 0):
                 return JsonResponse({'error': 'Sets dan Reps harus angka positif.'}, status=400)
            
            # Check for valid date format
            try:
                plan_date = datetime.date.fromisoformat(plan_date_str)
            except ValueError:
                return JsonResponse({'error': 'Format tanggal tidak valid.'}, status=400)
            
            # --- Create and Save the Object ---
            plan_item = WorkoutPlan.objects.create(
                user=request.user,
                exercise=exercise,
                sets=sets,
                reps=reps,
                plan_date=plan_date
            )
            
            # --- Return the created object as JSON ---
            # This is what the JavaScript uses to update the list
            return JsonResponse({
                'id': plan_item.id,
                'exercise_name': plan_item.exercise.exercise_name,
                'sets': plan_item.sets,
                'reps': plan_item.reps
            }, status=201) # 201 = Created

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(f"Error in AddPlanAPIView: {e}")
            return JsonResponse({'error': 'Terjadi kesalahan di server.'}, status=500)


class GetPlansForDateAPIView(LoginRequiredMixin, View):
    """
    Responds to AJAX GET requests to fetch all plan items for a specific date.
    Called when the page loads and when the date picker changes.
    URL: /planner/api/get-plans-for-date/
    """
    def get(self, request, *args, **kwargs):
        date_str = request.GET.get('date', None)
        
        if not date_str:
            return JsonResponse({'error': 'Tanggal tidak diberikan.'}, status=400)
            
        try:
            plan_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return JsonResponse({'error': 'Format tanggal tidak valid.'}, status=400)
            
        try:
            plans = WorkoutPlan.objects.filter(
                user=request.user, 
                plan_date=plan_date
            )
            
            # Build the list of plans
            plans_list = []
            for plan_item in plans:
                plans_list.append({
                    'id': plan_item.id,
                    'exercise_name': plan_item.exercise.exercise_name,
                    'sets': plan_item.sets,
                    'reps': plan_item.reps 
                })
                
            return JsonResponse({'plans': plans_list})
            
        except Exception as e:
            print(f"Error in GetPlansForDateAPIView: {e}")
            return JsonResponse({'error': 'Gagal mengambil data rencana.'}, status=500)
        
@login_required
def load_completion_form(request, plan_id):
    """
    AJAX view (GET) untuk memuat form deskripsi ke dalam modal.
    Mengirimkan HTML partial.
    """
    plan = get_object_or_404(WorkoutPlan, id=plan_id, user=request.user)
    form = LogCompletionForm(instance=plan)
    context = {'form': form, 'plan': plan}
    return render(request, 'planner/partials/_completion_form.html', context)

@require_POST 
@login_required
def ajax_complete_log(request, plan_id):
    """
    AJAX view (POST) untuk memproses submit form dari modal.
    Menandai log sebagai selesai (is_completed=True), mencatat waktu (completed_at),
    dan menyimpan deskripsi. Mengembalikan JSON response.
    """
    plan = get_object_or_404(WorkoutPlan, id=plan_id, user=request.user)

    form = LogCompletionForm(request.POST, instance=plan)

    if form.is_valid():
        log = form.save(commit=False)
        if not log.is_completed:
            log.is_completed = True
            log.completed_at = timezone.now() 
        log.save()
        return JsonResponse({
            "status": "success",
            "message": "Log berhasil disimpan!",
            "plan_id": plan.id,
            "description": log.description,
            "is_completed": log.is_completed,
            # Format waktu jika ada
            "completed_at": log.completed_at.strftime("%d %b %Y, %H:%M") if log.completed_at else None,
            "on_time": log.completed_at.date() <= log.plan_date if log.completed_at else False
        }, status=200)
    else:
        # Kirim error validasi form jika ada
        return JsonResponse({"status": "error", "message": "Data tidak valid.", "errors": form.errors}, status=400)
        
class WorkoutLogView(LoginRequiredMixin, ListView): 
    model = WorkoutPlan 
    template_name = 'planner/workout_log.html' 
    context_object_name = 'plans' 

    def get_queryset(self):
        """Filter queryset berdasarkan user dan periode (minggu/bulan)."""
        queryset = super().get_queryset().filter(user=self.request.user)

        self.selected_year = self.request.GET.get('year')
        self.selected_month = self.request.GET.get('month')
        self.selected_week_start = self.request.GET.get('week_start_date') 

        today = timezone.now().date()
        current_year = today.year
        current_month = today.month

        try:
            year = int(self.selected_year) if self.selected_year else current_year
            month = int(self.selected_month) if self.selected_month else current_month
             # Validasi bulan
            if not (1 <= month <= 12):
                month = current_month
                year = current_year 
        except (ValueError, TypeError):
            year = current_year
            month = current_month

        self.year_for_context = year
        self.month_for_context = month

        if self.selected_year and self.selected_month and self.selected_week_start:
            try:
                start_date = datetime.datetime.strptime(self.selected_week_start, '%Y-%m-%d').date()
                end_date = start_date + datetime.timedelta(days=6)
                queryset = queryset.filter(
                    plan_date__year=year,
                    plan_date__month=month,
                    plan_date__range=[start_date, end_date]
                )
                self.period_start_date = start_date
                self.period_end_date = end_date
                self.filter_type = 'week'

            except ValueError:
                queryset = queryset.filter(plan_date__year=year, plan_date__month=month)
                self.period_start_date = datetime.date(year, month, 1)
                self.period_end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])
                self.filter_type = 'month'
                self.selected_week_start = None
        else:
            queryset = queryset.filter(plan_date__year=year, plan_date__month=month)
            self.period_start_date = datetime.date(year, month, 1)
            self.period_end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])
            self.filter_type = 'month'
            self.selected_week_start = None 
        return queryset.order_by('plan_date', 'id')

    def get_context_data(self, **kwargs):
        """Tambahkan data statistik periode dan filter ke context."""
        context = super().get_context_data(**kwargs)
        filtered_plans = context['plans'] #

        total_plans = filtered_plans.count()
        completed_plans = filtered_plans.filter(is_completed=True)
        completed_count = completed_plans.count()

        on_time_completed = 0
        for plan in completed_plans:
             if plan.completed_at and plan.completed_at.date() <= plan.plan_date:
                on_time_completed += 1
        percentage = (on_time_completed / total_plans) * 100 if total_plans > 0 else 0

        context['total_plans_period'] = total_plans
        context['completed_plans_period'] = completed_count
        context['on_time_completed_period'] = on_time_completed
        context['completion_percentage_period'] = round(percentage, 1)

        years = WorkoutPlan.objects.filter(user=self.request.user)\
                                   .annotate(year=ExtractYear('plan_date'))\
                                   .values_list('year', flat=True).distinct().order_by('-year')
        if not years:
             years = [timezone.now().year]

        months = [{'value': i, 'name': calendar.month_name[i]} for i in range(1, 13)]
        weeks = get_weeks_in_month(self.year_for_context, self.month_for_context)

        context['available_years'] = years
        context['available_months'] = months
        context['available_weeks'] = weeks 
        context['selected_year'] = self.year_for_context
        context['selected_month'] = self.month_for_context
        context['selected_week_start'] = self.selected_week_start 

        # Untuk judul statistik (Minggu X atau Bulan Y)
        if self.filter_type == 'week' and self.selected_week_start:
             selected_week_obj = next((w for w in weeks if w['value'] == self.selected_week_start), None)
             context['period_name'] = f"Minggu ({selected_week_obj['display'] if selected_week_obj else self.selected_week_start})"
        else:
             context['period_name'] = f"Bulan {calendar.month_name[self.month_for_context]} {self.year_for_context}"
        context['timezone'] = timezone

        return context



