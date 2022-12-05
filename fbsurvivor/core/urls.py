from django.urls import path

from fbsurvivor.core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("forgot/", views.forgot, name="forgot"),
    path("darkmode/<str:link>", views.dark_mode, name="dark_mode"),
    path("board/<str:link>/", views.player_redirect, name="player_redirect"),
    path("board/<str:link>", views.player_redirect),
    path("board/<str:link>/<int:year>/", views.player, name="player"),
    path("manager/<str:link>/", views.manager_redirect, name="manager_redirect"),
    path("manager/<str:link>/<int:year>/", views.manager, name="manager"),
    path("payouts/<str:link>/", views.payouts, name="payouts"),
    path("rules/<str:link>/", views.rules, name="rules"),
    path(
        "player-links/<str:link>/<int:year>",
        views.get_player_links,
        name="get-player-links",
    ),
    path(
        "update-board-cache/<str:link>/<int:year>/",
        views.update_board_cache,
        name="update-board-cache",
    ),
    path("remind/<str:link>/<int:year>/", views.remind, name="remind"),
    path("results/<str:link>/<int:year>/", views.results, name="results"),
    path(
        "results/<str:link>/<int:year>/<int:week>/<str:team>/<str:result>/",
        views.mark_result,
        name="mark_result",
    ),
    path("paid/<str:link>/<int:year>/", views.paid, name="paid"),
    path(
        "paid/<str:link>/<int:year>/<str:user_link>/", views.user_paid, name="user_paid"
    ),
    path("play/<str:link>/<int:year>/", views.play, name="play"),
    path("retire/<str:link>/<int:year>/", views.retire, name="retire"),
    path("picks/<str:link>/", views.picks_redirect, name="picks_redirect"),
    path("picks/<str:link>/<int:year>/", views.picks, name="picks"),
    path("picks/<str:link>/<int:year>/<int:week>/", views.pick, name="pick"),
    path("more/<str:link>/", views.more, name="more"),
    path("link/<str:link>/reset/", views.reset_link, name="reset_link"),
    path("<str:link>/", views.player_redirect),
    path("<str:link>", views.player_redirect),
]
