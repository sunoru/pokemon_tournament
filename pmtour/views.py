from django.shortcuts import loader, redirect
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.utils import timezone
from pmtour.models import Tournament, Player
from accounts.models import PlayerUser
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


def _get_player_by_request(request, tour):
    if request.user.is_anonymous():
        return None
    try:
        return tour.player_set.get(user=request.user.playeruser)
    except Player.DoesNotExist:
        return None


def _get_bracket(request, tour, has_perm, player=None, turn=None):
    temp = loader.get_template("pmtour/bracket_main.html")
    if turn is None:
        turn = tour.get_current_turn()
    log_set = turn.log_set.all()
    if not has_perm and player is None:
        player = _get_player_by_request(request, tour)
    cont = RequestContext(request, {
        "tour": tour, "has_perm": has_perm, "turn": turn, "logs": log_set, "player": player
    })
    return temp.render(cont)


def _get_standings(request, tour, has_perm, player=None, turn=None):
    temp = loader.get_template("pmtour/standings_main.html")
    if turn is None:
        turn = tour.get_last_turn()
    standings_set = turn.get_standing()
    if standings_set is not None:
        for s in standings_set:
            s["name"] = tour.player_set.get(playerid=s["pid"])
    if not has_perm and player is None:
        player = _get_player_by_request(request, tour)
    elimed = 0
    if tour.on_swiss_over(turn.turn_number):
        elimed = int(tour.get_option("elims"))
    cont = RequestContext(request, {
        "tour": tour, "has_perm": has_perm, "standings": standings_set, "player": player, "elimed": elimed
    })
    return temp.render(cont)


def home(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if has_perm and request.method == "POST":
        if request.POST["commit"] == "ok" and tour.status == -2:
            tour.ready()
            tour.save()
        elif request.POST["commit"] == "start_tour" and tour.status == -1:
            tour.begin()
            tour.save()
        elif request.POST["commit"] == "start":
            if tour.status == 0:
                tour.start(1)
            elif tour.status > 0:
                tour.end()
                tour.start(tour.status + 1)
            tour.save()
        elif request.POST["commit"] == "stop":
            if tour.status > 0:
                tour.end()
            tour.stop()
            tour.save()
    if tour.status > 0:
        bracket_set = _get_bracket(request, tour, has_perm)
    else:
        bracket_set = None
    temp = loader.get_template("pmtour/home.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "bracket": bracket_set})
    return HttpResponse(temp.render(cont))


def check(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)
    turn = tour.get_current_turn()
    data = turn.check_all()
    if len(data) == 0:
        return HttpResponse("All Done")
    else:
        return HttpResponse("\n".join(data))


def bracket(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    bracket_set = None
    if request.method == "POST":
        turn = tour.get_current_turn()
        alog = turn.log_set.get(id=request.POST["log"])
        player = _get_player_by_request(request, tour)
        if has_perm or player == alog.player_a or player is not None and player == alog.player_b:
            commit = request.POST["commit"]
            if commit == "1":
                alog.check(1)
                alog.save()
            elif commit == "2":
                alog.check(2)
                alog.save()
            elif commit == "3":
                alog.check(3)
                alog.save()
            elif commit == "4":
                alog.delete_status()
                alog.save()
        bracket_set = _get_bracket(request, tour, has_perm, player, turn)
    if bracket_set is None and tour.status > 0:
        bracket_set = _get_bracket(request, tour, has_perm)
    temp = loader.get_template("pmtour/bracket.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "bracket": bracket_set})
    return HttpResponse(temp.render(cont))


def standings(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    turn = tour.get_last_turn()
    standing = None
    if turn is not None and turn.type == Tournament.SWISS:
        standing = _get_standings(request, tour, has_perm, None)
    temp = loader.get_template("pmtour/standings.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "standings": standing})
    return HttpResponse(temp.render(cont))


def get_standings(request, tour_id, turn_number):
    tour, has_perm = _get_atour(request, tour_id)
    try:
        turn = tour.turn_set.get(turn_number=turn_number)
    except:
        raise 404
    return HttpResponse(_get_standings(request, tour, has_perm, turn=turn))


def get_bracket(request, tour_id, turn_number):
    tour, has_perm = _get_atour(request, tour_id)
    try:
        turn = tour.turn_set.get(turn_number=turn_number)
    except:
        raise 404
    return HttpResponse(_get_bracket(request, tour, has_perm, turn=turn))


def log(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    temp = loader.get_template("pmtour/log.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def participants(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)
    if has_perm and request.method == "POST":
        if request.POST["commit"] == "exit":
            try:
                player = tour.player_set.get(playerid=request.POST["playerid"])
            except Player.DoesNotExist:
                raise Http404
            player.exit()
            player.save()
    temp = loader.get_template("pmtour/participants.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def add_player(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    if request.method == "POST":
        q = request.POST.getlist("selected_players")
        not_shuffle = request.POST.get("not_shuffle", False)
        if not not_shuffle:
            random.shuffle(q)
        for sp in q:
            pu = PlayerUser.objects.get(player_id=sp)
            Player.create(
                user=pu,
                tournament=tour,
                playerid=tour.players_count() + 1
            )
        return redirect("/%s/participants/" % tour.alias)

    playerusers = PlayerUser.objects.all()
    temp = loader.get_template("pmtour/add_player.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm, "playerusers": playerusers})
    return HttpResponse(temp.render(cont))


# TODO: discussion
def discussion(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    temp = loader.get_template("pmtour/discussion.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


INVALID_LIST = {
    "admin",
    "django_admin",
    "accounts"
}

def settings(request, tour_id):
    tour, has_perm = _get_atour(request, tour_id)
    if not has_perm:
        return _ret_no_perm(request, tour_id)

    status = 0
    tm = str(timezone.localtime(tour.start_time).replace(tzinfo=None)).replace(' ', 'T')
    if request.method == "POST":
        try:
            if request.POST["tour_alias"] != tour.alias:
                if not tour.alias_unique(request.POST["tour_alias"]) or request.POST["tour_alias"] in INVALID_LIST:
                    raise Tournament.InvalidAliasError
            if tour.is_over():
                raise Tournament.TourOverError
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
        except Tournament.InvalidAliasError:
            status = 2
        except Tournament.TourOverError:
            status = 3
        except:
            status = -1
    mj = json.loads(tour.remarks)
    temp = loader.get_template("pmtour/settings.html")
    cont = RequestContext(request, {
        "tour": tour, "has_perm": has_perm, "status": status, "remarks": mj, "starttime": tm
    })
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
