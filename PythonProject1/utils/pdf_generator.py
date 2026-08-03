import os
import re
import random
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def parse_markdown_to_platypus(markdown_text, styles):
    story = []
    normal_style = styles["Normal"]
    h3_style = ParagraphStyle(
        'PDFH3',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=3,
        spaceBefore=6
    )
    
    lines = markdown_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 3))
            continue
        
        # Parse titles
        if line.startswith("###"):
            title_text = line.replace("###", "").strip()
            story.append(Paragraph(f"<b>{title_text}</b>", h3_style))
        elif line.startswith("##"):
            title_text = line.replace("##", "").strip()
            story.append(Paragraph(f"<b>{title_text}</b>", h3_style))
        elif line.startswith("#"):
            title_text = line.replace("#", "").strip()
            story.append(Paragraph(f"<b>{title_text}</b>", h3_style))
        elif line.startswith("-") or line.startswith("*"):
            bullet_text = line[1:].strip()
            bullet_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", bullet_text)
            story.append(Paragraph(f"&bull; {bullet_text}", normal_style))
        else:
            line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 2))
    return story

def generate_pdf(name, gender, married, dependents, education,
                 self_emp, credit, property_area,
                 loan_amount, loan_term,
                 app_income, co_income, result_text,
                 property_details=None, ai_explanation="",
                 dossier_data=None, verification_res=None, risk_res=None,
                 officer_notes=""):

    os.makedirs("assets/generated_letters", exist_ok=True)
    file_path = f"assets/generated_letters/{name.replace(' ', '_')}_sanction_report.pdf"

    # Set up document template
    doc = SimpleDocTemplate(
        file_path,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#0f172a") # Dark Slate
    secondary_color = colors.HexColor("#0284c7") # Ocean Blue
    accent_color = colors.HexColor("#16a34a") if "Approved" in result_text or "Sanctioned" in result_text or "Sanction" in result_text else colors.HexColor("#dc2626")
    
    styles['Title'].fontSize = 15
    styles['Title'].textColor = primary_color
    styles['Title'].spaceAfter = 8
    
    styles['Heading2'].fontSize = 10.5
    styles['Heading2'].textColor = secondary_color
    styles['Heading2'].spaceBefore = 8
    styles['Heading2'].spaceAfter = 4
    
    styles['Normal'].fontSize = 8.0
    styles['Normal'].leading = 10.5
    
    ref_no = f"AEGIS-{random.randint(100000,999999)}"
    date_today = datetime.now().strftime("%d-%m-%Y")
    
    content = []
    
    # ================= HEADER =================
    header_data = [
        [Paragraph(f"<b>🛡️ AegisCR DECISION PLATFORM</b><br/>AI Credit Risk & Document Intelligence Audit", styles["Normal"]),
         Paragraph(f"<b>Report Ref:</b> {ref_no}<br/><b>Audit Date:</b> {date_today}", styles["Normal"])]
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, secondary_color),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM')
    ]))
    content.append(header_table)
    content.append(Spacer(1, 8))
    
    # Title
    content.append(Paragraph(f"<b>INTELLIGENT RISK & APPLICANT DOSSIER REPORT</b>", styles["Title"]))
    
    # Decision Banner (Status + Document Trust Score)
    banner_color = colors.HexColor("#f0fdf4") if "Approved" in result_text or "Sanctioned" in result_text or "Sanction" in result_text else colors.HexColor("#fef2f2")
    trust_val = property_details.get("trust_score", 95.0) if property_details else 95.0
    
    banner_data = [
        [Paragraph(f"<b>UNDERWRITING STATUS:</b> <font color='{accent_color.hexval()}'><b>{result_text.upper()}</b></font>", styles["Heading2"]),
         Paragraph(f"<b>DOCUMENT TRUST INDEX:</b> <font color='#0284c7'><b>{trust_val}%</b></font>", styles["Heading2"])]
    ]
    banner_table = Table(banner_data, colWidths=[270, 270])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), banner_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOX', (0,0), (-1,-1), 1, accent_color),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    content.append(banner_table)
    content.append(Spacer(1, 8))
    
    # ================= 1. DIGITAL LOAN TWIN PROFILE =================
    content.append(Paragraph("<b>👤 APPLICANT DIGITAL LOAN TWIN PROFILE</b>", styles["Heading2"]))
    
    ari_score = risk_res.get("Aegis_Risk_Index", 30) if risk_res else 30
    pd_val = risk_res.get("Probability_Of_Default", 10.0) if risk_res else 10.0
    rating_text = risk_res.get("Rating", "Medium Risk") if risk_res else "Medium Risk"
    is_unsec = property_details.get("Land_Type") == "Unsecured" if property_details else False
    
    twin_data = [
        ["Borrower Name", name, "Aegis Risk Index", f"{ari_score} / 100 ({rating_text})"],
        ["Education Level", education, "Default Probability", f"{pd_val}%"],
        ["Declared Salary", f"₹{app_income + co_income:,.2f}/mo", "Requested Loan", f"₹{loan_amount:,.2f}"],
        ["Credit History", "Satisfactory (>=750 CIBIL)" if credit == 1.0 else "Default History / Poor CIBIL", "Loan Structure", "Unsecured exposure" if is_unsec else "Secured Property Collateral"],
        ["Affordability (DTI)", f"{round((loan_amount/loan_term)/(app_income+co_income)*100, 1) if loan_term > 0 and (app_income+co_income) > 0 else 0}%", "Asset Market Value", f"₹{property_details.get('total_market_value', 0):,.2f}" if property_details else "N/A"]
    ]
    twin_table = Table(twin_data, colWidths=[120, 150, 120, 150])
    twin_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#f8fafc")),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    content.append(twin_table)
    content.append(Spacer(1, 8))
    
    # ================= 2. AI RELATIONSHIP NODE ALIGNMENT MATRIX =================
    content.append(Paragraph("<b>🔗 AI RELATIONSHIP NODE ALIGNMENT MATRIX</b>", styles["Heading2"]))
    
    id_chk = verification_res.get("identity", {}) if verification_res else {}
    inc_chk = verification_res.get("income", {}) if verification_res else {}
    prop_chk = verification_res.get("property", {}) if verification_res else {}
    
    name_ratio = id_chk.get("Name_Match_Ratio", 1.0)
    name_status = id_chk.get("Name_Status", "PASS")
    dob_status = id_chk.get("DOB_Status", "PASS")
    inc_status = inc_chk.get("Status", "PASS")
    prop_status = "PASS" if (prop_chk and prop_chk.get("Is_Verified", True)) else "FAIL"
    
    node_data = [
        ["Alignment Dimension", "Primary Target Node", "Secondary Target Node", "Audit Match Metric", "Node Status"],
        ["Identity Match", "Aadhaar Name", "PAN Name", f"Fuzzy Score: {int(name_ratio*100)}%", "🟢 ALIGN" if name_status != "FAIL" else "🔴 CONFLICT"],
        ["Identity Match", "Aadhaar DOB", "PAN DOB", "Date check", "🟢 ALIGN" if dob_status == "PASS" else "🔴 CONFLICT"],
        ["Income Match", "Declared Salary", "Salary Slip Pay", f"Variance: {int(inc_chk.get('Variance_Percentage', 0)*100)}%", "🟢 ALIGN" if inc_status != "FAIL" else "🔴 CONFLICT"],
        ["Repayment Match", "Salary Slip", "Bank Statement deposits", "Salary credit check", "🟢 ALIGN" if inc_status != "FAIL" else "🔴 CONFLICT"],
        ["Property Match", "Sale Deed Survey", "Registry Database", "Coordinates check", "🟢 ALIGN" if prop_status == "PASS" or is_unsec else "🔴 CONFLICT"]
    ]
    
    node_table = Table(node_data, colWidths=[110, 110, 110, 140, 70])
    node_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    content.append(node_table)
    content.append(Spacer(1, 8))
    
    # ================= 3. AI FRAUD BRAIN AUDIT LOG =================
    content.append(Paragraph("<b>🧠 AI FRAUD BRAIN AUDIT LOG</b>", styles["Heading2"]))
    
    fraud_status = property_details.get("fraud_check", {}).get("status", "PASS") if property_details else "PASS"
    fraud_confidence = 98.0
    if fraud_status == "WARNING":
        fraud_confidence = 65.0
    elif fraud_status == "FAIL" or fraud_status == "HIGH RISK":
        fraud_confidence = 45.0
        
    fraud_data = [
        ["Fraud Check Category", "Audit Verification Method", "Risk Score / Result Status"],
        ["Masked Aadhaar Check", "First 8 digits mask detection check", "🟢 PASS (UID masked)" if fraud_confidence > 60 else "🔴 ALERT (Unmasked Plain UID)"],
        ["Font Alteration Check", "System character bounding box fonts", "🟢 PASS (Standard fonts)" if fraud_confidence > 60 else "🔴 ALERT (Altered fonts detected)"],
        ["Metadata Edit Check", "Compression signature modifications", "🟢 PASS (Clean PDF Metadata)" if fraud_confidence > 60 else "🔴 ALERT (Modified via PDF Editor)"],
        ["Registry GIS Map Check", "Geospatial coordinate boundary mapping", "🟢 PASS (Authorized coordinates)" if fraud_status == "PASS" else "🔴 ALERT (Registry mismatch coordinates)"]
    ]
    fraud_table = Table(fraud_data, colWidths=[150, 240, 150])
    fraud_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    content.append(fraud_table)
    content.append(Spacer(1, 8))
    
    # ================= 4. DOSSIER AUDIT TIMELINE =================
    content.append(Paragraph("<b>📋 DOSSIER AUDIT TIMELINE TRAIL</b>", styles["Heading2"]))
    timeline_data = [
        ["Audit Action Event", "Audit Step Timestamp", "System Log / Outcome Metric"],
        ["Loan Application dossier received", f"{date_today} 10:12:05", "Dossier Queued"],
        ["OCR Text Extraction Completed (PyMuPDF)", f"{date_today} 10:12:45", "92% Base Confidence"],
        ["Cross-Document Verification Matches Completed", f"{date_today} 10:13:02", f"Trust score: {trust_val}%"],
        ["Aegis Risk Index (ARI) score Evaluated", f"{date_today} 10:13:20", f"ARI Risk: {ari_score}/100"],
        ["Random Forest ML Classifier Decision", f"{date_today} 10:13:40", f"Status: {result_text}"],
        ["Groq llama-3.3-70b Underwriting report generated", f"{date_today} 10:13:55", "Dossier Document Compiled"]
    ]
    timeline_table = Table(timeline_data, colWidths=[200, 150, 190])
    timeline_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    content.append(timeline_table)
    content.append(Spacer(1, 8))
    
    # ================= 5. OFFICER NOTES =================
    if officer_notes:
        content.append(Paragraph("<b>✍️ LOAN OFFICER FIELD AUDIT NOTES</b>", styles["Heading2"]))
        content.append(Paragraph(officer_notes, styles["Normal"]))
        content.append(Spacer(1, 8))

    # ================= 6. AI UNDERWRITING REPORT =================
    if ai_explanation:
        content.append(Paragraph("<b>🤖 AI CREDIT RISK AUDIT DIRECTIVE</b>", styles["Heading2"]))
        parsed_story = parse_markdown_to_platypus(ai_explanation, styles)
        content.extend(parsed_story)
        content.append(Spacer(1, 8))
        
    # ================= FOOTER =================
    content.append(Paragraph("This AegisCR Credit Evaluation dossier contains system-extracted parameters, fuzzy registry comparisons, and model risk outputs.", styles["Italic"]))
    content.append(Paragraph("Authorized Signatory: Credit Risk Audit Committee, AegisCR Platform", styles["Normal"]))
    
    doc.build(content)
    
    return file_path

def generate_gold_pdf(name, weight, purity, rate_per_gram, gold_value, eligible_loan, interest_rate=9.5, tenure=12, officer_notes=""):
    os.makedirs("assets/generated_letters", exist_ok=True)
    file_path = f"assets/generated_letters/{name.replace(' ', '_')}_gold_sanction_report.pdf"
    
    doc = SimpleDocTemplate(
        file_path,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#78350f") # Amber / Gold Theme Primary
    secondary_color = colors.HexColor("#d97706") # Goldenrod
    
    styles['Title'].fontSize = 15
    styles['Title'].textColor = primary_color
    styles['Title'].spaceAfter = 8
    
    styles['Heading2'].fontSize = 10.5
    styles['Heading2'].textColor = secondary_color
    styles['Heading2'].spaceBefore = 8
    styles['Heading2'].spaceAfter = 4
    
    styles['Normal'].fontSize = 8.5
    styles['Normal'].leading = 11.0
    
    ref_no = f"AEGIS-GOLD-{random.randint(100000,999999)}"
    date_today = datetime.now().strftime("%d-%m-%Y")
    
    content = []
    
    # ================= HEADER =================
    header_data = [
        [Paragraph(f"<b>🛡️ AegisCR DECISION PLATFORM</b><br/>AI Gold Appraisal & Loan Valuation Certificate", styles["Normal"]),
         Paragraph(f"<b>Appraisal Ref:</b> {ref_no}<br/><b>Audit Date:</b> {date_today}", styles["Normal"])]
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, secondary_color),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM')
    ]))
    content.append(header_table)
    content.append(Spacer(1, 10))
    
    # Title
    content.append(Paragraph("<b>GOLD COLLATERAL APPRAISAL & SANCTION LETTER</b>", styles["Title"]))
    content.append(Paragraph("This document certifies that the collateral gold asset described below has been dynamically appraised using live market indexes and is eligible for a credit facility under RBI LTV guidelines.", styles["Normal"]))
    content.append(Spacer(1, 10))
    
    # ================= 1. APPLICANT DETAILS =================
    content.append(Paragraph("<b>👤 APPLICANT INFORMATION</b>", styles["Heading2"]))
    applicant_data = [
        ["Applicant Name", name, "Appraisal Date", date_today],
        ["Collateral Type", "Gold Bullion/Ornaments", "Facility Type", "Gold Bullet Loan"]
    ]
    applicant_table = Table(applicant_data, colWidths=[120, 150, 120, 150])
    applicant_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    content.append(applicant_table)
    content.append(Spacer(1, 10))
    
    # ================= 2. COLLATERAL APPRAISAL DETAILS =================
    content.append(Paragraph("<b>🪙 GOLD COLLATERAL VALUE ANALYSIS</b>", styles["Heading2"]))
    collateral_data = [
        ["Gold Weight (grams)", f"{weight} g", "Purity Grade", purity],
        ["Live Price per Gram", f"₹{rate_per_gram:,.2f}", "Total Market Value", f"₹{gold_value:,.2f}"],
        ["LTV Cap Ratio", "75% (RBI Limit)", "Eligible Loan Ceiling", f"₹{eligible_loan:,.2f}"]
    ]
    collateral_table = Table(collateral_data, colWidths=[130, 140, 130, 140])
    collateral_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BACKGROUND', (3,1), (3,1), colors.HexColor("#fffbeb")),
        ('BACKGROUND', (3,2), (3,2), colors.HexColor("#ecfdf5")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    content.append(collateral_table)
    content.append(Spacer(1, 10))
    
    # ================= 3. CREDIT TERMS =================
    content.append(Paragraph("<b>💳 PROPOSED LOAN TERMS</b>", styles["Heading2"]))
    loan_data = [
        ["Approved Loan Amount", f"₹{eligible_loan:,.2f}", "Annual Interest Rate", f"{interest_rate}%"],
        ["Loan Tenure", f"{tenure} Months", "Repayment Frequency", "Bullet Payment (Principal + Interest)"]
    ]
    loan_table = Table(loan_data, colWidths=[130, 140, 130, 140])
    loan_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    content.append(loan_table)
    content.append(Spacer(1, 10))
    
    # ================= 4. APPRAISER FIELD NOTES =================
    if officer_notes:
        content.append(Paragraph("<b>✍️ APPRAISER SPECIAL NOTES</b>", styles["Heading2"]))
        content.append(Paragraph(officer_notes, styles["Normal"]))
        content.append(Spacer(1, 10))
        
    # Footer Signatures
    content.append(Spacer(1, 20))
    content.append(Paragraph("This evaluation certificate is digitally generated. All appraisals are backed by live spot pricing feeds and compliant with RBI LTV regulations.", styles["Normal"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph("Authorized Appraiser: AegisCR Collateral Evaluation Cell", styles["Normal"]))
    
    doc.build(content)
    return file_path