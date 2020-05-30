import pytest

from fbsurvivor.core.models import PlayerStatus, Pick


@pytest.fixture
def current_week(weeks):
    return weeks["this_season"][-1]


def clear_pick(player, week):
    pick = Pick.objects.get(player=player, week=week)
    pick.team = None
    pick.save()


def test_for_email_reminders_with_picks(db, current_week):
    assert PlayerStatus.objects.for_email_reminders(current_week).count() == 0


def test_for_email_reminders_no_pick(db, current_week, players):
    clear_pick(players[0], current_week)
    clear_pick(players[1], current_week)

    emails = list(PlayerStatus.objects.for_email_reminders(current_week))

    assert emails == [players[0].email, players[1].email]


def test_for_email_reminders_is_retired(db, current_week, players, player_statuses):
    clear_pick(players[0], current_week)
    clear_pick(players[1], current_week)

    player_status = player_statuses["p1"][1]
    player_status.is_retired = True
    player_status.save()

    emails = list(PlayerStatus.objects.for_email_reminders(current_week))

    assert emails == [players[1].email]


def test_for_email_reminders_has_email_reminders(db, current_week, players):
    clear_pick(players[0], current_week)
    clear_pick(players[1], current_week)

    players[1].has_email_reminders = False
    players[1].save()

    emails = list(PlayerStatus.objects.for_email_reminders(current_week))

    assert emails == [players[0].email]
