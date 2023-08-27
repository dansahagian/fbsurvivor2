import pytest

from fbsurvivor.core.models import Pick, PlayerStatus, Week


@pytest.fixture
def current_week(weeks):
    return weeks["this_season"][-1]


@pytest.fixture
def this_season(seasons):
    return seasons[1]


class TestPicks:
    def test_pick_for_player_season(self, db, players, seasons, picks):
        p1 = players[0]
        this_season = seasons[1]

        qs = Pick.objects.for_player_season(p1, this_season)

        assert list(qs) == picks["p1"]["this_season"]

    def test_pick_for_player_season_locked(self, db, players, seasons, picks):
        p1 = players[0]
        this_season = seasons[1]

        qs = Pick.objects.for_board(p1, this_season)
        picks = list(reversed(picks["p1"]["this_season"]))

        assert list(qs) == picks[1:]  # latest pick isn't locked

    def test_pick_for_results(self, db, weeks, picks):
        first_week = weeks["this_season"][0]
        team1 = picks["p1"]["this_season"][0].team.team_code
        team2 = picks["p2"]["this_season"][0].team.team_code

        qs = Pick.objects.for_results(first_week)
        assert list(qs) == sorted([team1, team2])

    def test_pick_for_result_updates(self, db, weeks, picks):
        first_week = weeks["this_season"][0]
        team = picks["p1"]["this_season"][0].team

        qs = Pick.objects.for_result_updates(first_week, team)
        assert qs.count() == 1


class TestReminders:
    def clear_pick(self, player, week):
        pick = Pick.objects.get(player=player, week=week)
        pick.team = None
        pick.save()

    def test_for_email_reminders_with_picks(self, db, current_week):
        assert PlayerStatus.objects.for_email_reminders(current_week).count() == 0

    def test_for_email_reminders_no_pick(self, db, current_week, players):
        self.clear_pick(players[0], current_week)
        self.clear_pick(players[1], current_week)

        emails = list(PlayerStatus.objects.for_email_reminders(current_week))

        assert emails == [players[0].email, players[1].email]

    def test_for_email_reminders_is_retired(self, db, current_week, players, player_statuses):
        self.clear_pick(players[0], current_week)
        self.clear_pick(players[1], current_week)

        player_status = player_statuses["p1"][1]
        player_status.is_retired = True
        player_status.save()

        emails = list(PlayerStatus.objects.for_email_reminders(current_week))

        assert emails == [players[1].email]

    def test_for_email_reminders_has_email_reminders(self, db, current_week, players):
        self.clear_pick(players[0], current_week)
        self.clear_pick(players[1], current_week)

        players[1].has_email_reminders = False
        players[1].save()

        emails = list(PlayerStatus.objects.for_email_reminders(current_week))

        assert emails == [players[0].email]


class TestWeeks:
    def test_week_for_display(self, this_season, weeks):
        qs = Week.objects.for_display(this_season)
        assert list(qs) == weeks["this_season"][:4]

    def test_week_get_current(self, this_season, weeks):
        qs = Week.objects.get_current(this_season)
        assert qs == weeks["this_season"][3]

    def test_week_get_next(self, this_season, weeks):
        qs = Week.objects.get_next(this_season)
        assert qs == weeks["this_season"][4]

    def test_week_is_locked(self, weeks):
        assert weeks["this_season"][3].is_locked
        assert not weeks["this_season"][4].is_locked
