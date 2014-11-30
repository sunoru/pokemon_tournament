# coding=utf-8
from pmtour.models import Tournament
from pmtour.views.utils import (
    get_a_tour,
    get_standings,
    ret_tempcont,
)


def standings(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    turn = tour.get_last_turn()
    standing = None
    if turn is not None and (turn.type == Tournament.SWISS or tour.is_over()):
        standing = get_standings(request, tour, has_perm, None)
    return ret_tempcont(
        request,
        "pmtour/standings.html",
        {"tour": tour, "has_perm": has_perm, "standings": standing}
    )

