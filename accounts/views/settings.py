# coding=utf-8
from accounts.models import PlayerUser
from django.shortcuts import redirect, loader
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template import RequestContext
from django.http import HttpResponse, Http404


@login_required
def player_setting(request, player_id):
    try:
        playeruser = PlayerUser.objects.get(player_id=player_id)
    except PlayerUser.DoesNotExist:
        return redirect("/accounts/")
    if request.user != playeruser.user and not request.user.is_staff:
        return redirect("/accounts/")
    if request.method == "POST":
        playeruser.name = request.POST["player_name"]
        playeruser.birthday = timezone.datetime.strptime(request.POST["player_birthday"], "%Y-%m-%d").date()
        playeruser.save()
        return redirect(request.POST["obj_url"])
    obj_url = request.META.get('HTTP_REFERER', "/")
    player_set = playeruser.player_set.all()
    temp = loader.get_template("accounts/player_setting.html")
    cont = RequestContext(request, {"playeruser": playeruser, "obj_url": obj_url, "player_set": player_set})
    return HttpResponse(temp.render(cont))


@login_required
def edit(request):
    if not request.user.is_staff:
        raise Http404
    temp = loader.get_template("accounts/edit.html")
    cont = RequestContext(request, {"playerusers": PlayerUser.objects.all()})
    return HttpResponse(temp.render(cont))

