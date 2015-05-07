# coding=utf-8
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import pmtour.models


@login_required
def home(request):
    return render_to_response("accounts/accounts.html", context_instance=RequestContext(request, {
        'tours': [
            x for x in pmtour.models.Tournament.objects.all()
            if x.status >= 0 or x.status == -3 or x in request.user.playeruser.tournament_set.all()
        ]
    }))
