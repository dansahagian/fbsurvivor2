import hashlib

import arrow
import sentry_sdk
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from jwt import encode, decode, ExpiredSignatureError, InvalidSignatureError

from fbsurvivor.core.utils.emails import send_email
from fbsurvivor.core.models import TokenHash, Player, Season
from fbsurvivor.core.utils.helpers import get_current_season
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
            sentry_sdk.set_user({"username": player.username})
            kwargs["player"] = player
            kwargs["path"] = request.session.get("path")
            request.session["path"] = request.path
            return view(*args, **kwargs)
        request.session.delete("token")

        return redirect(reverse("signin"))

    return inner


def authenticate_admin(view):
    def inner(*args, **kwargs):
        request = args[0]
        if player := get_authenticated_admin(request):
            sentry_sdk.set_user({"username": player.username})
            kwargs["player"] = player
            kwargs["path"] = request.session.get("path")
            request.session["path"] = request.path
            return view(*args, **kwargs)
        request.session.delete("token")

        return redirect(reverse("signin"))

    return inner


def check_token_and_get_player(payload, token):
    username = payload.get("username")

    if not username:
        return None

    try:
        player = Player.objects.get(username=username)
    except Player.DoesNotExist:
        return None

    try:
        player.tokens.get(hash=get_token_hash(token))
        return player
    except TokenHash.DoesNotExist:
        return None


def get_authenticated_player(request) -> Player | None:
    token = request.session.get("token")

    if not token:
        return None

    try:
        payload = decode(token, SECRET_KEY, algorithms="HS256")
        return check_token_and_get_player(payload, token)
    except (ExpiredSignatureError, InvalidSignatureError):
        return None


def get_authenticated_admin(request) -> Player | None:
    player = get_authenticated_player(request)
    return player if player and player.is_admin else None


def get_season_context(year, **kwargs):
    season = get_object_or_404(Season, year=year)
    current_season = get_current_season()
    return season, {"season": season, "player": kwargs["player"], "current_season": current_season}


def send_magic_link(player):
    token = create_token(player)
    subject = "🏈 Survivor Sign in"
    message = f"Click the link below to signin\n\n{DOMAIN}/enter/{token}"
    send_email(subject, [player.email], message)
