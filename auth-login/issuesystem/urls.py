from django.contrib import admin
from django.urls import path
from issuesystem import views

app_name = 'issuesystem'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
]
