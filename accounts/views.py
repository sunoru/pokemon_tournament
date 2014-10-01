from django.shortcuts import render_to_response, redirect, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponse
import pmtour.models


def login_view(request):
    mes = 0
    if request.method == "POST":
        username = request.POST["log"]
        password = request.POST["pwd"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.POST.get("next", "/"))
            else:
                mes = 1
        else:
            mes = 2
    temp = loader.get_template("login.html")
    cont = RequestContext(request, {"mes": mes, "next": request.GET.get("next", "/")})
    return HttpResponse(temp.render(cont))


def logout_view(request):{% extends "base.html" %}
{% block title %}个人中心{% endblock %}
{% block body %}
    <p id="new_tour"><a href="create">新建比赛</a></p>
{% endblock %}

    logout(request)
    return redirect(request.GET.get("next", "/"))


@login_required
def home(request):
    return render_to_response("accounts.html", context_instance=RequestContext(request))


@login_required
def create(request):
    tour = pmtour.models.Tournament.create()
    return redirect("/%s/admin/" % tour.alias)
