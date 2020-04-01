from django.urls import path

from fbsurvivor.core import views

urlpatterns = [
    path('', views.home, name='home'),
]