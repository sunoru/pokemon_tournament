# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils import timezone
import json
from pmtour.models import Tournament
from pmtour.views.utils import (
    get_a_tour,
    ret_no_perm,
    ret_tempcont,
)

INVALID_LIST = {
    "admin",
    "django_admin",
    "accounts"
}


@login_required
def settings(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)

    status = 0
    tm = str(timezone.localtime(tour.start_time).replace(tzinfo=None)).replace(' ', 'T')
    if request.method == "POST":
        try:
            if request.POST["tour_alias"] != tour.alias:
                if not tour.alias_unique(request.POST["tour_alias"]) or request.POST["tour_alias"] in INVALID_LIST:
                    raise Tournament.InvalidAliasError
            if tour.is_over():
                raise Tournament.TourOverError
            tour.name = request.POST["tour_name"]
            tour.alias = request.POST["tour_alias"]
            tour.tournament_type = request.POST["tour_type"]
            tour.start_time = request.POST["tour_start_time"]  # TODO: time zone settings
            tm = request.POST["tour_start_time"]
            tour.description = request.POST["tour_description"]
            if "tour_turns" in request.POST:
                tour.set_option("turns", int(request.POST["tour_turns"]))
            if "tour_elims" in request.POST:
                tour_elims = int(request.POST["tour_elims"])
                if tour_elims not in {2, 4, 8}:
                    raise Tournament.InvalidNumberError
                tour.set_option("elims", tour_elims)
            tour.save()
            status = 1
        except Tournament.InvalidAliasError:
            status = 2
        except Tournament.TourOverError:
            status = 3
        except Tournament.InvalidNumberError:
            status = 4
        except:
            status = -1
    mj = json.loads(tour.remarks)
    return ret_tempcont(
        request,
        "pmtour/settings.html",
        {"tour": tour, "has_perm": has_perm, "status": status, "remarks": mj, "starttime": tm}
    )


def get_turns(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    tp = int(request.GET.get("q", -1))
    if tp == 0:
        return HttpResponse(_get_turns(tour.get_players_count()))
    elif tp == 2:
        return HttpResponse(_get_turns_2(tour.get_players_count()))
    else:
        raise Http404


def get_elims(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if int(request.GET.get("q", -1)) == 2:
        return HttpResponse(_get_elims(tour.get_players_count()))
    else:
        raise Http404


def _get_turns(number):
    if number < 6:
        return -1
    elif 6 <= number <= 8:
        return 3
    elif number <= 16:
        return 4
    elif number <= 32:
        return 5
    elif number <= 64:
        return 6
    elif number <= 128:
        return 7
    elif number <= 256:
        return 8
    else:
        return -1


def _get_turns_2(number):
    if number < 8:
        return -1
    elif number == 8:
        return 3
    elif number <= 12:
        return 4
    elif number <= 32:
        return 5
    elif number <= 64:
        return 6
    elif number <= 128:
        return 7
    elif number <= 226:
        return 8
    elif number <= 409:
        return 9
    elif number > 409:
        return 10


def _get_elims(number):
    if number < 8:
        return -1
    elif number == 8:
        return 0
    elif number <= 20:
        return 4
    elif number >= 21:
        return 8

