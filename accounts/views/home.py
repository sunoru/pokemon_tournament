# coding=utf-8
import math
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pmtour.models
import accounts.models


@login_required
def home(request):
    return render(request, "accounts/home.html")


@login_required
def tournaments(request):
    tours = [
        x for x in pmtour.models.Tournament.objects.all()
        if x.status >= 0 or x.status == -3 or
        x in request.user.playeruser.tournament_set.all() or
        x.player_set.filter(user=request.user.playeruser).count() > 0
        ]
    count = len(tours)
    total_pages = int(math.ceil(count / 20))
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1
    if page > total_pages or page < 1:
        page = 1
    return render(request, "accounts/tournaments.html", {
        'tours': tours[20 * (page - 1):min(count, 20 * page)],
        'prev': None if page == 1 else page - 1,
        'next': None if page == total_pages else page + 1,
    })


@login_required
def playerusers(request):
    playerusers = [
        x for x in accounts.models.PlayerUser.objects.all()
        if x.player_id.find("test") == -1 and not x.user.is_staff
        ]
    count = len(playerusers)
    total_pages = count / 20
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1
    if page > total_pages or page < 1:
        page = 1
    return render(request, "accounts/playerusers.html", {
        'playerusers': playerusers[20 * (page - 1):min(count, 20 * page)],
        'prev': None if page == 1 else page - 1,
        'next': None if page == total_pages else page + 1,
    })
