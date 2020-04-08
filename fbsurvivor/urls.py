from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("wicked/admin/", admin.site.urls),
    path("", include("fbsurvivor.core.urls")),
]
