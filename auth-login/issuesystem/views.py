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
