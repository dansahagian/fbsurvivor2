from django.urls import path

from fbsurvivor.core.views.auth import enter, login, signin
from fbsurvivor.core.views.pick import (
    picks,
    picks_redirect,
    pick,
)
from fbsurvivor.core.views.player import (
    board,
    board_redirect,
    dark_mode,
    payouts,
    play,
    retire,
    rules,
    seasons,
)

urlpatterns = [
    path("", signin, name="signin"),
    path("enter/<str:token>/", enter, name="enter"),
    path("login/<str:link>/", login, name="login"),
    path("board/", board_redirect, name="board_redirect"),
    path("board/<int:year>/", board, name="board"),
    path("play/<int:year>/", play, name="play"),
    path("retire/<int:year>/", retire, name="retire"),
    path("payouts/", payouts, name="payouts"),
    path("rules/", rules, name="rules"),
    path("seasons/", seasons, name="seasons"),
    path("darkmode/", dark_mode, name="dark_mode"),
    path("picks/", picks_redirect, name="picks_redirect"),
    path("picks/<int:year>/", picks, name="picks"),
    path("picks/<int:year>/<int:week>/", pick, name="pick"),
    # path(
    #     "player-links/<str:link>/<int:year>",
    #     get_player_links,
    #     name="get-player-links",
    # ),
    # path(
    #     "update-board-cache/<str:link>/<int:year>/",
    #     update_board_cache,
    #     name="update-board-cache",
    # ),
    # path("remind/<str:link>/<int:year>/", remind, name="remind"),
    # path("results/<str:link>/<int:year>/", results, name="results"),
    # path(
    #     "results/<str:link>/<int:year>/<int:week>/<str:team>/<str:result>/",
    #     mark_result,
    #     name="mark_result",
    # ),
    # path("paid/<str:link>/<int:year>/", paid, name="paid"),
    # path("paid/<str:link>/<int:year>/<str:user_link>/", user_paid, name="user_paid"),
]
