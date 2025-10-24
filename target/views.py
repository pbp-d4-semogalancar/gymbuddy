from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Target, Activity
from .forms import TargetCreateForm, LogUpdateForm
from datetime import date, timedelta
import json

@login_required
def gym_log_page(request):
    targets = Target.objects.filter(user=request.user)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    total_todos_this_week = targets.filter(
        planned_date__gte=start_of_week
    ).count()
    
    completed_todos_this_week = targets.filter(
        planned_date__gte=start_of_week,
        is_completed=True
    ).count()
    
    percent_complete = 0
    if total_todos_this_week > 0:
        percent_complete = round((completed_todos_this_week / total_todos_this_week) * 100)

    context = {
        'targets': targets,
        'percent_complete': percent_complete,
    }
    return render(request, 'targetlog/gym_log.html', context)

@login_required 
def ajax_filter_activities(request):
    """
    AJAX view untuk filter Activity (dataset) berdasarkan target muscle.
    """
    target_muscle = request.GET.get('target_muscle')

    if target_muscle:
        activities = Activity.objects.filter(target_muscle=target_muscle)
    else:
        activities = Activity.objects.all()
        
    options = '<option value="">-- Select an activity --</option>'
    for act in activities:
        options += f'<option value="{act.id}">{act.name}</option>'
        
    return HttpResponse(options)


@login_required
def load_add_target_form(request):
    """
    AJAX (dipanggil fetch) untuk memuat partial form "Add Target"
    """
    form = TargetCreateForm()
    
    target_muscles = Activity.objects.values_list('target_muscle', flat=True).distinct()
    
    context = {
        'form': form,
        'target_muscles': target_muscles
    }

    return render(request, 'targetlog/main/_add_target_form.html', context)

@login_required
def ajax_add_target(request):
    """
    AJAX (dipanggil fetch) untuk memproses submit "Add Target"
    """
    if request.method == 'POST':
        form = TargetCreateForm(request.POST)
        
        if form.is_valid():
            target = form.save(commit=False)
            target.user = request.user 
            target.is_completed = False
            target.save()

            return JsonResponse({"status": "success", "message": "Rencana berhasil ditambahkan!"}, status=201)
        else:

            return JsonResponse({"status": "error", "message": "Data tidak valid.", "errors": form.errors}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required 
def load_update_log_form(request, target_id):
    """
    AJAX (dipanggil fetch) untuk memuat partial form "Update Log"
    """
    target = get_object_or_404(Target, id=target_id, user=request.user)
    form = LogUpdateForm(instance=target) #
    
    context = {'form': form, 'target': target}
    return render(request, 'targetlog/main/_update_log_form.html', context)

@login_required
def ajax_submit_log(request, target_id):
    """
    AJAX (dipanggil fetch) untuk memproses submit "Update Log"
    """
    target = get_object_or_404(Target, id=target_id, user=request.user)
    
    if request.method == 'POST':
        form = LogUpdateForm(request.POST, instance=target)
        
        if form.is_valid():
            log = form.save(commit=False)
            log.is_completed = True 
            log.save()
            return JsonResponse({"status": "success", "message": "Log berhasil disimpan!"}, status=200)
        else:
            return JsonResponse({"status": "error", "message": "Data tidak valid.", "errors": form.errors}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)