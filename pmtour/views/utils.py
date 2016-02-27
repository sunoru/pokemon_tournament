# coding=utf-8
from django.http import HttpResponse, Http404
from django.shortcuts import loader
from django.template import RequestContext
import json
from pmtour.models import Tournament, Player


def get_tour(tour_id):
    try:
        tour = Tournament.objects.get(alias=tour_id)
    except Tournament.DoesNotExist:
        try:
            tour = Tournament.objects.get(tour_id=tour_id)
        except Tournament.DoesNotExist:
            raise Http404
    return tour


def get_perm(request, tour):
    return request.user.is_staff or not request.user.is_anonymous() and request.user.playeruser in tour.admins.all()


def get_a_tour(request, tour_id):
    tour = get_tour(tour_id)
    has_perm = get_perm(request, tour)
    tour.refresh()
    return tour, has_perm


def get_player_by_request(request, tour):
    if request.user.is_anonymous():
        return None
    try:
        return tour.player_set.get(user=request.user.playeruser)
    except Player.DoesNotExist:
        return None


def get_player_printable(sts, player):
    if player is None:
        return ""
    for q in sts:
        if q["pid"] == player.playerid:
            return "%s(%s) (%s) %s" % (player.name, player.user.name, q["match"], q["score"])
    return ""


def get_bracket(request, tour, has_perm, player=None, turn=None):
    temp = loader.get_template("pmtour/bracket_main.html")
    if turn is None:
        turn = tour.get_current_turn()
    log_set = tmp_log_set = turn.log_set.all()
    if not has_perm and player is None:
        player = get_player_by_request(request, tour)
    sts = turn.get_standing()
    if sts is not None:
        log_set = []
        for logs in tmp_log_set:
            log_set.append({
                "player_a": get_player_printable(sts, logs.player_a),
                "player_b": get_player_printable(sts, logs.player_b),
                "status": logs.status
            })
    cont = RequestContext(request, {
        "tour": tour, "has_perm": has_perm, "turn": turn, "logs": log_set, "player": player
    })
    return temp.render(cont)


def get_standings(request, tour, has_perm, player=None, turn=None):
    temp = loader.get_template("pmtour/standings_main.html")
    if turn is None:
        turn = tour.get_last_turn()
    if turn is None:
        cont = RequestContext(request, {
            "tour": tour, "has_perm": has_perm, "standings": None
        })
        return temp.render(cont)
    standings_set = turn.get_standing()
    if standings_set is not None:
        for s in standings_set:
            p = tour.player_set.get(playerid=s["pid"])
            s["name"] = p.name
    if not has_perm and player is None:
        player = get_player_by_request(request, tour)
    elimed = 0
    if tour.on_swiss_over(turn.turn_number):
        elimed = tour.get_option("elims")
    cont = RequestContext(request, {
        "tour": tour, "has_perm": has_perm, "standings": standings_set, "player": player, "elimed": elimed
    })
    return temp.render(cont)


def ret_no_perm(request, tour_id):
    temp = loader.get_template("pmtour/no_perm.html")
    cont = RequestContext(request, {"tour": get_tour(tour_id)})
    return HttpResponse(temp.render(cont))


def ret_tempcont(request, template_path, context_dict):
    temp = loader.get_template(template_path)
    cont = RequestContext(request, context_dict)
    return HttpResponse(temp.render(cont))


def ret_json_data(data):
    return HttpResponse(json.dumps(data))
