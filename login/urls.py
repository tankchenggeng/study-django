from django.contrib import admin
from django.urls import path
from materialsystem import views

app_name = 'materialsystem'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('register/', views.register),
    path('logout/', views.logout),
]

