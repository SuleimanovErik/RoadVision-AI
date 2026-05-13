import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from apps.defects.models import Defect


SEVERITY_COLORS = {
    "high":   colors.HexColor("#FF4444"),
    "medium": colors.HexColor("#FFA500"),
    "low":    colors.HexColor("#4CAF50"),
}


def generate_defects_pdf(queryset=None) -> bytes:
    """Генерирует PDF отчёт по дефектам. Возвращает байты PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    story = []

    # Заголовок
    story.append(Paragraph("Отчёт по дефектам дорожного покрытия", title_style))
    story.append(Paragraph(
        f"Сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        subtitle_style
    ))

    # Статистика
    if queryset is None:
        queryset = Defect.objects.all()

    total = queryset.count()
    high = queryset.filter(severity="high").count()
    medium = queryset.filter(severity="medium").count()
    low = queryset.filter(severity="low").count()

    stats_data = [
        ["Всего дефектов", "Высокая", "Средняя", "Низкая"],
        [str(total), str(high), str(medium), str(low)],
    ]
    stats_table = Table(stats_data, colWidths=[4 * cm] * 4)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWHEIGHT", (0, 0), (-1, -1), 25),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#FFEBEB")),
        ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#FFF3E0")),
        ("BACKGROUND", (3, 1), (3, 1), colors.HexColor("#E8F5E9")),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.5 * cm))

    # Таблица дефектов
    story.append(Paragraph("Список дефектов", styles["Heading2"]))
    story.append(Spacer(1, 0.3 * cm))

    headers = ["#", "Тип дефекта", "Широта", "Долгота", "Уверенность", "Серьёзность", "Дата"]
    table_data = [headers]

    for i, defect in enumerate(queryset.order_by("-confidence"), start=1):
        table_data.append([
            str(i),
            defect.defect_type,
            f"{defect.latitude:.6f}",
            f"{defect.longitude:.6f}",
            f"{defect.confidence * 100:.1f}%",
            defect.get_severity_display(),
            defect.created_at.strftime("%d.%m.%Y"),
        ])

    col_widths = [1*cm, 3.5*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm, 2.5*cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    row_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWHEIGHT", (0, 0), (-1, -1), 20),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]

    # Цвет строки по серьёзности
    for i, defect in enumerate(queryset.order_by("-confidence"), start=1):
        color = SEVERITY_COLORS.get(defect.severity, colors.white)
        row_styles.append(("TEXTCOLOR", (5, i), (5, i), color))
        row_styles.append(("FONTNAME", (5, i), (5, i), "Helvetica-Bold"))

    table.setStyle(TableStyle(row_styles))
    story.append(table)

    doc.build(story)
    return buffer.getvalue()