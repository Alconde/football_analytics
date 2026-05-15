from django.urls import path

from . import views

app_name = "tactical"

urlpatterns = [
    path(
        "partials/partidos-por-temporada/",
        views.MatchSelectFragmentView.as_view(),
        name="match_options",
    ),
    path("informes/", views.TacticalReportListView.as_view(), name="list"),
    path("informes/<int:pk>/", views.TacticalReportDetailView.as_view(), name="detail"),
    path("informes/nuevo/", views.TacticalReportCreateView.as_view(), name="report_create"),
]