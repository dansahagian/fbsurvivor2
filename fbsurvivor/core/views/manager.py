from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from fbsurvivor.celery import send_reminders_task, send_email_task
from fbsurvivor.core.forms import MessageForm
from fbsurvivor.core.helpers import update_player_records, update_league_caches, get_current_season
from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.player import Player, PlayerStatus
from fbsurvivor.core.models.season import Season
from fbsurvivor.core.models.team import Team
from fbsurvivor.core.models.week import Week
from fbsurvivor.core.views.auth import authenticate_admin


def get_season_context(year, **kwargs):
    season = get_object_or_404(Season, year=year)
    current_season = get_current_season()
    return season, {"season": season, "player": kwargs["player"], "current_season": current_season}


@authenticate_admin
def manager_redirect(request, **kwargs):
    season = get_current_season()

    return redirect(reverse("manager", args=[season.year]))


@authenticate_admin
def manager(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)
    return render(request, "manager.html", context=context)


@authenticate_admin
def paid(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)
    player_statuses = PlayerStatus.objects.paid_for_season(season).prefetch_related("player")
    context["player_statuses"] = player_statuses
    return render(request, "paid.html", context=context)


@authenticate_admin
def user_paid(request, year, username, **kwargs):
    season, context = get_season_context(year, **kwargs)
    ps = get_object_or_404(PlayerStatus, player__username=username, season=season)
    ps.is_paid = True
    ps.save()
    update_league_caches(season)
    messages.info(request, f"{ps.player.username} marked as paid!")
    return redirect(reverse("paid", args=[year]))


@authenticate_admin
def results(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)
    current_week = Week.objects.get_current(season)
    teams = Pick.objects.for_results(current_week)

    context["week"] = current_week
    context["teams"] = teams

    return render(request, "results.html", context=context)


@authenticate_admin
def result(request, year, week, team, outcome, **kwargs):
    season, context = get_season_context(year, **kwargs)
    week = get_object_or_404(Week, season=season, week_num=week)

    team = get_object_or_404(Team, team_code=team, season=season)
    Pick.objects.for_result_updates(week, team).update(result=outcome)
    Pick.objects.for_no_picks(week).update(result="L")

    messages.info(request, f"Picks for week {week.week_num} of {team} updated!")

    player_records_updated = update_player_records(year)
    update_league_caches(season)
    messages.info(request, f"{player_records_updated} player records updated!")

    return redirect(reverse("results", args=[year]))


@authenticate_admin
def remind(request, year, **kwargs):
    send_reminders_task.delay()
    messages.info(request, "Reminder task kicked off")
    return redirect(reverse("manager", args=[year]))


@authenticate_admin
def get_players(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)
    context["players"] = (
        PlayerStatus.objects.values_list("player__username", flat=True)
        .distinct()
        .order_by("player__username")
    )

    return render(request, "players.html", context=context)


@authenticate_admin
def update_board_cache(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)
    update_league_caches(season)

    return redirect(reverse("board", args=[year]))


@authenticate_admin
def send_message(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)

    if request.method == "GET":
        context["form"] = MessageForm()
        return render(request, "message.html", context=context)

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            recipients = list(
                Player.objects.filter(playerstatus__season=season)
                .exclude(email="")
                .values_list("email", flat=True)
            )

            subject = f"🏈 Survivor {subject}"

            send_email_task.delay(subject, recipients, message)

            return redirect(reverse("board", args=[year]))


@authenticate_admin
def send_message_all(request, year, **kwargs):
    season, context = get_season_context(year, **kwargs)

    if request.method == "GET":
        context["form"] = MessageForm()
        return render(request, "message_all.html", context=context)

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            recipients = list(Player.objects.exclude(email="").values_list("email", flat=True))

            subject = f"🏈 Survivor {subject}"

            send_email_task.delay(subject, recipients, message)

            return redirect(reverse("board", args=[year]))
