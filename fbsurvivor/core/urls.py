from django.urls import path

from fbsurvivor.core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("forgot/", views.forgot, name="forgot"),
    path("<str:link>/<str:contact>/", views.confirm_contact, name="confirm_contact"),
    path("<str:link>/", views.player_page, name="player_page"),
]
