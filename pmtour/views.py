from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    pass


def home(request, tour_id):
    return HttpResponse('Hello, world!')


def admin(request, tour_id):
    pass

