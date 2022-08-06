from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, reverse

from fbsurvivor import settings
from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm, PlayerForm
from fbsurvivor.core.models import Season, Player, League


def home(request):
    current_season = get_object_or_404(Season, is_current=True)

    if request.method == "GET":
        context = {
            "form": PlayerForm(),
        }
        return render(request, "home.html", context=context)

    if request.method == "POST":
        form = PlayerForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            league = form.cleaned_data["league"]

            try:
                league = League.objects.get(code=league)
            except League.DoesNotExist:
                messages.info(request, "Invalid league. Try again!")
                return redirect(reverse("home"))

            usernames = list(Player.objects.values_list("username", flat=True))
            if username in usernames:
                messages.info(request, "Username already in use. Try again!")
                return redirect(reverse("home"))
            else:
                Player.objects.create(username=username, email=email, league=league)
                return render(request, "created.html")


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
