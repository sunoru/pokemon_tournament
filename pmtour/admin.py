from django.contrib import admin
from pmtour.models import PlayerUser, Player, Tournament, Log, Turn

models = (
    PlayerUser,
    Player,
    Tournament,
    Log,
    Turn
)
for model in models:
    admin.site.register(model)
