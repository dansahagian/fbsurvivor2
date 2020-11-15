from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from fbsurvivor import settings
from fbsurvivor.schema import schema
from graphene_django.views import GraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path("", include("fbsurvivor.core.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
