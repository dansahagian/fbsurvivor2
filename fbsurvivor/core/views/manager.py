from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from fbsurvivor.celery import send_reminders_task, send_email_task
from fbsurvivor.core.forms import MessageForm
from fbsurvivor.core.helpers import update_player_records, update_league_caches
from fbsurvivor.core.models.pick import Pick
from fbsurvivor.core.models.player import Player, PlayerStatus
from fbsurvivor.core.models.season import Season
from fbsurvivor.core.models.team import Team
from fbsurvivor.core.models.week import Week


def get_admin_info(link, year):
    player = get_object_or_404(Player, link=link, is_admin=True)
    season = get_object_or_404(Season, year=year)
    context = {"player": player, "season": season}
    return player, season, context


def manager_redirect(request, link):
    current_season = get_object_or_404(Season, is_current=True)
    player, season, context = get_admin_info(link, current_season.year)
    return redirect(reverse("manager", args=[link, current_season.year]))


def manager(request, link, year):
    player, season, context = get_admin_info(link, year)
    return render(request, "manager.html", context=context)


def paid(request, link, year):
    player, season, context = get_admin_info(link, year)
    player_statuses = PlayerStatus.objects.paid_for_season(season).prefetch_related(
        "player"
    )
    context["player_statuses"] = player_statuses
    return render(request, "paid.html", context=context)


def user_paid(request, link, year, user_link):
    player, season, context = get_admin_info(link, year)
    ps = get_object_or_404(PlayerStatus, player__link=user_link, season=season)
    ps.is_paid = True
    ps.save()
    update_league_caches(season)
    messages.info(request, f"{ps.player.username} marked as paid!")
    return redirect(reverse("paid", args=[link, year]))


def results(request, link, year):
    player, season, context = get_admin_info(link, year)
    current_week = Week.objects.get_current(season)
    teams = Pick.objects.for_results(current_week)

    context["week"] = current_week
    context["teams"] = teams

    return render(request, "results.html", context=context)


def mark_result(request, link, year, week, team, result):
    player, season, context = get_admin_info(link, year)
    week = get_object_or_404(Week, season=season, week_num=week)

    team = get_object_or_404(Team, team_code=team, season=season)
    Pick.objects.for_result_updates(week, team).update(result=result)
    Pick.objects.for_no_picks(week).update(result="L")

    messages.info(request, f"Picks for week {week.week_num} of {team} updated!")

    player_records_updated = update_player_records(year)
    update_league_caches(season)
    messages.info(request, f"{player_records_updated} player records updated!")

    return redirect(reverse("results", args=[link, year]))


def remind(request, link, year):
    get_object_or_404(Player, link=link, is_admin=True)
    send_reminders_task.delay()
    messages.info(request, "Reminder task kicked off")
    return redirect(reverse("manager", args=[link, year]))


def get_player_links(request, link, year):
    player, season, context = get_admin_info(link, year)
    player_links = (
        PlayerStatus.objects.values_list("player__username", "player__link")
        .distinct()
        .order_by("player__username")
    )

    context["player_links"] = player_links
    return render(request, "player_links.html", context=context)


def update_board_cache(request, link, year):
    get_object_or_404(Player, link=link, is_admin=True)
    season = get_object_or_404(Season, year=year)
    update_league_caches(season)

    return redirect(reverse("player", args=[link, year]))


def send_message(request, link, year):
    player, season, context = get_admin_info(link, year)

    if request.method == "GET":
        context["form"] = MessageForm()
        return render(request, "message.html", context=context)

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            recipients = Player.objects.filter(playerstatus__season=season).values_list(
                "email", flat=True
            )

            send_email_task.delay(subject, recipients, message)

            return redirect(reverse("player", args=[link, year]))
