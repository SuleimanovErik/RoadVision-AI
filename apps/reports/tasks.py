from celery import shared_task
from django.core.files.base import ContentFile
from .models import Report
from .services import generate_defects_pdf
from apps.defects.models import Defect


@shared_task
def generate_report_task(report_id: int, filters: dict = None) -> None:
    try:
        report = Report.objects.get(pk=report_id)
        defects = Defect.objects.filter(**(filters or {}))
        pdf_bytes = generate_defects_pdf(defects)
        filename = f"report_{report_id}.pdf"
        report.file.save(filename, ContentFile(pdf_bytes), save=False)
        report.status = Report.Status.DONE
        report.save(update_fields=["file", "status"])
    except Exception as e:
        Report.objects.filter(pk=report_id).update(
            status=Report.Status.ERROR,
            error_message=str(e),
        )