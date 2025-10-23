from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.template.loader import render_to_string


from .models import Thread
from .forms import ThreadForm, CustomUserCreationForm


# ==============================================================================
#                      HELPER FUNCTION
# ==============================================================================
def is_staff_user(user):
    """Mengecek apakah user terautentikasi dan merupakan admin/staff."""
    return user.is_authenticated and user.is_staff


# ==============================================================================
#                      FITUR OTENTIKASI
# ==============================================================================
class SignUpView(CreateView):
    """Menangani pendaftaran akun baru (registrasi)."""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class CustomLoginView(LoginView):
    template_name = 'login.html'  # pakai template login HTML custom
    authentication_form = AuthenticationForm

# logout juga bisa dibuat:
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('community:login')  # setelah logout, balik ke login


# ==============================================================================
#                      FITUR KOMUNITAS - SISI USER
# ==============================================================================

# [R] - READ: Menampilkan Semua Thread (Halaman Komunitas)
def show_community(request):
    threads = Thread.objects.all().order_by('-date_created')
    
    # LOGIC FILTER BARU
    filter_type = request.GET.get('filter')
    
    if filter_type == 'my' and request.user.is_authenticated:
        # Filter hanya thread milik user yang sedang login
        threads = threads.filter(user=request.user)
    elif filter_type == 'all' or not request.user.is_authenticated:
        # Tampilkan semua jika filter 'all' atau jika user belum login
        filter_type = 'all'

    # Jika filter_type == 'all' atau user belum login, threads tetap all().

    form = ThreadForm()
    context = {
        'threads': threads,
        'form': form,
        'user_is_admin': is_staff_user(request.user),
        # Kirimkan filter_type saat ini ke template untuk styling tombol
        'current_filter': filter_type,
    }
    return render(request, 'community/community_page.html', context)

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

    # Hanya pemilik thread yang boleh edit
    if thread.user != request.user:
        # Mengembalikan JSON jika terjadi kegagalan otorisasi
        return JsonResponse({'success': False, 'error': 'Anda tidak memiliki izin untuk mengedit thread ini.'}, status=403)

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            updated_thread = form.save() # Simpan perubahan

            # FIX: Deteksi AJAX dan kembalikan JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'title': updated_thread.title,
                    'content': updated_thread.content,
                    'thread_id': updated_thread.id
                })

            # FALLBACK: Jika non-AJAX (tidak terjadi jika script berjalan), lakukan redirect
            return redirect('community:show_community')

        else:
            # Mengembalikan error validasi form dalam JSON jika request adalah AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': form.errors}, status=400)

    else:
        form = ThreadForm(instance=thread)

    # Mengembalikan form HTML jika request adalah GET
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

def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('community:login'))  # ke halaman login HTML custom
    return redirect(reverse('community:show_community')) 
