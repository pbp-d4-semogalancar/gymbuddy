from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from django.contrib.auth.models import User

# Tanpa AJAX, render biasa
@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('authentication:login_user'))
    response.delete_cookie('last_login')
    return response

# Dengan AJAX

@csrf_exempt
def register_user_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']

        # Check if the passwords match
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            context = {
                "username": request.user.username,
                "status": False,
                "message": "Username already exists."
            }
            return JsonResponse(context, status=400)
        
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        context = {
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }
        return JsonResponse(context, status=200)
    
    else:
        context = {
            "status": False,
            "message": "Invalid request method."
        }
        return JsonResponse(context, status=400)

@csrf_exempt
def login_user_ajax(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            context = {
                "username": user.username,
                "status": True,
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

@csrf_exempt
def logout_user_ajax(request):
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
