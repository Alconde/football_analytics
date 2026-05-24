from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    
    path("", include("apps.core.urls")),
    path("players/", include("apps.players.urls")),
    path("matches/", include("apps.matches.urls")),
    path("tactical/", include("apps.tactical.urls")),
    path("reports/", include("apps.reports.urls")),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)