from django.contrib import messages
from django.shortcuts import render

from fbsurvivor.core.models import Season
from fbsurvivor.core.utils import get_current_season


def home(request):
    season: Season = get_current_season()

    if season.is_locked:
        messages.warning(request, "Sign Ups are currently locked!")
        return render(request, template_name="locked.html")
