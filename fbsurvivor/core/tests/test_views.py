import pytest
from django.urls import reverse

from fbsurvivor.core.models import Pick
from fbsurvivor.core.utils.auth import create_token
from fbsurvivor.core.utils.helpers import get_player_context


@pytest.fixture
def token(players):
    return create_token(players[0])


@pytest.fixture
def year(seasons):
    return seasons[1].year


def test_get_player_info_and_context(players, seasons, player_statuses):
    p1 = players[0]
    this_season = seasons[1]

    season, player_status, context = get_player_context(p1, this_season.year)
    assert season == this_season
    assert player_status == player_statuses["p1"][1]
    assert "player" in context
    assert "season" in context
    assert "player_status" in context


class TestPickViews:
    def test_view_picks(self, client, token, year):
        client.get(reverse("enter", args=[token]))
        url = reverse("picks", args=[year])
        response = client.get(url)
        assert response.status_code == 200

    def test_view_pick_week_is_locked(self, client, token, year):
        client.get(reverse("enter", args=[token]))
        url = reverse("pick", args=[year, 1])
        response = client.get(url, follow=True)
        messages = [str(x) for x in response.context["messages"]]
        assert response.status_code == 200
        assert "Week 1 is locked!" in messages

    def test_view_pick_get(self, client, token, year):
        client.get(reverse("enter", args=[token]))
        url = reverse("pick", args=[year, 5])
        response = client.get(url)
        assert response.status_code == 200

    def test_view_pick_post(self, client, token, year, players):
        client.get(reverse("enter", args=[token]))
        p1 = players[0]

        url = reverse("pick", args=[year, 5])
        response = client.post(url, {"team": "BUF"}, follow=True)
        messages = [str(x) for x in response.context["messages"]]
        pick = Pick.objects.get(player=p1, week__season__year=year, week__week_num=5)

        assert response.status_code == 200
        assert pick.team.team_code == "BUF"
        assert "BUF submitted for week 5" in messages

    def test_view_pick_post_bad_team(self, client, token, year, players):
        client.get(reverse("enter", args=[token]))
        url = reverse("pick", args=[year, 5])
        response = client.post(url, {"team": "WAS"}, follow=True)
        messages = [str(x) for x in response.context["messages"]]

        assert response.status_code == 200
        assert "Bad form submission" in messages
