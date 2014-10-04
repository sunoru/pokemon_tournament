from django.shortcuts import loader, redirect
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.utils import timezone
from pmtour.models import Tournament, Player
from accounts.models import PlayerUser
import datetime
import json
import random


def _get_tour(tour_id):
    try:
        tour = Tournament.objects.get(alias=tour_id)
    except Tournament.DoesNotExist:
        try:
            tour = Tournament.objects.get(tour_id=tour_id)
        except Tournament.DoesNotExist:
            raise Http404
    return tour


def _get_perm(request, tour):
    return not request.user.is_anonymous() and request.user.playeruser in tour.admins.all()


def _ret_no_perm(request, tour_id):
    temp = loader.get_template("pmtour/no_perm.html")
    cont = RequestContext(request, {"tour": _get_tour(tour_id)})
    return HttpResponse(temp.render(cont))


def _get_atour(request, tour_id):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    tour.refresh()

    return tour, has_perm


def home(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if has_perm and request.method == "POST":
        if request.POST["commit"] == "ok" and tour.status == -2:
            tour.status = -1
            tour.save()
        elif request.POST["commit"] == "start_tour" and tour.status == -1:
            t = timezone.now()
            tour.start_time = t.strftime("%Y-%m-%dT%H:%M:%S%z")
            tour.status = 0
            tour.save()
        elif request.POST["commit"] == "start" and tour.status >= 0:
            tour.start(tour.status + 1)
            tour.save()
    temp = loader.get_template("pmtour/home.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def participants(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    temp = loader.get_template("pmtour/participants.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def add_player(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    if request.method == "POST":
        q = request.POST.getlist("selected_players")
        random.shuffle(q)
        for sp in q:
            pu = PlayerUser.objects.get(player_id=sp)
            Player.objects.create(
                user=pu,
                tournament=tour,
                playerid=tour.players_count() + 1
            )
        return redirect("/%s/participants/" % tour.alias)

    playerusers = PlayerUser.objects.all()
    temp = loader.get_template("pmtour/add_player.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "playerusers": playerusers})
    return HttpResponse(temp.render(cont))


def settings(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    status = 0
    tm = str(timezone.localtime(tour.start_time).replace(tzinfo=None)).replace(' ', 'T')
    if request.method == "POST":
        print request.POST
        try:
            if request.POST["tour_alias"] != tour.alias and not tour.alias_unique(request.POST["tour_alias"]):
                status = 2
                raise Exception
            tour.name = request.POST["tour_name"]
            tour.alias = request.POST["tour_alias"]
            tour.tournament_type = request.POST["tour_type"]
            tour.start_time = request.POST["tour_start_time"]  # TODO: time zone settings
            tm = request.POST["tour_start_time"]
            tour.description = request.POST["tour_description"]
            if "tour_turns" in request.POST:
                tour.set_option("turns", request.POST["tour_turns"])
            if "tour_elims" in request.POST:
                tour.set_option("elims", request.POST["tour_elims"])
            tour.save()
            status = 1
        except Exception as e:
            print e
            status = -1
    mj = json.loads(tour.remarks)
    temp = loader.get_template("pmtour/settings.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "status": status, "remarks": mj, "starttime": tm})
    return HttpResponse(temp.render(cont))


def delete(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)
    tour.delete()
    return redirect("/accounts")


def get_turns(request, tour_id):
    tour = _get_tour(tour_id)
    if tour.tournament_type == Tournament.SWISS:
        return HttpResponse(_get_turns(tour.players_count()))
    elif tour.tournament_type == Tournament.SWISS_PLUS_SINGLE:
        return HttpResponse(_get_turns_2(tour.players_count()))
    else:
        raise Http404


def get_elims(request, tour_id):
    tour = _get_tour(tour_id)
    if tour.tournament_type == Tournament.SWISS_PLUS_SINGLE:
        return HttpResponse(_get_elims(tour.players_count()))
    else:
        raise Http404


def _get_turns(number):
    if number < 6:
        return -1
    elif 6 <= number <= 8:
        return 3
    elif number <= 16:
        return 4
    elif number <= 32:
        return 5
    elif number <= 64:
        return 6
    elif number <= 128:
        return 7
    elif number <= 256:
        return 8
    else:
        return -1


def _get_turns_2(number):
    if number < 8:
        return -1
    elif number == 8:
        return 3
    elif number <= 12:
        return 4
    elif number <= 32:
        return 5
    elif number <= 64:
        return 6
    elif number <= 128:
        return 7
    elif number <= 226:
        return 8
    elif number <= 409:
        return 9
    elif number > 409:
        return 10


def _get_elims(number):
    if number < 8:
        return -1
    elif number == 8:
        return 0
    elif number <= 20:
        return 4
    elif number > 21:
        return 8