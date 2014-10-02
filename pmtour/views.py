from django.shortcuts import render, loader
from django.http import HttpResponse, Http404
from django.template import RequestContext
from pmtour.models import Tournament, Player

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
    return (not request.user.is_anonymous() and request.user.playeruser in tour.admins.all())


def _ret_normal(request, tour_id, aname):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    temp = loader.get_template("pmtour/%s.html" % aname)
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))


def _ret_no_perm(request, tour_id):
    temp = loader.get_template("pmtour/no_perm.html")
    cont = RequestContext(request, {"tour": _get_tour(tour_id)})
    return HttpResponse(temp.render(cont))


def home(request, tour_id):
    print tour_id
    return _ret_normal(request, tour_id, "home")


def settings(request, tour_id):
    tour = _get_tour(tour_id)
    has_perm = _get_perm(request, tour)
    if not has_perm:
        return _ret_no_perm(request, tour_id)
    temp = loader.get_template("pmtour/settings.html")
    cont = RequestContext(request, {"tour": tour, "has_perm": has_perm})
    return HttpResponse(temp.render(cont))
