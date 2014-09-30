from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def home(request):
    pass


def login_view(request):
    pass


def create(request):
    pass