from django.urls import path

from fbsurvivor.core.views.home import forgot, home
from fbsurvivor.core.views.manager import (
    manager_redirect,
    get_player_links,
    update_board_cache,
    remind,
    results,
    mark_result,
    paid,
    user_paid,
    manager,
    send_message,
)
from fbsurvivor.core.views.pick import picks_redirect, picks, pick
from fbsurvivor.core.views.player import (
    dark_mode,
    player_redirect,
    payouts,
    rules,
    play,
    retire,
    more,
    reset_link,
    player,
)

urlpatterns = [
    path("", home, name="home"),
    path("forgot/", forgot, name="forgot"),
    path("darkmode/<str:link>", dark_mode, name="dark_mode"),
    path("board/<str:link>/", player_redirect, name="player_redirect"),
    path("board/<str:link>", player_redirect),
    path("board/<str:link>/<int:year>/", player, name="player"),
    path("manager/<str:link>/", manager_redirect, name="manager_redirect"),
    path("manager/<str:link>/<int:year>/", manager, name="manager"),
    path("message/<str:link>/<int:year>/", send_message, name="message"),
    path("payouts/<str:link>/", payouts, name="payouts"),
    path("rules/<str:link>/", rules, name="rules"),
    path(
        "player-links/<str:link>/<int:year>",
        get_player_links,
        name="get-player-links",
    ),
    path(
        "update-board-cache/<str:link>/<int:year>/",
        update_board_cache,
        name="update-board-cache",
    ),
    path("remind/<str:link>/<int:year>/", remind, name="remind"),
    path("results/<str:link>/<int:year>/", results, name="results"),
    path(
        "results/<str:link>/<int:year>/<int:week>/<str:team>/<str:result>/",
        mark_result,
        name="mark_result",
    ),
    path("paid/<str:link>/<int:year>/", paid, name="paid"),
    path("paid/<str:link>/<int:year>/<str:user_link>/", user_paid, name="user_paid"),
    path("play/<str:link>/<int:year>/", play, name="play"),
    path("retire/<str:link>/<int:year>/", retire, name="retire"),
    path("picks/<str:link>/", picks_redirect, name="picks_redirect"),
    path("picks/<str:link>/<int:year>/", picks, name="picks"),
    path("picks/<str:link>/<int:year>/<int:week>/", pick, name="pick"),
    path("more/<str:link>/", more, name="more"),
    path("link/<str:link>/reset/", reset_link, name="reset_link"),
    path("<str:link>/", player_redirect),
    path("<str:link>", player_redirect),
]
