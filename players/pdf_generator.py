import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def format_inr(val):
    try:
        num = int(val)
        return f"Rs. {num:,}"
    except (ValueError, TypeError):
        return "Rs. 0"

def generate_team_pdf(team, players):
    """
    Generate an official, professional PDF roster for a single team.
    Returns: bytes of PDF document.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )

    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )

    league_desc_style = ParagraphStyle(
        'LeagueDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748b')
    )

    team_heading_style = ParagraphStyle(
        'TeamHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a')
    )

    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    cell_bold_style = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    )

    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("HTPL CRICKET LEAGUE &bull; SEASON 1", title_style))
    story.append(Paragraph("MALLINAMADUGU PANCHAYATH PREMIER CHAMPIONSHIP 2026", sub_title_style))
    story.append(Paragraph("Official Team Squad &amp; Auction Expenditure Statement", league_desc_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=14))

    # Calculate financial totals
    team_players = [p for p in players if getattr(p, 'team', '') == team.name]
    total_budget = int(getattr(team, 'total_budget', 100000))
    total_spent = sum(int(getattr(p, 'bid_amount', 0) or 0) for p in team_players)
    remaining_balance = total_budget - total_spent

    batsmen_count = sum(1 for p in team_players if getattr(p, 'role', '') == 'Batsman')
    bowler_count = sum(1 for p in team_players if getattr(p, 'role', '') == 'Bowler')
    ar_count = sum(1 for p in team_players if getattr(p, 'role', '') == 'All-Rounder')

    # 2. Team Information & Financial Summary Box
    summary_data = [
        [
            Paragraph(f"<b>Team Name:</b> {team.name}", cell_style),
            Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", cell_style)
        ],
        [
            Paragraph(f"<b>Total Purse (Budget):</b> <font color='#0f172a'><b>{format_inr(total_budget)}</b></font>", cell_style),
            Paragraph(f"<b>Amount Spent:</b> <font color='#dc2626'><b>{format_inr(total_spent)}</b></font>", cell_style)
        ],
        [
            Paragraph(f"<b>Remaining Balance:</b> <font color='#059669'><b>{format_inr(remaining_balance)}</b></font>", cell_style),
            Paragraph(f"<b>Squad Size:</b> <b>{len(team_players)} Players</b> (Bat: {batsmen_count} | Bowl: {bowler_count} | AR: {ar_count})", cell_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[260, 260])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    # 3. Squad Heading
    story.append(Paragraph(f"Players List &bull; {team.name} Squad ({len(team_players)})", team_heading_style))
    story.append(Spacer(1, 8))

    # 4. Players Table
    table_data = [
        [
            Paragraph("#", header_cell_style),
            Paragraph("Player Name", header_cell_style),
            Paragraph("Role", header_cell_style),
            Paragraph("Amount Spent", header_cell_style),
            Paragraph("Village", header_cell_style),
            Paragraph("Phone Number", header_cell_style),
        ]
    ]

    if not team_players:
        table_data.append([
            Paragraph("—", cell_style),
            Paragraph("<i>No players acquired yet for this team.</i>", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
        ])
    else:
        for idx, p in enumerate(team_players, 1):
            p_name = getattr(p, 'name', '') or f"{getattr(p, 'first_name', '')} {getattr(p, 'last_name', '')}".strip()
            p_role = getattr(p, 'role', '') or getattr(p, 'primary_role', '') or 'All-Rounder'
            p_amt = format_inr(getattr(p, 'bid_amount', 0) or 0)
            p_village = getattr(p, 'village', '') or getattr(p, 'city', '') or 'Mallinamadugu'
            p_phone = getattr(p, 'phone', '') or '—'

            table_data.append([
                Paragraph(str(idx), ParagraphStyle('CenterNum', parent=cell_style, alignment=TA_CENTER)),
                Paragraph(f"<b>{p_name}</b>", cell_bold_style),
                Paragraph(p_role, cell_style),
                Paragraph(f"<font color='#dc2626'><b>{p_amt}</b></font>", cell_style),
                Paragraph(p_village, cell_style),
                Paragraph(p_phone, cell_style),
            ])

    # Table styling
    # Total printable width on A4 with 36pt margins = 595.27 - 72 = 523.27
    col_widths = [28, 140, 85, 90, 95, 85]
    roster_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]

    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))

    roster_table.setStyle(TableStyle(t_style))
    story.append(roster_table)
    story.append(Spacer(1, 14))

    # 5. Financial Summary Total Row
    tot_data = [
        [
            Paragraph("<b>TOTAL SQUAD EXPENDITURE</b>", cell_style),
            Paragraph(f"<font color='#dc2626'><b>{format_inr(total_spent)}</b></font>", cell_style),
            Paragraph("<b>REMAINING TEAM PURSE</b>", cell_style),
            Paragraph(f"<font color='#059669'><b>{format_inr(remaining_balance)}</b></font>", cell_style),
        ]
    ]
    tot_table = Table(tot_data, colWidths=[160, 100, 160, 103])
    tot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tot_table)

    # 6. Signatures and Verification
    story.append(Spacer(1, 35))
    sig_data = [
        [
            Paragraph("&nbsp;<br/>_______________________________<br/><b>Team Captain / Owner Signature</b><br/>" + team.name, cell_style),
            Paragraph("&nbsp;<br/>_______________________________<br/><b>HTPL Governing Council Official</b><br/>Mallinamadugu Panchayath", cell_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether(sig_table))

    # 7. Document Footer
    story.append(Spacer(1, 20))
    footer_text = Paragraph(
        "&copy; 2026 HTPL League Official Tournament Portal. All Rights Reserved. Verified by Mallinamadugu Cricket Committee.",
        ParagraphStyle('FooterNotice', parent=styles['Normal'], fontSize=7.5, leading=10, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)
    )
    story.append(footer_text)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
