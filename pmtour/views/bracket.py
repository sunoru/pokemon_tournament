# coding=utf-8
from pmtour.views.utils import (
    get_a_tour,
    get_bracket,
    get_player_by_request,
    ret_tempcont,
)
from pmtour.models import (
    LOG_STATUS_A_WIN,
    LOG_STATUS_B_WIN,
    LOG_STATUS_TIE,
    LOG_STATUS_BOTH_LOSE
)


def bracket(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    bracket_set = None
    if request.method == "POST":
        turn = tour.get_current_turn()
        alog = turn.log_set.get(id=request.POST["log"])
        player = get_player_by_request(request, tour)
        if has_perm or player == alog.player_a or player is not None and player == alog.player_b:
            commit = request.POST["commit"]
            if commit == "1":
                alog.check_status(LOG_STATUS_A_WIN)
                alog.save()
            elif commit == "2":
                alog.check_status(LOG_STATUS_B_WIN)
                alog.save()
            elif commit == "3":
                alog.check_status(LOG_STATUS_TIE)
                alog.save()
            elif commit == "4":
                alog.delete_status()
                alog.save()
            elif commit == "5":
                alog.check_status(LOG_STATUS_BOTH_LOSE)
                alog.save()
        bracket_set = get_bracket(request, tour, has_perm, player, turn)
    if bracket_set is None and tour.status > 0:
        bracket_set = get_bracket(request, tour, has_perm)
    return ret_tempcont(
        request,
        "pmtour/bracket.html",
        {"tour": tour, "has_perm": has_perm, "bracket": bracket_set}
    )
