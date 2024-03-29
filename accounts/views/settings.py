# coding=utf-8
from accounts.models import PlayerUser
from django.shortcuts import redirect, loader
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, Http404


@login_required
def player_setting(request, player_id):
    try:
        playeruser = PlayerUser.objects.get(player_id=player_id)
    except PlayerUser.DoesNotExist:
        return redirect("/accounts/")
    if request.user != playeruser.user and not request.user.is_staff:
        return redirect("/accounts/")
    status = 0
    if request.method == "POST":
        try:
            playeruser.name = request.POST["player_name"]
            playeruser.birthday = timezone.datetime.strptime(request.POST["player_birthday"], "%Y-%m-%d").date()
            playeruser.set_info("introduction", request.POST["player_introduction"])
            playeruser.save()
            status = 1
        except:
            status = 2
    temp = loader.get_template("accounts/player_setting.html")
    cont = {
        "playeruser": playeruser,
        "introduction": playeruser.get_info("introduction"),
        "status": status
    }
    return HttpResponse(temp.render(cont, request))


@login_required
def edit(request):
    if not request.user.is_staff:
        raise Http404
    temp = loader.get_template("accounts/edit.html")
    cont = {"playerusers": PlayerUser.objects.all()}
    return HttpResponse(temp.render(cont, request))
