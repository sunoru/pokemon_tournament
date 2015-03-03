from django.shortcuts import render_to_response, redirect, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponse, Http404
from accounts.models import PlayerUser
import pmtour.models
import datetime


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
    temp = loader.get_template("accounts/login.html")
    cont = RequestContext(request, {"mes": mes, "next": request.GET.get("next", "/")})
    return HttpResponse(temp.render(cont))


def logout_view(request):
    logout(request)
    return redirect(request.GET.get("next", "/"))


@login_required
def home(request):
    return render_to_response("accounts/accounts.html", context_instance=RequestContext(request, {
        'tours': [
            x for x in pmtour.models.Tournament.objects.all()
            if x.status >= 0 or x.status == -3 or x in request.user.playeruser.tournament_set.all()
        ]
    }))


@login_required
def create(request):
    if not request.user.is_staff:
        raise Http404
    tour = pmtour.models.Tournament.create(request.user.playeruser)
    return redirect("/%s/" % tour.alias)


@login_required
def load(request):
    if not request.user.is_staff:
        raise Http404
    status = 0
    if request.method == "POST":
        datas = request.POST.get("import_data", "")
        if datas == "":
            status = -1
        else:
            #try:
                tour = pmtour.models.Tournament.loaddata(datas, request.user.playeruser)
                return redirect("/%s/" % tour.alias)
            # except pmtour.models.Tournament.LoaddataError:
            #     status = -1
    temp = loader.get_template("accounts/load.html")
    cont = RequestContext(request, {"status": status})
    return HttpResponse(temp.render(cont))


@login_required
def edit(request):
    if not request.user.is_staff:
        raise Http404
    temp = loader.get_template("accounts/edit.html")
    cont = RequestContext(request, {"playerusers": PlayerUser.objects.all()})
    return HttpResponse(temp.render(cont))


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
        playeruser.birthday = datetime.datetime.strptime(request.POST["player_birthday"], "%Y-%m-%d").date()
        playeruser.save()
        return redirect(request.POST["obj_url"])
    obj_url = request.META.get('HTTP_REFERER', "/")
    player_set = playeruser.player_set.all()
    temp = loader.get_template("accounts/player_setting.html")
    cont = RequestContext(request, {"playeruser": playeruser, "obj_url": obj_url, "player_set": player_set})
    return HttpResponse(temp.render(cont))

