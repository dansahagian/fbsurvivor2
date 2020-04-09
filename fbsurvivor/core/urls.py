from django.urls import path

from fbsurvivor.core import views

urlpatterns = [
    path("", views.signup, name="home"),
    path("forgot/", views.forgot, name="forgot"),
    path("<str:link>/", views.player_redirect, name="player_redirect"),
    path("<str:link>", views.player_redirect, name="player_redirect"),
    path("board/<str:link>/<int:year>/", views.player, name="player"),
    path("manager/<str:link>/<int:year>/", views.manager, name="manager"),
    path("paid/<str:link>/<int:year>/", views.paid, name="paid"),
    path(
        "paid/<str:link>/<int:year>/<str:user_link>/", views.user_paid, name="user_paid"
    ),
    path("play/<str:link>/<int:year>/", views.play, name="play"),
    path("picks/<str:link>/<int:year>/", views.picks, name="picks"),
    path("picks/<str:link>/<int:year>/<int:week>/", views.pick, name="pick"),
    path("confirm/<str:link>/<str:contact>/", views.confirm, name="confirm",),
]
