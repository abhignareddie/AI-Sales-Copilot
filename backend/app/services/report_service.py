import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportService:
    """Enterprise report generator producing high quality styled PDF documents."""
    
    @classmethod
    def generate_executive_pdf(cls, company_name: str, score: float, recommendations: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=15
        )
        
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=8
        )

        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#111827'),
            spaceAfter=10
        )

        # Content
        story.append(Paragraph(f"AI Sales Copilot - Executive Report", title_style))
        story.append(Paragraph(f"<b>Target Account:</b> {company_name}", body_style))
        story.append(Paragraph(f"<b>Account Health Index:</b> {score}%", body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("Next Best Action Matrix", h2_style))
        
        # Table data
        data = [["ID", "Priority", "NBA Action Item", "ROI", "Confidence"]]
        for idx, rec in enumerate(recommendations, 1):
            data.append([
                str(idx),
                rec.get("priority", "HIGH").upper(),
                rec.get("recommendation", ""),
                f"${rec.get('roi', 0.0):,.0f}",
                f"{int(rec.get('confidence', 0.0) * 100)}%"
            ])
            
        t = Table(data, colWidths=[30, 60, 270, 70, 70])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9fafb')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f3f4f6')]),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Compliance & Security Statement:</b> Generated with full explainability traces and auditable approval workflows. Designed aligned to SOC2/GDPR frameworks.", body_style))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
