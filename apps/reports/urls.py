from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.GeneratedReportListView.as_view(), name="list"),
    path("nuevo/", views.GeneratedReportCreateView.as_view(), name="create"),
]
