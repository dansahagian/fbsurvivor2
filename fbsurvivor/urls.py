from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.views.decorators.http import require_GET

from fbsurvivor import settings
from fbsurvivor.core.constants import ROBOTS_TXT_CONTENT


@require_GET
def robots_txt(
    request,
):
    return HttpResponse(ROBOTS_TXT_CONTENT, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("", include("fbsurvivor.core.urls")),
]

if settings.ENV == "dev":
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
