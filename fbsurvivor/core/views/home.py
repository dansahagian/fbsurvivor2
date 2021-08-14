from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, reverse

from fbsurvivor import settings
from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm, SignUpCodeForm, PlayerForm
from fbsurvivor.core.models import Season, Player, SignUpCode


def home(request):
    current_season = get_object_or_404(Season, is_current=True)

    if request.method == "GET":
        context = {"form": SignUpCodeForm(), "locked": current_season.is_locked}
        return render(request, "home.html", context=context)

    if request.method == "POST":
        form = SignUpCodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                SignUpCode.objects.get(code=code)
            except SignUpCode.DoesNotExist:
                messages.error(
                    request, f"'{code}' is not a valid sign up code. Try Again!"
                )
                return redirect(reverse("home"))
            return redirect(reverse("signup"))


def signup(request):
    if request.method == "GET":
        context = {
            "form": PlayerForm(),
        }
        return render(request, "signup.html", context=context)

    if request.method == "POST":
        form = PlayerForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            usernames = list(Player.objects.values_list("username", flat=True))
            if username in usernames:
                messages.error(request, "Username already in use. Try again!")
                return redirect(reverse("signup"))
            else:
                Player.objects.create(username=username, email=email)
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
