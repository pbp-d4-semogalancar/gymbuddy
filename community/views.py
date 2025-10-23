import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count, OuterRef, Subquery
from django.contrib.auth.models import User
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .models import Thread, Reply
from .forms import ThreadForm, ReplyForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def community_page_view(request):
    sort_option = request.GET.get('sort', 'newest')
    top_reply_subquery = Reply.objects.filter(thread=OuterRef('pk')).order_by('-date_created')
    threads = Thread.objects.annotate(
        reply_count=Count('replies'),
        top_reply_content=Subquery(top_reply_subquery.values('content')[:1]),
        top_reply_user=Subquery(top_reply_subquery.values('user__username')[:1]),
    )

    if sort_option == 'most_replied':
        threads = threads.order_by('-reply_count', '-date_created')
    elif sort_option == 'oldest':
        threads = threads.order_by('date_created')
    else:
        threads = threads.order_by('-date_created')
        
    context = {'threads': threads, 'current_sort': sort_option, 'thread_form': ThreadForm()}
    return render(request, 'community/community_page.html', context)

def thread_detail_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    top_level_replies = thread.replies.filter(parent__isnull=True).order_by('date_created')
    reply_form = ReplyForm()
    return render(request, 'community/thread_detail.html', {'thread': thread, 'replies': top_level_replies, 'reply_form': reply_form})

# [C] - CREATE: Membuat Thread Baru via AJAX
@login_required
@csrf_exempt
def create_thread_ajax(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            new_thread = form.save(commit=False)
            new_thread.user = request.user
            new_thread.save()

            return JsonResponse({
                'status': 'success',
                'thread_id': new_thread.id,
                'thread_title': new_thread.title,
                'thread_content': new_thread.content,
                'thread_user': new_thread.user.username,
                'date_created': new_thread.date_created.strftime('%b %d, %Y'),
                'is_owner': True,
            }, status=201)

        # Form tidak valid
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return HttpResponse(status=405)  # Method Not Allowed


# [U] - UPDATE: Mengedit Thread Milik Sendiri
@login_required
def edit_thread_user(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    # Hanya pemilik thread yang bisa edit
    if thread.user != request.user:
        return HttpResponse("Anda tidak memiliki izin untuk mengedit thread ini.", status=403)

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('community:community_page')
    else:
        form = ThreadForm(instance=thread)

    return render(request, 'community/edit_thread.html', {'form': form, 'thread': thread})


# [D] - DELETE: Menghapus Thread Milik Sendiri
@login_required
@require_POST
def delete_thread_user(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if thread.user != request.user:
        return JsonResponse({"status": "error", "message": "Anda tidak memiliki izin untuk menghapus thread ini."}, status=403)

    thread.delete()
    return JsonResponse({'status': 'success', 'message': 'Thread berhasil dihapus.'}, status=200)

@login_required
def add_reply_ajax(request, thread_id):
    if request.method == 'POST':
        thread = get_object_or_404(Thread, id=thread_id)
        data = json.loads(request.body)
        form = ReplyForm({'content': data.get('content')})
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user; reply.thread = thread
            parent_id = data.get('parent_id')
            if parent_id:
                try: reply.parent = Reply.objects.get(id=parent_id)
                except Reply.DoesNotExist: pass
            reply.save()
            html_reply = render_to_string('community/reply.html', {'reply': reply, 'user': request.user})
            return JsonResponse({'status': 'success', 'html_reply': html_reply, 'parent_id': parent_id}, status=201)
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def edit_reply_ajax(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user != reply.user: return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    if request.method == 'POST':
        data = json.loads(request.body)
        form = ReplyForm(data, instance=reply)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'content': reply.content})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@login_required
def delete_reply_ajax(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user != reply.user: return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    if request.method == 'POST':
        reply.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)
class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'community/register.html'