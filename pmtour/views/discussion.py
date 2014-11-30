# coding=utf-8
from pmtour.views.utils import (
    get_a_tour,
    ret_tempcont,
)


# TODO: discussion
def discussion(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    return ret_tempcont(
        request,
        "pmtour/discussion.html",
        {"tour": tour, "has_perm": has_perm}
    )

