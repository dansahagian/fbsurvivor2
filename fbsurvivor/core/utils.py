import secrets
import smtplib
import string
from email.mime.text import MIMEText

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from fbsurvivor import settings
from fbsurvivor.core.models import Player, Season, PlayerStatus


def get_player_info(link, year):
    player = get_object_or_404(Player, link=link)
    season = get_object_or_404(Season, year=year)

    try:
        player_status = PlayerStatus.objects.get(player=player, season=season)
    except PlayerStatus.DoesNotExist:
        player_status = None

    return player, season, player_status


def send_to_latest_season_played(request, link, year):
    ps = PlayerStatus.objects.filter(player__link=link).order_by("-season__year")
    if ps:
        latest = ps[0].season.year
        messages.warning(request, f"You did NOT play in {year}. Here is {latest}")
        return redirect(reverse("player_view", args=[link, latest]))
    else:
        messages.warning(request, f"We don't have a record of you playing any season.")
        return redirect(reverse("home"))


def generate_link() -> str:
    char_set = string.ascii_lowercase + string.digits
    link = "".join(secrets.choice(char_set) for _ in range(44))

    links = Player.objects.values_list("link", flat=True)

    if link in links:
        return generate_link()

    return link


def generate_code() -> int:
    return secrets.choice(range(111111, 1000000))


def send_email(subject, recipients, message):
    sender = settings.SMTP_SENDER

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = sender

    conn = smtplib.SMTP_SSL(settings.SMTP_SERVER)
    conn.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    try:
        conn.sendmail(sender, recipients, msg.as_string())
    finally:
        conn.quit()
