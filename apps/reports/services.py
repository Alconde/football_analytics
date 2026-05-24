import logging
import textwrap
import uuid
from io import BytesIO
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from pptx.util import Inches
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from pptx import Presentation

from apps.matches.models import Match
from .models import GeneratedReport

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

logger = logging.getLogger(__name__)


class ReportGenerationService:
    @classmethod
    def generate_report(cls, report: GeneratedReport) -> GeneratedReport:
        summary = cls.generate_summary(report)
        buffer = cls._build_file_buffer(report, summary)
        file_name = cls._build_file_name(report)

        report.summary = summary
        report.file.save(file_name, ContentFile(buffer.getvalue()), save=False)
        report.save()
        return report

    @classmethod
    def generate_summary(cls, report: GeneratedReport) -> str:
        if report.match and report.match.is_finished:
            context = cls._build_match_context(report.match)
        else:
            context = cls._build_report_context(report)

        if settings.OPENAI_API_KEY and openai:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                prompt = cls._build_prompt(report, context)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Eres un asistente de informes de fútbol que genera resúmenes claros, compactos y accionables en español.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                generated_text = response.choices[0].message.content.strip()
                if generated_text:
                    return generated_text
            except Exception as exc:
                logger.warning("OpenAI summary generation failed: %s", exc)

        return cls._build_fallback_summary(report, context)

    @classmethod
    def _build_prompt(cls, report: GeneratedReport, context: str) -> str:
        prompt = [
            f"Genera un resumen ejecutivo para el siguiente informe de fútbol:",
            f"Tipo de informe: {report.get_report_type_display()}",
        ]

        if report.match:
            prompt.append(f"Partido: {report.match}")
        if report.team:
            prompt.append(f"Equipo principal: {report.team}")
        if report.player:
            prompt.append(f"Jugador principal: {report.player}")

        prompt.append("Contexto:")
        prompt.append(context)
        prompt.append(
            "Escribe un resumen de 4 a 6 líneas en español que incluya hallazgos clave y recomendaciones básicas."
        )
        return "\n".join(prompt)

    @classmethod
    def _build_report_context(cls, report: GeneratedReport) -> str:
        context_lines = []
        if report.team:
            context_lines.append(f"Equipo objetivo: {report.team}")
        if report.player:
            context_lines.append(f"Jugador objetivo: {report.player}")
        if report.match:
            context_lines.append(cls._build_match_context(report.match))
        return "\n".join(context_lines)

    @classmethod
    def _build_match_context(cls, match: Match) -> str:
        lines = [
            f"Partido: {match.home_team} vs {match.away_team}",
            f"Fecha: {match.match_date:%d/%m/%Y}",
            f"Resultado: {match.display_score}",
        ]

        home_stats = match.team_stats.filter(team=match.home_team).first()
        away_stats = match.team_stats.filter(team=match.away_team).first()

        if home_stats and away_stats:
            lines.extend([
                f"Posesión: {match.home_team} {home_stats.possession_pct or 0}% vs {match.away_team} {away_stats.possession_pct or 0}%.",
                f"xG: {match.home_team} {home_stats.xg or 0} vs {match.away_team} {away_stats.xg or 0}.",
                f"PPDA: {match.home_team} {home_stats.ppda or 0} vs {match.away_team} {away_stats.ppda or 0}.",
                f"Pases: {match.home_team} {home_stats.passes} vs {match.away_team} {away_stats.passes}.",
            ])

        top_kpis = match.kpis.select_related("kpi_type").order_by("-value")[:4]
        if top_kpis:
            lines.append("KPIs destacados:")
            for kpi in top_kpis:
                lines.append(f"  - {kpi.kpi_type.name}: {float(kpi.value):.2f} {kpi.kpi_type.unit}")

        return "\n".join(lines)

    @classmethod
    def _build_fallback_summary(cls, report: GeneratedReport, context: str) -> str:
        title = report.title or report.get_report_type_display()
        lines = [f"{title}", ""]

        if report.match and report.match.is_finished:
            match = report.match
            lines.append(f"El partido finalizó {match.display_score}.")
            winner = None
            if match.home_score is not None and match.away_score is not None:
                if match.home_score > match.away_score:
                    winner = match.home_team
                elif match.away_score > match.home_score:
                    winner = match.away_team
                else:
                    winner = "empate"
            if winner:
                lines.append(f"Resultado destacado: {winner} obtuvo el resultado más relevante.")

            home_stats = match.team_stats.filter(team=match.home_team).first()
            away_stats = match.team_stats.filter(team=match.away_team).first()
            if home_stats and away_stats:
                lines.extend([
                    f"{match.home_team} dominó la posesión con {home_stats.possession_pct or 0}% frente a {away_stats.possession_pct or 0}%.",
                    f"xG relevante: {match.home_team} {home_stats.xg or 0} vs {match.away_team} {away_stats.xg or 0}.",
                ])

        if report.team:
            lines.append(f"El informe se centra en el equipo {report.team}.")
        if report.player:
            lines.append(f"Se incluye al jugador {report.player} como referencia de análisis individual.")

        if not any([report.match, report.team, report.player]):
            lines.append("No hay datos adicionales disponibles para generar un resumen detallado.")

        lines.append("Recomendación: revisar los datos de rendimiento y priorizar áreas de mejora tácticas.")
        return "\n".join(lines)

    @classmethod
    def _build_file_buffer(cls, report: GeneratedReport, summary: str) -> BytesIO:
        file_type = report.file_type.lower()
        if file_type == GeneratedReport.FileType.PDF:
            return cls._build_pdf(summary)
        if file_type == GeneratedReport.FileType.PPTX:
            return cls._build_pptx(report.title, summary)
        if file_type == GeneratedReport.FileType.XLSX:
            return cls._build_xlsx(report.title, summary)
        raise ValueError(f"Formato de archivo no soportado: {file_type}")

    @classmethod
    def _build_file_name(cls, report: GeneratedReport) -> str:
        label = slugify(report.title or report.get_report_type_display())[:50] or "informe"
        return f"{label}-{uuid.uuid4().hex[:8]}.{report.file_type}"

    @classmethod
    def _build_pdf(cls, summary: str) -> BytesIO:
        buffer = BytesIO()
        document = canvas.Canvas(buffer, pagesize=letter)
        document.setTitle("Informe automático")
        document.setFont("Helvetica-Bold", 16)
        document.drawString(40, 760, "Informe de análisis")
        text = document.beginText(40, 730)
        text.setFont("Helvetica", 10)

        for line in textwrap.wrap(summary, width=90):
            if text.getY() < 40:
                document.drawText(text)
                document.showPage()
                text = document.beginText(40, 760)
                text.setFont("Helvetica", 10)
            text.textLine(line)

        document.drawText(text)
        document.save()
        buffer.seek(0)
        return buffer

    @classmethod
    def _build_pptx(cls, title: str, summary: str) -> BytesIO:
        presentation = Presentation()
        slide_layout = presentation.slide_layouts[5] if len(presentation.slide_layouts) > 5 else presentation.slide_layouts[0]
        slide = presentation.slides.add_slide(slide_layout)

        if slide.shapes.title:
            slide.shapes.title.text = title or "Informe de análisis"

        left = Inches(0.5)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(5)
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.text = ""

        for line in summary.splitlines():
            paragraph = text_frame.add_paragraph()
            paragraph.text = line

        buffer = BytesIO()
        presentation.save(buffer)
        buffer.seek(0)
        return buffer

    @classmethod
    def _build_xlsx(cls, title: str, summary: str) -> BytesIO:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Informe"
        sheet["A1"] = title or "Informe de análisis"
        sheet["A2"] = "Resumen"

        for index, line in enumerate(summary.splitlines(), start=3):
            sheet.cell(row=index, column=1, value=line)

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return buffer
