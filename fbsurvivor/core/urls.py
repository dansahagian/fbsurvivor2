from django.urls import path

from fbsurvivor.core import views

urlpatterns = [
    path("", views.signup, name="home"),
    path("forgot/", views.forgot, name="forgot"),
    path("<str:link>", views.player_redirect, name="player_redirect"),
    path("<str:link>/<int:year>/", views.player_view, name="player_view"),
    path("<str:link>/<str:contact>/", views.confirm_contact, name="confirm_contact"),
]
