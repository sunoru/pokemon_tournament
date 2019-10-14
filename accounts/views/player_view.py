# coding=utf-8
import json

from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.models import PlayerUser
from pmtour.models import Tournament, Log


def player_logs(request, player_id):
    try:
        playeruser = PlayerUser.objects.get(player_id=player_id)
    except PlayerUser.DoesNotExist:
        raise Http404
    logs = {Tournament.SWISS: {u"轮空": []}, Tournament.SINGLE: {u"轮空": []}}
    players = playeruser.player_set.all()
    for player in players:
        for log in player.player_a_log.all():
            if log.player_b is None:
                name = u"轮空"
            else:
                name = log.player_b.user.name
            if name not in logs[log.turn.type]:
                logs[log.turn.type][name] = []
            logs[log.turn.type][name].append({"status": log.status})
        for log in player.player_b_log.all():
            name = log.player_a.user.name
            if name not in logs[log.turn.type]:
                logs[log.turn.type][name] = []
            logs[log.turn.type][name].append({"status": Log.STATUS_DICT.get(log.status)})
    if request.user.is_staff or request.user.playeruser == playeruser:
        pass
    return HttpResponse(json.dumps(logs), content_type="json")


def player_view(request, player_id):
    try:
        playeruser = PlayerUser.objects.get(player_id=player_id)
    except PlayerUser.DoesNotExist:
        raise Http404

    players = playeruser.player_set.all()
    no1 = []
    no2 = []
    top4 = []
    top8 = []
    tour_others = []
    for x in players:
        if x.standing == 1:
            no1.append(x.tournament)
        elif x.standing == 2:
            no2.append(x.tournament)
        elif x.standing <= 4:
            top4.append(x.tournament)
        elif x.standing <= 8:
            top8.append(x.tournament)
        else:
            tour_others.append(x.tournament)
    render_dict = {
        "playeruser": playeruser,
        "used_name": ', '.join({x.name for x in players}),
        "played_tours_count": len(players),
        "no1": no1,
        "no2": no2,
        "top4": top4,
        "top8": top8,
        "tour_others": tour_others,
        "introduction": playeruser.get_info("introduction")
    }
    if request.user.is_staff or request.user.playeruser == playeruser:
        pass

    return render_to_response("accounts/player_view.html", context_instance=RequestContext(request, render_dict))
