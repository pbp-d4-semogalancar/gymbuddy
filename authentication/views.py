from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from django.contrib.auth.models import User

def register_user(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('authentication:login_user')
    context = {
        'form':form
    }
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            datetime_now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            response.set_cookie('last_login', datetime_now_str)
            return response

    else:
        form = AuthenticationForm(request)
    context = {
        'form': form
    }
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('authentication:login_user'))
    response.delete_cookie('last_login')
    return response

# UNTUK API

@csrf_exempt
def register_user_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password1 = data.get('password1', '').strip()
            password2 = data.get('password2', '').strip()

            if not username or not password1:
                return JsonResponse({
                    "status": False,
                    "message": "Username and password cannot be empty."
                }, status=400)

            if password1 != password2:
                return JsonResponse({
                    "status": False,
                    "message": "Passwords do not match."
                }, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username already exists."
                }, status=400)
            
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "User created successfully!"
            }, status=201)
        
        except json.JSONDecodeError:
             return JsonResponse({"status": False, "message": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)
    
    else:
        return JsonResponse({"status": False, "message": "Invalid request method."}, status=400)

@csrf_exempt
def login_user_api(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = {
                "username": user.username,
                "status": True,
                "user_id": user.id,
                "message": "Login successfully!"
            }
            return JsonResponse(context, status=200)
        else:
            context = {
                "status": False,
                "message": "Login gagal, akun dinonaktifkan."
            }
            return JsonResponse(context, status=401)

    else:
        context = {
            "status": False,
            "message": "Login gagal, periksa kembali email atau kata sandi."
        }
        return JsonResponse(context, status=401)


def logout_user_api(request):
    username = request.user.username

    try:
        logout(request)
        context = {
            "username": username,
            "status": True,
            "message": "Logout berhasil!"
        }
        return JsonResponse(context, status=200)
    except:
        context = {
        "status": False,
        "message": "Logout gagal."
        }
        return JsonResponse(context, status=401)
