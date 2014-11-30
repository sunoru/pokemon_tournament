# coding=utf-8
from django.http import HttpResponse
from pmtour.views.utils import (
    get_a_tour,
    get_bracket,
    get_standings,
    ret_tempcont,
)


def log(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    return ret_tempcont(
        request,
        "pmtour/log.html",
        {"tour": tour, "has_perm": has_perm}
    )


def log_standings(request, tour_id, turn_number):
    tour, has_perm = get_a_tour(request, tour_id)
    try:
        turn = tour.turn_set.get(turn_number=turn_number)
    except:
        raise 404
    return HttpResponse(get_standings(request, tour, has_perm, turn=turn))


def log_bracket(request, tour_id, turn_number):
    tour, has_perm = get_a_tour(request, tour_id)
    try:
        turn = tour.turn_set.get(turn_number=turn_number)
    except:
        raise 404
    return HttpResponse(get_bracket(request, tour, has_perm, turn=turn))
