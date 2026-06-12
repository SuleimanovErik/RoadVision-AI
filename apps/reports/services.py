import io
from datetime import datetime
from pathlib import Path

from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from apps.defects.models import Defect


# ====================== РЕГИСТРАЦИЯ ШРИФТА ======================
def register_cyrillic_fonts():
    # Надёжный поиск шрифта
    font_paths = [
        Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans.ttf",
        Path(settings.BASE_DIR) / "staticfiles" / "fonts" / "DejaVuSans.ttf",
        Path("static/fonts/DejaVuSans.ttf"),
    ]

    font_path = None
    for path in font_paths:
        if path.exists():
            font_path = str(path)
            break

    if not font_path:
        return  # silently fail

    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        registerFontFamily(
            'DejaVuSans',
            normal='DejaVuSans',
            bold='DejaVuSans',
            italic='DejaVuSans',
            boldItalic='DejaVuSans'
        )
    except Exception:
        pass  # silently fail


# Регистрируем при импорте модуля
register_cyrillic_fonts()


SEVERITY_COLORS = {
    "high": colors.HexColor("#FF4444"),
    "medium": colors.HexColor("#FFA500"),
    "low": colors.HexColor("#4CAF50"),
}


def generate_defects_pdf(queryset=None) -> bytes:
    """Генерирует PDF отчёт по дефектам."""
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
        fontName="DejaVuSans",
        fontSize=18,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="DejaVuSans",
        fontSize=14,
        spaceAfter=12,
    )

    story = []

    # Заголовок
    story.append(Paragraph("Отчёт по дефектам дорожного покрытия", title_style))
    story.append(Paragraph(
        f"Сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        subtitle_style
    ))
    story.append(Spacer(1, 0.8 * cm))

    if queryset is None:
        queryset = Defect.objects.all()

    # Статистика
    total = queryset.count()
    high = queryset.filter(severity="high").count()
    medium = queryset.filter(severity="medium").count()
    low = queryset.filter(severity="low").count()

    stats_data = [
        ["Всего дефектов", "High", "Medium", "Low"],
        [str(total), str(high), str(medium), str(low)],
    ]

    stats_table = Table(stats_data, colWidths=[4.5 * cm] * 4)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 1 * cm))

    # Таблица дефектов
    story.append(Paragraph("Список дефектов", heading_style))
    story.append(Spacer(1, 0.4 * cm))

    headers = ["#", "Тип дефекта", "Широта", "Долгота", "Уверенность", "Серьёзность", "Дата создания"]

    defects = list(queryset.order_by("-confidence")[:5000])

    table_data = [headers]
    for i, defect in enumerate(defects, start=1):
        table_data.append([
            str(i),
            str(getattr(defect, 'defect_type', '-')),
            f"{defect.latitude:.6f}",
            f"{defect.longitude:.6f}",
            f"{defect.confidence * 100:.1f}%",
            defect.get_severity_display() or "-",
            defect.created_at.strftime("%d.%m.%Y %H:%M"),
        ])

    col_widths = [0.8 * cm, 4.5 * cm, 3 * cm, 3 * cm, 2.5 * cm, 2.8 * cm, 2.8 * cm]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
    ])

    table.setStyle(table_style)

    # Цвета по серьёзности
    for row_idx, defect in enumerate(defects, start=1):
        color = SEVERITY_COLORS.get(getattr(defect, 'severity', ''), colors.black)
        severity_style = TableStyle([
            ("TEXTCOLOR", (5, row_idx), (5, row_idx), color),
        ])
        table.setStyle(severity_style)

    story.append(table)
    doc.build(story)

    return buffer.getvalue()