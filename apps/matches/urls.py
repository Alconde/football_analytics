from django.urls import path

from . import views

app_name = "matches"

urlpatterns = [
    path("", views.MatchListView.as_view(), name="list"),
    path("nuevo/", views.MatchCreateView.as_view(), name="create"),
    path("<int:pk>/analitica/", views.MatchAnalyticsView.as_view(), name="analytics"),

]