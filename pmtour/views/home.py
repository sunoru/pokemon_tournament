# coding=utf-8
from django.shortcuts import redirect
from pmtour.views.utils import (
    get_a_tour,
    get_bracket,
    get_standings,
    ret_tempcont,
)


def home(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
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
            return redirect("bracket/")
        elif request.POST["commit"] == "stop":
            if tour.status > 0:
                tour.end()
            tour.stop()
            tour.save()
    if tour.status > 0:
        bracket_set = get_bracket(request, tour, has_perm)
    else:
        bracket_set = None
    if tour.is_over():
        bracket_set = get_standings(request, tour, has_perm)

    return ret_tempcont(
        request,
        "pmtour/home.html",
        {"tour": tour, "has_perm": has_perm, "bracket": bracket_set}
    )
