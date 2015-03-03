# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
import random
from accounts.models import PlayerUser
from pmtour.models import Player
from pmtour.views.utils import (
    get_a_tour,
    ret_no_perm,
    ret_tempcont,
    ret_json_data
)


@login_required
def participants(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    if has_perm and request.method == "POST":
        if request.POST["commit"] == "exit":
            try:
                player = tour.player_set.get(playerid=request.POST["playerid"])
            except Player.DoesNotExist:
                raise Http404
            player.exit()
            player.save()
    return ret_tempcont(
        request,
        "pmtour/participants.html",
        {"tour": tour, "has_perm": has_perm}
    )


@login_required
def add_player(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)

    if request.method == "POST":
        q = request.POST.getlist("selected_players")
        not_shuffle = request.POST.get("not_shuffle", False)
        if not not_shuffle:
            random.shuffle(q)
        for sp in q:
            pu = PlayerUser.objects.get(player_id=sp)
            Player.create(
                user=pu,
                name=pu.name,
                tournament=tour,
                playerid=tour.get_available_playerid()
            )
        tour.save()
        return redirect("/%s/participants/" % tour.alias)

    playerusers = PlayerUser.objects.all()
    return ret_tempcont(
        request,
        "pmtour/add_player.html",
        {"tour": tour, "has_perm": has_perm, "playerusers": playerusers}
    )


@login_required
def add_test_player(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)

    if request.method == "POST":
        q = request.POST.getlist("selected_players")
        not_shuffle = request.POST.get("not_shuffle", True)
        if not not_shuffle:
            random.shuffle(q)
        for sp in q:
            pid = tour.get_available_playerid()
            playeruser = PlayerUser.create_test_player(tour, sp, pid)
            Player.create(
                user=playeruser,
                name=sp,
                tournament=tour,
                playerid=pid
            )
        tour.save()
        return redirect("/%s/participants/" % tour.alias)

    playerusers = PlayerUser.objects.all()
    return ret_tempcont(
        request,
        "pmtour/add_test_player.html",
        {"tour": tour, "has_perm": has_perm, "playerusers": playerusers}
    )


@login_required
def edit_name(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    if request.method == "POST":
        if "playerid" not in request.POST or "name" not in request.POST:
            raise Http404
        player = tour.player_set.get(playerid=request.POST["playerid"])
        try:
            player.name = request.POST["name"]
            player.save()
        except Exception:
            return ret_json_data({"status": False})
        return ret_json_data({"status": True, "name": player.name, "playerid": player.playerid})
    raise Http404
