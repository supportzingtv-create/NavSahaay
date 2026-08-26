from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

def build_receipt(donation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()
    title = styles["Title"]; title.alignment = TA_CENTER
    story = [Paragraph("SHIVOHAM FOUNDATION", title),
             Paragraph("Donation Receipt", styles["Heading2"]), Spacer(1, 20)]
    data = [
        ["Receipt Number", donation.receipt_number or "Pending verification"],
        ["Donation ID", donation.donation_id],
        ["Donor", "Anonymous Donor" if donation.anonymous else donation.donor_name],
        ["Amount", f"₹ {donation.amount:,.2f}"],
        ["Frequency", donation.frequency],
        ["Cause", donation.cause],
        ["Status", donation.status],
        ["Date", donation.created_at.strftime("%d %b %Y") if donation.created_at else ""],
    ]
    table = Table(data, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.whitesmoke),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("PADDING",(0,0),(-1,-1),8),
    ]))
    story += [table, Spacer(1,20),
              Paragraph("This locally generated receipt is a technical prototype. Publish 80G/tax-deductibility information only after verifying Shivoham's current registration and legal status.", styles["BodyText"])]
    doc.build(story)
    buffer.seek(0)
    return buffer
