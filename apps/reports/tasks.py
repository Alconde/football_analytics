import logging
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import GeneratedReport

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_report_async(self, report_id):
    """
    Genera un informe de análisis de forma asincrónica.
    
    Esta tarea se ejecuta en background usando Celery.
    Si falla, se reintenta hasta 3 veces.
    
    Args:
        report_id: ID del GeneratedReport a procesar
    """
    try:
        # 1. Obtener el informe de la base de datos
        report = GeneratedReport.objects.get(pk=report_id)
        
        # 2. Cambiar estado a 'processing' (está siendo generado)
        report.status = GeneratedReport.Status.PROCESSING
        report.save()
        
        # 3. AQUÍ VA LA LÓGICA DE GENERACIÓN DE INFORME
        # Por ahora es un placeholder. Tú completarás esto después
        
        # Ejemplo de lógica (puedes modificar esto):
        if report.file_type == 'pdf':
            # TODO: Generar PDF con reportlab o similar
            report.file.name = f"reports/report_{report_id}.pdf"
        elif report.file_type == 'pptx':
            # TODO: Generar PowerPoint con python-pptx
            report.file.name = f"reports/report_{report_id}.pptx"
        elif report.file_type == 'xlsx':
            # TODO: Generar Excel con openpyxl
            report.file.name = f"reports/report_{report_id}.xlsx"
        
        # 4. Cambiar estado a 'completed' (finalizado)
        report.status = GeneratedReport.Status.COMPLETED
        report.summary = "Informe generado exitosamente"
        report.save()
        
        # 5. Opcional: enviar email de notificación
        # send_report_email.delay(report_id)
        
        logger.info(f"✅ Informe {report_id} generado exitosamente")
        
    except GeneratedReport.DoesNotExist:
        logger.error(f"❌ Informe {report_id} no encontrado en la BD")
        
    except Exception as exc:
        logger.error(f"❌ Error generando informe {report_id}: {str(exc)}")
        # Reintentar después de 5 minutos
        raise self.retry(exc=exc, countdown=300)


@shared_task
def send_report_email(report_id):
    """
    Envía un email al usuario cuando el informe está listo.
    
    Args:
        report_id: ID del GeneratedReport
    """
    try:
        report = GeneratedReport.objects.get(pk=report_id)
        user = report.generated_by
        
        subject = "Tu informe de análisis está listo"
        message = "El informe ha sido generado correctamente. Puedes descargarlo desde la plataforma."
        
        send_mail(
            subject,
            message,
            'noreply@football-analytics.com',
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"✅ Email enviado a {user.email} para informe {report_id}")
        
    except GeneratedReport.DoesNotExist:
        logger.error(f"❌ Informe {report_id} no encontrado")
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de informe: {str(e)}")