from django.shortcuts import render, loader
from django.http import HttpResponse, Http404
from django.template import RequestContext
from pmtour.models import Tournament, Player


def index(request):
    pass


def home(request, tour_id):
    try:
        tour = Tournament.objects.get(alias=tour_id)
    except Tournament.DoesNotExist:
        try:
            tour = Tournament.objects.get(tour_id=tour_id)
        except Tournament.DoesNotExist:
            raise Http404
    temp = loader.get_template("pmtour/home.html")
    cont = RequestContext(request, {"tour":tour})
    return HttpResponse(temp.render(cont))

