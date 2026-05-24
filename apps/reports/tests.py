from django.test import TestCase
from django.utils import timezone
from django.core.files.base import ContentFile

from apps.clubs.models import Club, Competition, Season, Team
from apps.matches.models import Match, MatchTeamStat
from apps.users.models import User
from apps.reports.models import GeneratedReport
from apps.reports.services import ReportGenerationService


class ReportGenerationServiceTest(TestCase):
    def setUp(self):
        club = Club.objects.create(name="Club A")
        competition = Competition.objects.create(name="Liga de prueba")
        season = Season.objects.create(name="2025", start_date="2025-01-01", end_date="2025-12-31")
        self.team_home = Team.objects.create(club=club, name="Casa")
        self.team_away = Team.objects.create(club=club, name="Visitante")
        self.user = User.objects.create_user(username="analista", password="secret", role=User.Role.DATA_ANALYST)

        self.match = Match.objects.create(
            season=season,
            competition=competition,
            match_date=timezone.now(),
            home_team=self.team_home,
            away_team=self.team_away,
            home_score=2,
            away_score=1,
            status=Match.Status.FINISHED,
        )
        MatchTeamStat.objects.create(
            match=self.match,
            team=self.team_home,
            possession_pct=58.5,
            xg=1.75,
            shots=12,
            shots_on_target=6,
            passes=420,
            pass_accuracy_pct=83.2,
            ppda=8.5,
            recoveries=22,
        )
        MatchTeamStat.objects.create(
            match=self.match,
            team=self.team_away,
            possession_pct=41.5,
            xg=0.95,
            shots=8,
            shots_on_target=3,
            passes=310,
            pass_accuracy_pct=77.1,
            ppda=10.2,
            recoveries=18,
        )

    def test_generate_report_creates_file_and_summary(self):
        report = GeneratedReport.objects.create(
            title="Informe de prueba",
            report_type=GeneratedReport.ReportType.POSTMATCH,
            file_type=GeneratedReport.FileType.PDF,
            match=self.match,
            generated_by=self.user,
            file=ContentFile(b"placeholder", name="placeholder.pdf"),
        )

        generated = ReportGenerationService.generate_report(report)
        self.assertTrue(generated.summary)
        self.assertTrue(generated.file.name.endswith(".pdf"))
        self.assertGreater(len(generated.summary), 20)
