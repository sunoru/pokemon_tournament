# coding=utf-8

from pmtour.views.home import home
from pmtour.views.bracket import bracket
from pmtour.views.standings import standings
from pmtour.views.discussion import discussion
from pmtour.views.log import log, log_bracket, log_standings
from pmtour.views.settings import settings, get_turns, get_elims
from pmtour.views.participants import participants, add_player, add_test_player, edit_name
from pmtour.views.others import check, export, delete
