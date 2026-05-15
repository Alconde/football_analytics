from django.urls import path

from . import views

app_name = "players"

urlpatterns = [
    path("", views.PlayerListView.as_view(), name="list"),
    path("nuevo/", views.PlayerCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.PlayerUpdateView.as_view(), name="update"),
    path("<int:pk>/", views.PlayerDetailView.as_view(), name="detail"),
]