# coding=utf-8
from django.http import Http404
from django.shortcuts import render_to_response
from accounts.models import PlayerUser

def player_view(request, player_id):
    try:
        playeruser = PlayerUser.objects.get(player_id=player_id)
    except PlayerUser.DoesNotExist:
        raise Http404

    players = playeruser.player_set.all()
    render_dict = {
        "playeruser": playeruser,
        "used_name": ', '.join({x.name for x in players}),
        "played_tours_count": len(players),
        "no1": [x.tournament.name for x in players if x.standing == 1],
        "no2": [x.tournament.name for x in players if x.standing == 2],
        "top4": [x.tournament.name for x in players if 3 <= x.standing <= 4],
        "top8": [x.tournament.name for x in players if 5 <= x.standing <= 8],
        "tour_others": [x.tournament.name for x in players if x.standing > 8],
    }
    if request.user.is_staff or request.user.playeruser == playeruser:
        pass

    return render_to_response("accounts/player_view.html", render_dict)
