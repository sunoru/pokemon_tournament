# coding=utf-8
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout


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
    return render(request, "accounts/login.html", {
        "mes": mes, "next": request.GET.get("next", "/")
    })


def logout_view(request):
    logout(request)
    return redirect(request.GET.get("next", "/"))

