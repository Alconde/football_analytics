from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('player/<int:player_id>/', views.player_profile, name='player_profile'),
    path('comparison/', views.team_comparison, name='team_comparison'),
    path('calendar/', views.calendar_view, name='calendar'),
]