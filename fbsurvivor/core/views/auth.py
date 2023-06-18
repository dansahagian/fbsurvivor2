import arrow
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from jwt import ExpiredSignatureError, InvalidSignatureError, encode, decode

from fbsurvivor.celery import send_email_task
from fbsurvivor.core.forms import EmailForm
from fbsurvivor.core.models.player import Player
from fbsurvivor.settings import SECRET_KEY, DOMAIN


def create_token(player) -> str:
    exp = arrow.now().shift(days=30).datetime
    payload = {"username": player.username, "exp": exp}

    return encode(payload, SECRET_KEY, algorithm="HS256")


def get_authenticated_player(request) -> Player | None:
    if token := request.session.get("token"):
        try:
            if payload := decode(token, SECRET_KEY, algorithms="HS256"):
                if username := payload.get("username"):
                    return get_object_or_404(Player, username=username)
                request.session.delete("token")
        except (ExpiredSignatureError, InvalidSignatureError):
            return None
    return None


def authenticate_player(view):
    def inner(*args, **kwargs):
        request = args[0]
        if player := get_authenticated_player(request):
            kwargs["player"] = player
            kwargs["path"] = request.session.get("path")
            request.session["path"] = request.path
            return view(*args, **kwargs)

        return redirect(reverse("signin"))

    return inner


def get_authenticated_admin(request) -> Player | None:
    if player := get_authenticated_player(request):
        return player if player.is_admin else None


def authenticate_admin(view):
    def inner(*args, **kwargs):
        request = args[0]
        if player := get_authenticated_admin(request):
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
        if request.session.get("token"):
            return redirect(reverse("board_redirect"))

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


def logout(request):
    request.session.delete("token")
    return redirect(reverse("signin"))


def enter(request, token):
    request.session["token"] = token

    return redirect(reverse("board_redirect"))


@authenticate_admin
def assume(request, username, **kwargs):
    player = get_object_or_404(Player, username=username)
    token = create_token(player)

    return redirect(reverse("enter", args=[token]))
