# coding=utf-8
from django.http import HttpResponse
from django.shortcuts import redirect
from pmtour.views.utils import (
    get_a_tour,
    ret_no_perm,
)


def check_status(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    turn = tour.get_current_turn()
    data = turn.check_all()
    if len(data) == 0:
        return HttpResponse("All Done")
    else:
        return HttpResponse("\n".join(data))


def export(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    if tour.is_over():
        response = HttpResponse(tour.dumpdata(), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="%s.json"' % tour.alias
        return response


def delete(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    tour.delete()
    return redirect("/accounts")


