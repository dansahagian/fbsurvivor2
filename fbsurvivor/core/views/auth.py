import arrow
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from jwt import ExpiredSignatureError, InvalidSignatureError, encode, decode

from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm
from fbsurvivor.core.models.player import Player
from fbsurvivor.core.models.season import Season
from fbsurvivor.settings import SECRET_KEY, DOMAIN


def create_token(player) -> str:
    days = 1 if player.is_admin else 7
    exp = arrow.now().shift(days=days).datetime

    payload = {"link": player.link, "exp": exp}

    return encode(payload, SECRET_KEY, algorithm="HS256")


def authenticate(request) -> Player | None:
    if token := request.session.get("token"):
        try:
            if payload := decode(token, SECRET_KEY, algorithms="HS256"):
                return get_object_or_404(Player, link=payload["link"])
        except (ExpiredSignatureError, InvalidSignatureError):
            return None
    return None


def authenticator(view):
    def inner(*args, **kwargs):
        request = args[0]
        if player := authenticate(request):
            kwargs["player"] = player
            kwargs["path"] = request.session.get("path")
            request.session["path"] = request.path
            return view(*args, **kwargs)

        return redirect(reverse("signin"))

    return inner


def signin(request):
    if request.method == "GET":
        context = {
            "form": EmailForm(),
        }
        return render(request, "signin.html", context=context)

    if request.method == "POST":
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                player = Player.objects.get(email=email)
            except Player.DoesNotExist:
                player = None

            if player:
                token = create_token(player)
                subject = "Survivor - Sign in"
                message = f"Click the link below to signin\n\n{DOMAIN}/enter/{token}"
                send_email_task.delay(subject, [email], message)
        return render(request, "signin-sent.html")


def login(request, link):
    player = get_object_or_404(Player, link=link)
    current_season = get_object_or_404(Season, is_current=True)

    request.session["link"] = player.link
    return redirect(reverse("board", args=[current_season.year]))


def enter(request, token):
    request.session["token"] = token

    return redirect(reverse("board_redirect"))
