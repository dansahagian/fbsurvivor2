from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse

from fbsurvivor import settings
from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm, SignUpCodeForm
from fbsurvivor.core.models import Season, Player


def home(request):
    current_season = get_object_or_404(Season, is_current=True)

    if current_season.is_locked:
        messages.warning(request, "Sign Ups are currently locked!")

    if request.method == "GET":
        context = {
            "form": SignUpCodeForm(),
        }
        return render(request, "home.html", context=context)

    if request.method == "POST":
        form = SignUpCodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]
            return redirect(reverse("signup"))


def signup(request):
    return HttpResponse("Not Implemented Yet!")


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
