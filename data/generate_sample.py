"""Generates a 4-page fictional clinical policy document for 'Noor Care Clinic'.

Contains exact ground-truth facts for testing RAG retrieval and evaluation:
- Page 1: Operating hours (Friday 9-1 and 3-8, Sunday closed)
- Page 2: Consultation fees (General PKR 1,500, Pediatric 1,200, Specialist 3,000) & Cancellation (12 hrs, PKR 500)
- Page 3: Laboratory services (CBC within 4 hours, fasting requirements)
- Page 4: Medical records copy (3 working days, PKR 300) & Refill policies
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle


def create_clinic_faq_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ClinicTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "ClinicHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "ClinicBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    story = []

    # -------------------------------------------------------------------------
    # PAGE 1: Clinic Overview & Operating Hours
    # -------------------------------------------------------------------------
    story.append(Paragraph("Noor Care Clinic — Patient Guidelines & Policies", title_style))
    story.append(Paragraph("Document Version: 2026.1 | Effective: January 1, 2026", body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1. General Information & Operating Hours", heading_style))
    story.append(Paragraph(
        "Welcome to Noor Care Clinic. We are a multi-specialty outpatient healthcare facility dedicated "
        "to providing accessible and compassionate clinical care to our community.",
        body_style
    ))
    story.append(Paragraph("Our operating schedule is as follows:", body_style))
    
    hours_data = [
        ["Day", "Operating Hours", "Departments Open"],
        ["Monday – Thursday", "8:00 AM – 8:00 PM", "All Outpatient Clinics & Laboratory"],
        ["Friday", "9:00 AM – 1:00 PM & 3:00 PM – 8:00 PM", "General OPD & Diagnostics (Closed for Juma 1-3 PM)"],
        ["Saturday", "9:00 AM – 2:00 PM", "General OPD & Routine Labs Only"],
        ["Sunday", "Closed", "Emergency cases redirected to City Hospital"],
    ]
    t_hours = Table(hours_data, colWidths=[120, 200, 180])
    t_hours.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EBF8FF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(t_hours)
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Emergency Protocols:</b> Noor Care Clinic is an ambulatory outpatient center. "
                           "We do not operate an inpatient ICU or acute trauma bay. In life-threatening emergencies, "
                           "patients must proceed immediately to the nearest tertiary emergency department.", body_style))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # PAGE 2: Consultation Fees & Cancellation Policy
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Consultation Fee Schedule & Appointment Policies", heading_style))
    story.append(Paragraph("All consultations require prior scheduling or same-day token allocation at the reception desk. "
                           "Payment is collected at check-in prior to seeing the physician.", body_style))
    
    fee_data = [
        ["Consultation Type", "Fee (PKR)", "Standard Duration"],
        ["General Physician Consultation", "PKR 1,500", "15 minutes"],
        ["Pediatric Consultation", "PKR 1,200", "20 minutes"],
        ["Specialist Consultation (Cardiology, Dermatology)", "PKR 3,000", "25 minutes"],
        ["Follow-up Visit (within 7 days)", "Complimentary / PKR 0", "10 minutes"],
    ]
    t_fee = Table(fee_data, colWidths=[220, 130, 150])
    t_fee.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EBF8FF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(t_fee)
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("<b>Appointment Cancellation & Rescheduling:</b>", heading_style))
    story.append(Paragraph(
        "Patients may reschedule or cancel their appointment without penalty by providing at least "
        "<b>12 hours notice</b> prior to the scheduled slot. Cancellations made with less than 12 hours notice, "
        "or no-show appointments, will incur a <b>cancellation fee of PKR 500</b>, which must be settled "
        "before booking any future consultations.",
        body_style
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # PAGE 3: Laboratory & Diagnostic Turnaround
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Diagnostic Services & Laboratory Turnaround Times", heading_style))
    story.append(Paragraph("Our on-site clinical pathology laboratory is ISO-15189 certified. "
                           "Phlebotomy is conducted daily from 8:00 AM to 12:00 PM.", body_style))
    
    lab_data = [
        ["Diagnostic Test", "Fasting Required", "Report Turnaround Time"],
        ["Complete Blood Count (CBC)", "None", "Within 4 hours"],
        ["Fasting Blood Sugar (FBS)", "8 - 10 hours", "Within 2 hours"],
        ["Lipid Profile", "12 hours water-only fasting", "Within 6 hours"],
        ["Thyroid Profile (TSH, FT3, FT4)", "None", "Same day by 7:00 PM"],
    ]
    t_lab = Table(lab_data, colWidths=[180, 150, 170])
    t_lab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EBF8FF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(t_lab)
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "For Complete Blood Count (CBC), automated results are validated by the on-duty pathologist "
        "and made available online or via reception strictly <b>within 4 hours</b> of sample collection.",
        body_style
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # PAGE 4: Medical Records & Refill Protocols
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Medical Records & Prescription Management", heading_style))
    story.append(Paragraph(
        "<b>Medical Records Copy Requests:</b> Patients requesting a physical certified copy of their medical "
        "records, diagnostic reports, or discharge summaries must submit a formal written request along with a "
        "valid government-issued photo ID. Processing time is strictly <b>3 working days</b>. An administrative "
        "processing fee of <b>PKR 300</b> applies per request.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Prescription Refill Policy:</b> Chronic medication refill requests must be submitted at least 24 hours "
        "prior to running out of medication. Controlled substances and psychiatric medications cannot be refilled "
        "over the phone and require an in-person clinical review every 90 days.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Patient Confidentiality Notice:</b> In compliance with healthcare data protection standards, records are "
        "never disclosed to third parties or employers without explicit, signed patient authorization.",
        body_style
    ))

    doc.build(story)
    print(f"Successfully generated 4-page PDF at: {output_path}")


if __name__ == "__main__":
    out = Path("data/sample_docs/clinic_faq.pdf")
    create_clinic_faq_pdf(out)
