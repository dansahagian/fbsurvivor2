import arrow
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from jwt import ExpiredSignatureError, InvalidSignatureError, encode, decode

from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm
from fbsurvivor.core.models.player import Player
from fbsurvivor.settings import SECRET_KEY, DOMAIN


def create_token(player) -> str:
    days = 1 if player.has_advanced_security else 7
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


def send_magic_link(player):
    token = create_token(player)
    subject = "Survivor - Sign in"
    message = f"Click the link below to signin\n\n{DOMAIN}/enter/{token}"
    send_email_task.delay(subject, [player.email], message)


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
                send_magic_link(player)
            except Player.DoesNotExist:
                pass

        return render(request, "signin-sent.html")


def me(request, link):
    player = get_object_or_404(Player, link=link)

    context = {
        "username": player.username,
        "has_advanced_security": player.has_advanced_security,
        "link": link,
    }

    return render(request, "me.html", context=context)


def enter(request, token):
    request.session["token"] = token

    return redirect(reverse("board_redirect"))


def login(request, link):
    if authenticate(request):
        return redirect(reverse("board_redirect"))

    player = get_object_or_404(Player, link=link)

    if player.has_advanced_security:
        send_magic_link(player)
        return render(request, "sent-magic-link.html")

    token = create_token(player)
    return redirect(reverse("enter", args=[token]))
