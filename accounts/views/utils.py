# coding=utf-8
from django.shortcuts import redirect, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import pmtour.models


@login_required
def create(request):
    if not request.user.is_staff:
        raise Http404
    tour = pmtour.models.Tournament.create(request.user.playeruser)
    return redirect("/%s/" % tour.alias)


@login_required
def load(request):
    if not request.user.is_staff:
        raise Http404
    status = 0
    if request.method == "POST":
        datas = request.POST.get("import_data", "")
        if datas == "":
            status = -1
        else:
            #try:
                tour = pmtour.models.Tournament.loaddata(datas, request.user.playeruser)
                return redirect("/%s/" % tour.alias)
            # except pmtour.models.Tournament.LoaddataError:
            #     status = -1
    temp = loader.get_template("accounts/load.html")
    cont = {"status": status}
    return HttpResponse(temp.render(cont, request))
