# encoding=utf-8
from django.shortcuts import render, redirect
from materialsystem import models
from materialsystem import forms

def login_required(func):
    def view(request, *args, **kwargs):
        username = request.session.get('username', None)
        if username:
            return func(request, *args, **kwargs)
        else:
            return login(request, *args, **kwargs)
    return view

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "POST":  # 登录post操作
        userform = forms.UserForm(request.POST)
        user = request.POST
        username = user.get("username")
        try:
            password = models.User.objects.get(username=username).password
        except:
            message = "用户不存在"
            return render(request, 'login.html', {"message": message, 
                                                  "userform": userform,})
        if user.get("password") == password: # 提交密码正确
            request.session["username"] = username
            return redirect('../index/')
        else:
            message = "密码不正确"
            return render(request, 'login.html', {"message": message, 
                                                  "userform": userform,})
    else:
        userform = forms.UserForm()
    return render(request, "login.html", {"userform": userform,})
  
def register(request):
    if request.method == "POST":  # 登录post操作
        userform = forms.UserForm(request.POST)
        user = request.POST
        username = user.get("username")
        password = user.get("password")
        repassword = user.get("repassword")
        if username.strip() != username:
            message = "用户名不规范"
            return render(request, 'register.html', {"message": message, 
                                                     "userform": userform,})
        elif models.User.objects.filter(username=username):
            message = "用户已存在"
            return render(request, 'register.html', {"message": message, 
                                                     "userform": userform,})
        elif password != repassword:
            print(userform)
            message = "两次密码不一致"
            return render(request, 'register.html', {"message": message, 
                                                     "userform": userform,})
        else:
            userform.save()
            request.session["username"] = username
            return redirect('../index/')
    else:
        userform = forms.UserForm()
    return render(request, "register.html", {"userform": userform,})
  
def logout(request):
    del request.session["username"]
    return redirect('../login/')
