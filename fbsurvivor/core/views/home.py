from django.contrib import messages
from django.shortcuts import render, get_object_or_404

from fbsurvivor import settings
from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm
from fbsurvivor.core.models import Season, Player


def home(request):
    current_season = get_object_or_404(Season, is_current=True)

    if current_season.is_locked:
        messages.warning(request, "Sign Ups are currently locked!")

    if request.method == "GET":
        return render(request, "home.html")


def forgot(request):
    if request.method == "GET":
        context = {
            "form": EmailForm(),
        }
        return render(request, "forgot.html", context=context)

    if request.method == "POST":
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            players = Player.objects.filter(email=email)
            if players:
                subject = "Survivor - Player Links"
                message = (
                    "We found the following links associated with your email address:"
                )
                for player in players:
                    message += f"\n\n{settings.DOMAIN}/board/{player.link}/"

                send_email_task.delay(subject, [email], message)
                return render(request, "forgot-sent.html")
