from django.contrib.auth.decorators import login_required

from pmtour.views.utils import (
    get_a_tour,
    ret_no_perm,
    ret_tempcont,
    ret_json_data
)


@login_required
def advanced(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    return ret_tempcont(
        request,
        "pmtour/advanced.html",
        {"tour": tour, "has_perm": has_perm}
    )


@login_required
def bye_rounds(request, tour_id):
    tour, has_perm = get_a_tour(request, tour_id)
    if not has_perm:
        return ret_no_perm(request, tour_id)
    if request.method == "POST":
        if request.POST.get("commit") == "submit":
            playerid = request.POST["playerid"]
            player = tour.player_set.get(playerid=playerid)
            player.bye_rounds = request.POST["value"]
            player.save()
            return ret_json_data({'status': True, 'playerid': playerid})
        return ret_json_data({'status': False})
    return ret_tempcont(
        request,
        "pmtour/bye_rounds.html",
        {"tour": tour, "has_perm": has_perm}
    )
