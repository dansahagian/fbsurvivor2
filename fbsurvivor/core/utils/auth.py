import hashlib

import arrow
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from jwt import encode, decode, ExpiredSignatureError, InvalidSignatureError

from fbsurvivor.celery import send_email_task
from fbsurvivor.core.helpers import get_current_season
from fbsurvivor.core.models import TokenHash, Player, Season
from fbsurvivor.settings import SECRET_KEY, DOMAIN


def get_token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_token(player) -> str:
    exp = arrow.now().shift(days=30).datetime
    payload = {"username": player.username, "exp": exp}

    token = encode(payload, SECRET_KEY, algorithm="HS256")
    TokenHash.objects.create(hash=get_token_hash(token), player=player)
    return token


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


def check_token_and_get_player(request, payload, token):
    if username := payload.get("username"):
        player = get_object_or_404(Player, username=username)
        try:
            player.tokens.get(hash=get_token_hash(token))
            return player
        except TokenHash.DoesNotExist:
            request.session.delete("token")
            return None
    request.session.delete("token")
    return None


def get_authenticated_player(request) -> Player | None:
    if token := request.session.get("token"):
        try:
            payload = decode(token, SECRET_KEY, algorithms="HS256")
            return check_token_and_get_player(request, payload, token)
        except (ExpiredSignatureError, InvalidSignatureError):
            return None
    return None


def get_authenticated_admin(request) -> Player | None:
    if player := get_authenticated_player(request):
        return player if player.is_admin else None


def get_season_context(year, **kwargs):
    season = get_object_or_404(Season, year=year)
    current_season = get_current_season()
    return season, {"season": season, "player": kwargs["player"], "current_season": current_season}


def send_magic_link(player):
    token = create_token(player)
    subject = "Survivor - Sign in"
    message = f"Click the link below to signin\n\n{DOMAIN}/enter/{token}"
    send_email_task.delay(subject, [player.email], message)
