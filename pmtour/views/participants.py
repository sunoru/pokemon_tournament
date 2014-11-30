# coding=utf-8
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth.models import User
import random
from accounts.models import PlayerUser
from pmtour.models import Player
from pmtour.views.utils import (
    get_a_tour,
    ret_no_perm,
    ret_tempcont,
)


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


def add_test_player(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)

    if request.method == "POST":
        q = request.POST.getlist("selected_players")
        not_shuffle = request.POST.get("not_shuffle", False)
        if not not_shuffle:
            random.shuffle(q)
        for sp in q:
            pwd = "%s" % random.randint(100000, 999999)
            pid = tour.get_available_playerid()
            usr = "test_%s_%s" % (tour.tour_id, pid)
            user = User.objects.create_user(usr, "%s@moon.moe" % usr, pwd)
            playeruser = PlayerUser.objects.create(user=user, name=sp, player_id=user.username)
            Player.create(
                user=playeruser,
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
