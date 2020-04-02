from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor.core.forms import PlayerForm, CodeForm, EmailForm
from fbsurvivor.core.models import Season, Player
from fbsurvivor.core.utils import (
    get_current_season,
    generate_link,
    generate_code,
    send_email,
)
from fbsurvivor import settings


def home(request):
    season: Season = get_current_season()

    if season.is_locked:
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


def player_page(request, link):
    player = get_object_or_404(Player, link=link)
    return HttpResponse(f"You made it {player.username}")
