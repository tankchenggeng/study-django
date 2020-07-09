## 开发一个物料管理系统

**1. 创建项目**aisystem

```shell
$ django-admin startproject aisystem
```

在根目录下生成了aisystem项目文件夹,里面包含了一个名为manage.py的管理程序,和一个名为aisystem的项目配置文件夹.项目配置文件夹中包含了\__init__.py, settings.py,urls.py,wsgi.py.

**2. 创建应用**

进入项目目录下执行以下命令

```shell
$ python3 manage.py startapp materialsystem
```

在项目文件夹下多了一个materialsystem应用文件夹,内部包含了一个用于数据库迁移的migrations文件夹,以及\__init__.py,admin.py,apps.py,models.py,tests.py,views.py

**3. 添加应用到项目**

将应用名添加到项目配置文件夹下的settings.py中:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'materialsystem',  # 添加应用名在最后
]
```

同时settings.py设置项目数据库:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'aisystem.db'),
    }
}
```

**4. 迁移数据库**

```shell
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

在项目文件夹下会生成一个aisystem.db数据库

**5. 运行**

```shell
$ python3 manage.py runserver
```

终端显示
```shell
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
July 09, 2020 - 08:15:24
Django version 2.2.4, using settings 'aisystem.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

打开浏览器输入http://127.0.0.1:8000/,可以看到django.即表示项目搭建成功.