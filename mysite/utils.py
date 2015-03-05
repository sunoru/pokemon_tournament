# coding=utf-8
from pmtour.models import Tournament
from accounts.models import PlayerUser


def import_from_files(files):
    admin = PlayerUser.objects.get(player_id="root")
    for afile in files:
        print "Parsing %s..." % afile,
        with open(afile) as f: datas = f.read()
        tour = Tournament.loaddata(datas, admin)
        print tour.name
