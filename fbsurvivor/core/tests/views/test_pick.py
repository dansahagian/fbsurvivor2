from django.urls import reverse
from fbsurvivor.core.views.pick import get_player_info_and_context


def test_get_player_info_and_context(players, seasons, player_statuses):
    p, s, ps, c = get_player_info_and_context(players[0].link, 2020)
    assert p == players[0]
    assert s == seasons[1]
    assert ps == player_statuses[0]
    assert "player" in c
    assert "season" in c
    assert "player_status" in c


def test_view_picks(db, client, players):
    url = reverse("picks", args=[players[0].link, 2020])
    response = client.get(url)
    assert response.status_code == 200
