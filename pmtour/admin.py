from django.contrib import admin
from pmtour.models import Player, Tournament, Log, Turn

models = (
    Player,
    Tournament,
    Log,
    Turn
)
for model in models:
    admin.site.register(model)
