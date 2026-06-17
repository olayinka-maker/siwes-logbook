from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_logbook_pdf(response, user, profile, entries, reports):
    """Generate a professional PDF logbook report."""
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#1a1a2e'),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#16213e'),
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#0f3460'),
        spaceBefore=20,
        spaceAfter=10,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
    )

    # ─── Cover Page ──────────────────────────────────────────
    elements.append(Spacer(1, 2 * inch))
    elements.append(Paragraph("SIWES LOGBOOK", title_style))
    elements.append(Paragraph("Students Industrial Work Experience Scheme", subtitle_style))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(HRFlowable(width="60%", thickness=2, color=HexColor('#0f3460')))
    elements.append(Spacer(1, 0.5 * inch))

    # Student info table
    info_data = [
        ['Student Name:', user.get_full_name()],
        ['Matric Number:', profile.matric_number or 'N/A'],
        ['Department:', profile.department or 'N/A'],
        ['Institution:', profile.institution or 'N/A'],
        ['Company:', profile.company_name or 'N/A'],
        ['Training Period:',
         f"{profile.training_start_date or 'N/A'} to {profile.training_end_date or 'N/A'}"],
    ]

    info_table = Table(info_data, colWidths=[2.5 * inch, 4 * inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#333333')),
        ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#1a1a2e')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)

    elements.append(PageBreak())

    # ─── Daily Entries ───────────────────────────────────────
    elements.append(Paragraph("DAILY LOGBOOK ENTRIES", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e0e0e0')))
    elements.append(Spacer(1, 0.3 * inch))

    if entries:
        for entry in entries:
            # Entry header
            entry_header = ParagraphStyle(
                'EntryHeader',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=HexColor('#0f3460'),
                spaceBefore=15,
                spaceAfter=5,
            )
            status_color = '#27ae60' if entry.status == 'approved' else (
                '#e74c3c' if entry.status == 'rejected' else '#f39c12'
            )

            elements.append(Paragraph(
                f"Day {entry.day_number} — {entry.date.strftime('%A, %d %B %Y')} "
                f"<font color='{status_color}'>[{entry.status.upper()}]</font>",
                entry_header
            ))
            elements.append(Paragraph(f"<b>{entry.title}</b>", body_style))
            elements.append(Spacer(1, 0.1 * inch))

            elements.append(Paragraph("<b>Activities:</b>", label_style))
            elements.append(Paragraph(entry.activities, body_style))
            elements.append(Spacer(1, 0.1 * inch))

            if entry.skills_acquired:
                elements.append(Paragraph("<b>Skills Acquired:</b>", label_style))
                elements.append(Paragraph(entry.skills_acquired, body_style))
                elements.append(Spacer(1, 0.1 * inch))

            if entry.challenges:
                elements.append(Paragraph("<b>Challenges:</b>", label_style))
                elements.append(Paragraph(entry.challenges, body_style))
                elements.append(Spacer(1, 0.1 * inch))

            if entry.supervisor_comment:
                elements.append(Paragraph("<b>Supervisor Comment:</b>", label_style))
                elements.append(Paragraph(entry.supervisor_comment, body_style))

            elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e0e0e0')))
    else:
        elements.append(Paragraph("No daily entries recorded yet.", body_style))

    elements.append(PageBreak())

    # ─── Weekly Reports ──────────────────────────────────────
    elements.append(Paragraph("WEEKLY REPORTS", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e0e0e0')))
    elements.append(Spacer(1, 0.3 * inch))

    if reports:
        for report in reports:
            report_header = ParagraphStyle(
                'ReportHeader',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=HexColor('#0f3460'),
                spaceBefore=15,
                spaceAfter=5,
            )
            elements.append(Paragraph(
                f"Week {report.week_number} — "
                f"{report.start_date.strftime('%d %b')} to {report.end_date.strftime('%d %b %Y')}",
                report_header
            ))

            elements.append(Paragraph("<b>Summary:</b>", label_style))
            elements.append(Paragraph(report.summary, body_style))
            elements.append(Spacer(1, 0.1 * inch))

            if report.achievements:
                elements.append(Paragraph("<b>Achievements:</b>", label_style))
                elements.append(Paragraph(report.achievements, body_style))
                elements.append(Spacer(1, 0.1 * inch))

            if report.problems_encountered:
                elements.append(Paragraph("<b>Problems Encountered:</b>", label_style))
                elements.append(Paragraph(report.problems_encountered, body_style))
                elements.append(Spacer(1, 0.1 * inch))

            if report.plans_for_next_week:
                elements.append(Paragraph("<b>Plans for Next Week:</b>", label_style))
                elements.append(Paragraph(report.plans_for_next_week, body_style))

            if report.supervisor_comment:
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph("<b>Supervisor Comment:</b>", label_style))
                elements.append(Paragraph(report.supervisor_comment, body_style))

            elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e0e0e0')))
    else:
        elements.append(Paragraph("No weekly reports recorded yet.", body_style))

    # Build PDF
    doc.build(elements)
