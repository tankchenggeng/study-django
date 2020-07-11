# encoding=utf-8
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

def login(request):
    print("---------There is aisystem----------- ")
    if request.method == "POST":  # 登录post操作
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        print(user)
        if user:
            auth.login(request, user)
            return redirect('../index/')
        else:
            message = "用户名或密码不正确"
            return render(request, 'login.html', {"message": message,})
    return render(request, "login.html")
  
def register(request):
    if request.method == "POST":  # 登录post操作
        username = request.POST.get("username")
        password = request.POST.get("password")
        repassword = request.POST.get("repassword")
        if username.strip() != username:
            message = "用户名不规范"
            return render(request, 'register.html', {"message": message,})
        elif User.objects.filter(username=username):
            message = "用户已存在"
            return render(request, 'register.html', {"message": message,})
        elif password != repassword:
            message = "两次密码不一致"
            return render(request, 'register.html', {"message": message,})
        else:
            User.objects.create_user(username=username, password=password)
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect('../index/')
    return render(request, "register.html",)
  
def logout(request):
    auth.logout(request)
    return redirect('../login/')