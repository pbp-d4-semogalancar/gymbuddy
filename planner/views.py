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
from django.views.decorators.csrf import csrf_exempt  
from django.utils.decorators import method_decorator 
from django.contrib.auth.models import User          
from django.conf import settings                     

from howto.models import Exercise
from .models import WorkoutPlan
from .forms import LogCompletionForm 

# --- HELPER FUNCTION ---
def get_weeks_in_month(year, month):
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

# --- VIEW WEB (Tetap pakai LoginRequiredMixin) ---
class PlanCreatorView(LoginRequiredMixin, ListView): 
    model = WorkoutPlan
    template_name = 'planner/create_plan.html'
    context_object_name = 'plans' 

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        return context

class WorkoutLogView(LoginRequiredMixin, ListView): 
    model = WorkoutPlan 
    template_name = 'planner/workout_log.html' 
    context_object_name = 'plans' 

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        filtered_plans = context['plans']

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

        if self.filter_type == 'week' and self.selected_week_start:
             selected_week_obj = next((w for w in weeks if w['value'] == self.selected_week_start), None)
             context['period_name'] = f"Minggu ({selected_week_obj['display'] if selected_week_obj else self.selected_week_start})"
        else:
             context['period_name'] = f"Bulan {calendar.month_name[self.month_for_context]} {self.year_for_context}"
        context['timezone'] = timezone
        return context

# --- API VIEWS (MODIFIED FOR FLUTTER) ---

class ExerciseSearchJSONView(View): # HAPUS LoginRequiredMixin
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'exercises': []}, status=200)
            
        try:
            matching_exercises = Exercise.objects.filter(
                exercise_name__icontains=query
            )[:10]
            
            exercises_list = []
            for exercise in matching_exercises:
                exercises_list.append({
                    'id': exercise.id,
                    'name': exercise.exercise_name
                })
            
            return JsonResponse({'exercises': exercises_list})
            
        except Exception as e:
            print(f"Error in ExerciseSearchJSONView: {e}") 
            return JsonResponse({'error': 'Failed to search exercises.'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AddPlanAPIView(View): # HAPUS LoginRequiredMixin
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            exercise_id = data.get('exercise_id')
            sets = data.get('sets')
            reps = data.get('reps')
            plan_date_str = data.get('plan_date')

            if not all([exercise_id, sets, reps, plan_date_str]):
                return JsonResponse({'error': 'Data tidak lengkap.'}, status=400)
            
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                return JsonResponse({'error': 'Latihan tidak ditemukan.'}, status=404)
            
            # --- LOGIKA DEV MODE: FALLBACK USER ---
            user = request.user
            if not user.is_authenticated:
                if settings.DEBUG:
                    user = User.objects.first() 
                    print("DEBUG: Using fallback user for AddPlan")
                else:
                    return JsonResponse({'error': 'Authentication required.'}, status=401)
            
            if not user:
                 return JsonResponse({'error': 'No user available'}, status=400)
            # --------------------------------------
            
            try:
                plan_date = datetime.date.fromisoformat(plan_date_str)
            except ValueError:
                return JsonResponse({'error': 'Format tanggal tidak valid.'}, status=400)
            
            plan_item = WorkoutPlan.objects.create(
                user=user,
                exercise=exercise,
                sets=sets,
                reps=reps,
                plan_date=plan_date
            )
            
            return JsonResponse({
                'id': plan_item.id,
                'exercise_name': plan_item.exercise.exercise_name,
                'sets': plan_item.sets,
                'reps': plan_item.reps
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            print(f"Error in AddPlanAPIView: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class GetPlansForDateAPIView(View): # HAPUS LoginRequiredMixin
    def get(self, request, *args, **kwargs):
        date_str = request.GET.get('date', None)
        
        if not date_str:
            return JsonResponse({'error': 'Tanggal tidak diberikan.'}, status=400)
            
        try:
            plan_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return JsonResponse({'error': 'Format tanggal tidak valid.'}, status=400)
            
        # --- LOGIKA DEV MODE: FALLBACK USER ---
        user = request.user
        if not user.is_authenticated:
            if settings.DEBUG:
                user = User.objects.first()
                print("DEBUG: Using fallback user for GetPlans")
            else:
                return JsonResponse({'error': 'Authentication required.'}, status=401)
        
        if not user:
             return JsonResponse({'error': 'No user available'}, status=400)
        # --------------------------------------

        try:
            plans = WorkoutPlan.objects.filter(
                user=user, 
                plan_date=plan_date
            )
            
            plans_list = []
            for plan_item in plans:
                plans_list.append({
                    'id': plan_item.id,
                    'exercise_name': plan_item.exercise.exercise_name,
                    # Handle NULL di backend agar Flutter tidak crash
                    'sets': plan_item.sets if plan_item.sets is not None else 0,
                    'reps': plan_item.reps if plan_item.reps is not None else 0,
                })
                
            return JsonResponse({'plans': plans_list})
            
        except Exception as e:
            print(f"Error in GetPlansForDateAPIView: {e}")
            return JsonResponse({'error': 'Gagal mengambil data rencana.'}, status=500)

# --- VIEWS WEB AJAX (LOGIN REQUIRED) ---

@login_required
def load_completion_form(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id, user=request.user)
    form = LogCompletionForm(instance=plan)
    context = {'form': form, 'plan': plan}
    return render(request, 'planner/partials/_completion_form.html', context)

@require_POST 
@login_required
def ajax_complete_log(request, plan_id):
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
            "completed_at": log.completed_at.strftime("%d %b %Y, %H:%M") if log.completed_at else None,
            "on_time": log.completed_at.date() <= log.plan_date if log.completed_at else False
        }, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Data tidak valid.", "errors": form.errors}, status=400)

# --- FLUTTER API VIEWS (NO LOGIN REQUIRED FOR DEV) ---

@csrf_exempt # WAJIB untuk endpoint ini
def api_complete_log(request, plan_id):
    """
    API endpoint untuk menandai log selesai dari Flutter.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # --- LOGIKA DEV MODE: FALLBACK USER ---
    user = request.user
    if not user.is_authenticated:
        if settings.DEBUG:
            user = User.objects.first()
        else:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
    
    if not user:
        return JsonResponse({'error': 'No user available'}, status=400)
    # --------------------------------------

    plan = get_object_or_404(WorkoutPlan, id=plan_id, user=user)
    
    # Ambil deskripsi dari POST data
    description = request.POST.get('description', '')

    if not plan.is_completed:
        plan.is_completed = True
        plan.completed_at = timezone.now()
    
    plan.description = description
    plan.save()

    return JsonResponse({
        "status": "success",
        "message": "Log updated",
        "is_completed": True
    })

# Hapus LoginRequiredMixin dari sini juga!
def get_workout_logs_api(request):
    """
    API endpoint untuk mengambil data log latihan (JSON) untuk Flutter.
    URL: /planner/api/get-logs/
    """
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    selected_week_start = request.GET.get('week_start_date')

    today = timezone.now().date()
    try:
        year = int(selected_year) if selected_year else today.year
        month = int(selected_month) if selected_month else today.month
    except ValueError:
        year = today.year
        month = today.month

    # --- LOGIKA DEV MODE: FALLBACK USER ---
    user = request.user
    if not user.is_authenticated:
        if settings.DEBUG:
            user = User.objects.first()
        else:
            return JsonResponse({'error': 'Auth required'}, status=401)
    
    if not user:
        return JsonResponse({'error': 'No user'}, status=400)
    # --------------------------------------

    queryset = WorkoutPlan.objects.filter(user=user)

    filter_type = 'month'
    if selected_year and selected_month and selected_week_start:
        try:
            start_date = datetime.datetime.strptime(selected_week_start, '%Y-%m-%d').date()
            end_date = start_date + datetime.timedelta(days=6)
            queryset = queryset.filter(
                plan_date__year=year,
                plan_date__month=month,
                plan_date__range=[start_date, end_date]
            )
            filter_type = 'week'
        except ValueError:
            queryset = queryset.filter(plan_date__year=year, plan_date__month=month)
    else:
        queryset = queryset.filter(plan_date__year=year, plan_date__month=month)

    queryset = queryset.order_by('plan_date', 'id')

    total_plans = queryset.count()
    completed_plans = queryset.filter(is_completed=True).count()
    on_time_completed = 0
    plans_data = []
    
    nama_bulan_id = [
        None, 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]

    for plan in queryset:
        if plan.is_completed and plan.completed_at and plan.completed_at.date() <= plan.plan_date:
            on_time_completed += 1
            
        plans_data.append({
            'id': plan.id,
            'user': plan.user.id,
            'exercise_id': plan.exercise.id,
            'exercise_name': plan.exercise.exercise_name,
            'sets': plan.sets or 0,
            'reps': plan.reps or 0,
            'plan_date': plan.plan_date.strftime('%Y-%m-%d'),
            'description': plan.description,
            'is_completed': plan.is_completed,
            'completed_at': plan.completed_at.strftime('%Y-%m-%d %H:%M:%S') if plan.completed_at else None,
        })

    percentage = (on_time_completed / total_plans) * 100 if total_plans > 0 else 0

    month_name = nama_bulan_id[month] if 1 <= month <= 12 else ''
    if filter_type == 'week' and selected_week_start:
        period_name = f"Minggu ({selected_week_start}) - {month_name} {year}"
    else:
        period_name = f"Bulan {month_name} {year}"

    return JsonResponse({
        'plans': plans_data,
        'total_plans': total_plans,
        'completed_plans': completed_plans,
        'on_time_completed': on_time_completed,
        'percentage': round(percentage, 1),
        'period_name': period_name,
    })