from django.urls import path

from fbsurvivor.core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("forgot/", views.forgot, name="forgot"),
    path("board/<str:link>/", views.player_redirect, name="player_redirect"),
    path("board/<str:link>", views.player_redirect),
    path("board/<str:link>/<int:year>/", views.player, name="player"),
    path("manager/<str:link>/<int:year>/", views.manager, name="manager"),
    path("other/<str:link>/<int:year>/", views.other, name="other"),
    path("get-link/<str:link>/", views.get_link, name="get-link"),
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
    path("picks/<str:link>/<int:year>/", views.picks, name="picks"),
    path("picks/<str:link>/<int:year>/<int:week>/", views.pick, name="pick"),
    path("<str:link>/", views.player_redirect),
    path("<str:link>", views.player_redirect),
]
