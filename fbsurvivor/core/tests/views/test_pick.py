from django.urls import reverse

from fbsurvivor.core.views.pick import get_player_info_and_context


def test_get_player_info_and_context(players, seasons, player_statuses):
    p1 = players[0]
    this_season = seasons[1]

    player, season, player_status, context = get_player_info_and_context(
        p1.link, this_season.year
    )
    assert player == p1
    assert season == this_season
    assert player_status == player_statuses["p1"][1]
    assert "player" in context
    assert "season" in context
    assert "player_status" in context


def test_view_picks(db, client, players, seasons):
    link = players[0].link
    year = seasons[1].year
    url = reverse("picks", args=[link, year])
    response = client.get(url)
    assert response.status_code == 200


def test_view_pick_week_is_locked(db, client):
    url = reverse("pick", args=["ABC123", 2020, 1])
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == "/picks/ABC123/2020/"


def test_view_pick_get(db, client):
    url = reverse("pick", args=["ABC123", 2020, 5])
    response = client.get(url)
    assert response.status_code == 200
