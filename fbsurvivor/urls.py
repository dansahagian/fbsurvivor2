from django.contrib import admin
from django.urls import path, include

from fbsurvivor import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("fbsurvivor.core.urls")),
]

if settings.ENV == "dev":
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
