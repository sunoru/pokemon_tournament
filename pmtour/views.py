from django.shortcuts import loader, redirect
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.utils import timezone
from pmtour.models import Tournament, Player
from accounts.models import PlayerUser
import json


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
    return (not request.user.is_anonymous() and request.user.playeruser in tour.admins.all())


def _ret_normal(request, tour_id, aname):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    temp = loader.get_template("pmtour/%s.html" % aname)
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def _ret_no_perm(request, tour_id):
    temp = loader.get_template("pmtour/no_perm.html")
    cont = RequestContext(request, {"tour": _get_tour(tour_id)})
    return HttpResponse(temp.render(cont))


def home(request, tour_id):
    print tour_id
    return _ret_normal(request, tour_id, "home")


def participants(request, tour_id):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    temp = loader.get_template("pmtour/participants.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def add_player(request, tour_id):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    if request.method == "POST":
        for sp in request.POST.getlist("selected_players"):
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


def player_setting(request, tour_id, playerid):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    if not has_perm:
        return _ret_no_perm(request, tour_id)
    try:
        player = tour.player_set.get(playerid=playerid)
    except Player.DoesNotExist:
        return redirect("/%s/participants/" % tour.alias)
    temp = loader.get_template("pmtour/player_setting.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "player": player})
    return HttpResponse(temp.render(cont))


def settings(request, tour_id):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    status = 0
    mj = json.loads(tour.remarks)
    tm = str(tour.start_time.astimezone(timezone.get_current_timezone()).isoformat())[:-6] #
    if request.method == "POST":
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
                mj["turns"] = request.POST["tour_turns"]
            if "tour_elims" in request.POST:
                mj["elims"] = request.POST["tour_elims"]
            tour.remarks = json.dumps(mj)
            tour.save()
            status = 1
        except Exception as e:
            print e
            status = -1
    temp = loader.get_template("pmtour/settings.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "status": status, "remarks": mj, "starttime": tm})
    return HttpResponse(temp.render(cont))


def delete(request, tour_id):
    tour = _get_tour(tour_id)
    tour.delete()
    return redirect("/accounts")


def get_turns(request, tour_id):
    try:
        tour = _get_tour(tour_id)
        return HttpResponse(_get_turns(tour))
    except:
        raise Http404

def _get_turns(tour):
    if tour.players_count in xrange(6, 9):
        return 3
    elif tour.players_count in xrange(9, 17):
        return 4
    elif tour.players_count in xrange(17, 33):
        return 5
    elif tour.players_count in xrange(33, 65):
        return 6
    elif tour.players_count in xrange(65, 129):
        return 7
    elif tour.players_count in xrange(129, 257):
        return 8
    else:
        return -1
