from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor import settings
from fbsurvivor.core.forms import PlayerForm, CodeForm, EmailForm
from fbsurvivor.core.models import Season, Player, PlayerStatus
from fbsurvivor.core.utils import (
    generate_link,
    generate_code,
    send_email,
)


def home(request):
    current_season = get_object_or_404(Season, is_current=True)

    if current_season.is_locked:
        messages.warning(request, "Sign Ups are currently locked!")
        return render(request, "locked.html")

    if request.method == "GET":
        form = PlayerForm()
        return render(request, "signup.html", {"form": form})

    if request.method == "POST":
        form = PlayerForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            link = generate_link()
            code = generate_code()

            player, created = Player.objects.get_or_create(
                username=username,
                defaults={"email": email, "link": link, "confirmation_code": code},
            )

            if created:
                subject = "Survivor - Email Confirmation Code"
                message = f"Email Code: {code}"
                send_email(subject, [player.email], message)
                return redirect(reverse("confirm_contact", args=[link, "email"]))

            messages.warning(request, "That username is taken! Try again.")
            return redirect(reverse("home"))


def confirm_contact(request, link, contact):
    player = get_object_or_404(Player, link=link)

    if contact not in ["email", "phone"]:
        raise Http404

    if request.method == "GET":
        context = {
            "form": CodeForm(),
            "info": f"Enter the code you received to confirm your {contact}",
            "link": link,
            "contact": contact,
        }
        return render(request, "confirm.html", context=context)

    if request.method == "POST":
        form = CodeForm(request.POST)

        if form.is_valid():
            code = int(form.cleaned_data["confirmation_code"].strip())
            if code == player.confirmation_code:
                player.confirmation_code = None
                setattr(player, f"is_{contact}_confirmed", True)
                player.save()
                return redirect(reverse("player_page", args=[link]))


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
                    message += f"\n\n{settings.DOMAIN}/{player.link}"

                send_email(subject, [email], message)
                return render(request, "forgot-sent.html")


def player_redirect(request, link):
    get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)
    return redirect(reverse("player_page", args=[link, current_season.year]))


def player_page(request, link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)
    try:
        player_status = PlayerStatus.objects.get(player=player, season=season)
        is_retired = player_status.is_retired
    except PlayerStatus.DoesNotExist:
        player_status = None
        is_retired = False

    can_retire = player_status and (not is_retired) and season.is_current
    years = (
        PlayerStatus.objects.filter(player=player)
        .values_list("season__year", flat=True)
        .order_by("season__year")
    )

    player_statuses = PlayerStatus.objects.filter(season=season).order_by(
        "is_retired", "player__username", "loss_count", "win_count", "is_survivor"
    )

    for status in player_statuses:
        print(status.player.username)

    context = {
        "player": player,
        "season": season,
        "player_status": player_status,
        "years": years,
        "can_retire": can_retire,
        "board": None,
    }

    return render(request, "player-page.html", context=context)
