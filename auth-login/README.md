## 使用Django的Auth模块实现多应用共用User
继续以最基本的注册登录进入网页为例,子应用issuesystem
```shell
$ python3 manage.py startapp issuesystem
```

**1. 设置模板文件路径**

由于是一个项目多个应用,我们直接在项目文件夹aisystem下新建templates模板文件夹.打开项目配置文件夹aisystem下的setting.py,设置templates路径:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 设置公共templates路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

```
由于设置了templates路径,在视图函数中使用的模板文件*.html都会优先在此路径下寻找模板文件,所以我们将所有应用共用的模板文件直接放在templates目录下.
在templates目录下新建3个模板文件:
1. login.html(登录界面)
2. index.html(主页)
3. register.html(注册界面)

对于应用issuesystem的专用模板文件,在templates下新建一个issuesystem文件夹

**2. 添加app并设置未登录跳转**

打开项目配置文件夹aisystem下的setting.py,添加issuesystem:
```python
INSTALLED_APPS = [
    # 在最后添加
    'issuesystem',
]

LOGIN_URL = '/login/'  # 配置未登录访问需登录界面的跳转
```

**3. 设置路由分发和视图**

打开项目配置文件夹,新建urls.py
添加以下代码:
```python
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from aisystem import views

urlpatterns = [
    path('', views.login),
    path('login/', views.login),
    path('index/', views.index),
    path('register/', views.register),
    path('logout/', views.logout),
    path('issuesystem/', include('issuesystem.urls')),
]

```

新建views.py,添加以下代码(使用auth模块完成注册登录登出)
```python
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
    if request.method == "POST":  # 登录post操作
        username = request.POST.get("username")
        password = request.POST.get("password")
        # 对于密文存储的密码,需要依赖auth.authenticate进行验证
        # 明文密码则直接访问数据库验证
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)  # 登录
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
```
auth.authenticate(username=username, password=password)验证成功时返回user,否则返回None
auth.login(request, user)将user信息注册到session中,登录成功后,就可以访问被login_required装饰的index视图,如果未登录,网页则会重定向到settings.py中设置的LOGIN_URL配置的网页
`LOGIN_URL = '/login/'  # 配置未登录访问需登录界面的跳转`
User.objects.create_user(username=username, password=password)创建的是密文密码,
User.objects.create(username=username, password=password)创建的是明文密码,User模x型支持明文密文两种方式共存.
auth.logout(request)登出,会将session中的user信息删除.

**4. 项目用户注册登录模板文件**
模板文件如下
login.html
```html
<div style="text-align: center;">
    <form action="/login/" method="post">
        {% csrf_token %} <!-- 跨域请求，-->
        <div class="form-group">
            <label>用户名:</label>
            <input type="text" name='username' class="form-control" required>
        </div>
        <div class="form-group">
            <label>密码：</label>
            <input type="password" name='password' class="form-control" required>
        </div>
        <a href="/register/" ><ins>新用户注册</ins></a>
        <input type="submit" name="提交", value="登录">
    </form>
    {% if message %}
    <div class="alert alert-warning">{{ message }}</div>
     {% endif %}
</div>
```

register.html
```html
<div style="text-align: center;">
    <form action="/register/" method="post">
        {% csrf_token %} <!-- 跨域请求，-->
        <div class="form-group">
            <label>用户名:</label>
            <input type="text" name='username' class="form-control" required>
        </div>
        <div class="form-group">
            <label>密码：</label>
            <input type="password" name='password' class="form-control" required>
        </div>
        <div class="form-group">
            <label>验证密码：</label>
            <input type="password" name='repassword' class="form-control" required>
        </div>
        <input type="submit" name="提交", value="注册">
        <a href="/login/" ><ins>用户登录</ins></a>
    </form>
    {% if message %}
    <div class="alert alert-warning">{{ message }}</div>
     {% endif %}
</div>
```

index.html
```html
<h1>主页</h1>
<a href="/logout/" ><ins>登出</ins></a>
<a href="/issuesystem/index/" ><ins>Issue管理系统</ins></a>
```
主页提供了进入应用的入口

**5. 应用配置**

打开issuesystem应用目录,删除test.py,增加urls.py
urls.py添加以下代码:
```python
from django.contrib import admin
from django.urls import path
from issuesystem import views

app_name = 'issuesystem'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
]
```

打开issuesystem应用目录,views.py编写以下内容:
```python
# encoding=utf-8
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os

app_name = 'issuesystem'

def apptemplates(template):
    return os.path.join(app_name, template)

# Create your views here.
@login_required
def index(request):
    return render(request, apptemplates('index.html'))
```

编写issuesystem的主页模板index.html,打开项目目录下templates/issuesystem,添加index.html文件
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Issue System</title>
</head>
<body>
<h1>主页</h1>
<a href="/logout/" ><ins>登出</ins></a>
</body>
</html>
```

现在开启服务就可以注册登录及进入主页了
