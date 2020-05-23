from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from fbsurvivor.core import views

urlpatterns = [
    path("", views.signup, name="home"),
    path("forgot/", views.forgot, name="forgot"),
    path("board/<str:link>/", views.player_redirect, name="player_redirect"),
    path("board/<str:link>", views.player_redirect, name="player_redirect"),
    path("board/<str:link>/<int:year>/", views.player, name="player"),
    path("seasons/<str:link>/", views.seasons, name="seasons"),
    path("manager/<str:link>/<int:year>/", views.manager, name="manager"),
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
    path("confirm/<str:link>/<str:contact>/", views.confirm, name="confirm",),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("api/hello/", views.Hello.as_view(), name="hello"),
]
