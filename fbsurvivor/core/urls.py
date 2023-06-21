from django.urls import path

from fbsurvivor.core.views.auth import enter, signin, assume, logout
from fbsurvivor.core.views.manager import (
    manager_redirect,
    manager,
    paid,
    user_paid,
    results,
    result,
    remind,
    get_players,
    update_board_cache,
    send_message,
)
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
    reminders,
    change_reminders,
)

urlpatterns = [
    path("", signin, name="signin"),
    path("logout", logout, name="logout"),
    path("enter/<str:token>/", enter, name="enter"),
    path("assume/<str:username>/", assume, name="assume"),
    path("board/", board_redirect, name="board_redirect"),
    path("board/<int:year>/", board, name="board"),
    path("play/<int:year>/", play, name="play"),
    path("retire/<int:year>/", retire, name="retire"),
    path("payouts/", payouts, name="payouts"),
    path("rules/", rules, name="rules"),
    path("seasons/", seasons, name="seasons"),
    path("darkmode/", dark_mode, name="dark_mode"),
    path("reminders/", reminders, name="reminders"),
    path("reminders/change/", change_reminders, name="change_reminders"),
    path("picks/", picks_redirect, name="picks_redirect"),
    path("picks/<int:year>/", picks, name="picks"),
    path("picks/<int:year>/<int:week>/", pick, name="pick"),
    path("manager/", manager_redirect, name="manager_redirect"),
    path("manager/<int:year>/", manager, name="manager"),
    path("paid/<int:year>/", paid, name="paid"),
    path("paid/<int:year>/<str:username>/", user_paid, name="user_paid"),
    path("results/<int:year>/", results, name="results"),
    path("results/<int:year>/<int:week>/<str:team>/<str:result>/", result, name="result"),
    path("remind/<int:year>/", remind, name="remind"),
    path("players/<int:year>", get_players, name="players"),
    path("update-board-cache/<int:year>/", update_board_cache, name="update_board_cache"),
    path("message/<int:year>/", send_message, name="send_message"),
]
