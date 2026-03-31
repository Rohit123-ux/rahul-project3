"""
HealthGuard DB — report.py
Generate downloadable PDF health report for each prediction
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io

W, H = A4
DARK   = HexColor("#0F172A")
HEART  = HexColor("#EF4444")
DIAB   = HexColor("#F59E0B")
KIDNEY = HexColor("#22D3EE")
GREEN  = HexColor("#22C55E")
ORANGE = HexColor("#F97316")
LGRAY  = HexColor("#E2E8F0")
GRAY   = HexColor("#64748B")
WHITE  = white

def sp(h=3): return Spacer(1, h*mm)
def mk(n, **kw): return ParagraphStyle(n, **kw)

def risk_color(level):
    if 'Low'  in level: return GREEN
    if 'High' in level: return HEART
    return ORANGE

def generate_report(pred, patient):
    """Generate PDF report and return as bytes"""
    buf = io.BytesIO()

    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=15*mm, bottomMargin=15*mm)

    CW = W - 40*mm
    S  = []

    # ── HEADER ────────────────────────────────────
    header = Table([[
        Paragraph("🛡️ HealthGuard",
            mk("logo", fontName="Helvetica-Bold", fontSize=18,
               textColor=WHITE, leading=22)),
        Paragraph("Health Risk Assessment Report",
            mk("tag", fontName="Helvetica", fontSize=10,
               textColor=HexColor("#A5F3FC"), leading=14)),
    ]], colWidths=[CW*0.5, CW*0.5], style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), HexColor("#0F172A")),
        ("LEFTPADDING",(0,0),(-1,-1), 16),
        ("TOPPADDING",(0,0),(-1,-1), 14),
        ("BOTTOMPADDING",(0,0),(-1,-1), 14),
        ("ALIGN",(1,0),(1,-1), "RIGHT"),
        ("RIGHTPADDING",(0,0),(-1,-1), 16),
        ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
    ]))
    S.append(header)
    S.append(sp(4))

    # ── PATIENT INFO ──────────────────────────────
    S.append(Paragraph("Patient Information",
        mk("ph", fontName="Helvetica-Bold", fontSize=11,
           textColor=DARK, leading=15)))
    S.append(sp(2))

    info_data = [
        ["Patient Name", patient.name,
         "Report Date", pred.created_at.strftime("%d %B %Y")],
        ["Age",          str(patient.age) + " years" if patient.age else "—",
         "Sex",          patient.sex or "—"],
        ["Mobile",       patient.mobile or "—",
         "Blood Group",  patient.blood_group or "—"],
        ["Email",        patient.email,
         "Report ID",    f"HG-{pred.id:05d}"],
    ]
    info_table = Table(info_data, colWidths=[30*mm, CW*0.35, 30*mm, CW*0.35],
        style=TableStyle([
            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
            ("FONTNAME",(1,0),(1,-1),"Helvetica"),
            ("FONTNAME",(3,0),(3,-1),"Helvetica"),
            ("FONTSIZE",(0,0),(-1,-1),9),
            ("TEXTCOLOR",(0,0),(0,-1), GRAY),
            ("TEXTCOLOR",(2,0),(2,-1), GRAY),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[white, HexColor("#F8FAFC")]),
            ("GRID",(0,0),(-1,-1), 0.3, LGRAY),
            ("TOPPADDING",(0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("LEFTPADDING",(0,0),(-1,-1), 8),
        ]))
    S.append(info_table)
    S.append(sp(5))

    # ── OVERALL SCORE ─────────────────────────────
    score_color = GREEN if pred.overall_score >= 75 else \
                  ORANGE if pred.overall_score >= 50 else HEART

    overall = Table([[
        Paragraph(f"{pred.overall_score}/100",
            mk("score", fontName="Helvetica-Bold", fontSize=32,
               textColor=score_color, leading=36, alignment=TA_CENTER)),
        [Paragraph("Overall Health Score",
            mk("ostitle", fontName="Helvetica-Bold", fontSize=12,
               textColor=DARK, leading=16)),
         Paragraph(pred.overall_status,
            mk("ostatus", fontName="Helvetica-Bold", fontSize=10,
               textColor=score_color, leading=14)),
         Paragraph("Based on all 3 disease risk predictions combined.",
            mk("ossub", fontName="Helvetica", fontSize=8.5,
               textColor=GRAY, leading=12))],
    ]], colWidths=[40*mm, CW-40*mm], style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), HexColor("#F8FAFC")),
        ("BOX",(0,0),(-1,-1), 1, score_color),
        ("LEFTPADDING",(0,0),(-1,-1), 14),
        ("TOPPADDING",(0,0),(-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",(0,0),(0,-1), "CENTER"),
    ]))
    S.append(overall)
    S.append(sp(5))

    # ── 3 DISEASE RESULTS ─────────────────────────
    S.append(Paragraph("Disease Risk Assessment",
        mk("drh", fontName="Helvetica-Bold", fontSize=11,
           textColor=DARK, leading=15)))
    S.append(sp(2))

    def disease_row(emoji, name, subtitle, risk_pct, level, color, advice):
        bar_w = int((risk_pct / 100) * 80)
        bar_empty = 80 - bar_w

        return Table([[
            # Left — icon + name
            [Paragraph(f"{emoji}  {name}",
                mk(f"dn{name}", fontName="Helvetica-Bold", fontSize=11,
                   textColor=DARK, leading=14)),
             Paragraph(subtitle,
                mk(f"ds{name}", fontName="Helvetica", fontSize=8.5,
                   textColor=GRAY, leading=12))],
            # Middle — risk %
            [Paragraph(f"{risk_pct:.1f}%",
                mk(f"dp{name}", fontName="Helvetica-Bold", fontSize=22,
                   textColor=color, leading=26, alignment=TA_CENTER)),
             Paragraph(level,
                mk(f"dl{name}", fontName="Helvetica-Bold", fontSize=9,
                   textColor=color, leading=12, alignment=TA_CENTER))],
            # Right — advice
            Paragraph(advice,
                mk(f"da{name}", fontName="Helvetica", fontSize=8.5,
                   textColor=DARK, leading=12.5, alignment=TA_JUSTIFY)),
        ]], colWidths=[40*mm, 28*mm, CW-68*mm], style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), white),
            ("BOX",(0,0),(-1,-1), 0.8, color),
            ("LINEBEFORE",(0,0),(0,-1), 4, color),
            ("LEFTPADDING",(0,0),(-1,-1), 10),
            ("RIGHTPADDING",(0,0),(-1,-1), 10),
            ("TOPPADDING",(0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
            ("ALIGN",(1,0),(1,-1), "CENTER"),
        ]))

    heart_advice = (
        "Cardiovascular indicators look healthy. Maintain exercise."
        if pred.heart_risk < 30 else
        "Monitor blood pressure and cholesterol regularly."
        if pred.heart_risk < 60 else
        "High risk! Consult a cardiologist immediately."
    )
    diab_advice = (
        "Blood sugar looks normal. Maintain a low-sugar diet."
        if pred.diabetes_risk < 30 else
        "Pre-diabetic signs. Reduce sugar and get HbA1c test."
        if pred.diabetes_risk < 60 else
        "High risk! Consult an endocrinologist urgently."
    )
    kidney_advice = (
        "Kidney function normal. Stay well hydrated daily."
        if pred.kidney_risk < 30 else
        "Mild stress markers. Reduce sodium intake."
        if pred.kidney_risk < 60 else
        "High risk! Consult a nephrologist urgently."
    )

    S.append(disease_row("❤️", "Heart Disease",    "Cardiovascular Risk",
        pred.heart_risk,    pred.heart_level,    HEART,  heart_advice))
    S.append(sp(2))
    S.append(disease_row("🩸", "Diabetes",         "Blood Sugar Disorder",
        pred.diabetes_risk, pred.diabetes_level, DIAB,   diab_advice))
    S.append(sp(2))
    S.append(disease_row("🫘", "Kidney Disease",   "Chronic Kidney Disease",
        pred.kidney_risk,   pred.kidney_level,   KIDNEY, kidney_advice))
    S.append(sp(5))

    # ── INPUT VALUES TABLE ────────────────────────
    S.append(Paragraph("Input Health Parameters",
        mk("iph", fontName="Helvetica-Bold", fontSize=11,
           textColor=DARK, leading=15)))
    S.append(sp(2))

    params = [
        ["Age",               f"{pred.age:.0f} years",
         "Blood Pressure",    f"{pred.trestbps:.0f} mm Hg"],
        ["Sex",               "Male" if pred.sex == 1 else "Female",
         "Cholesterol",       f"{pred.chol:.0f} mg/dl"],
        ["Chest Pain Type",   f"Type {pred.cp:.0f}",
         "Blood Glucose",     f"{pred.glucose:.0f} mg/dl"],
        ["Max Heart Rate",    f"{pred.thalach:.0f} bpm",
         "Fasting Sugar",     f"{pred.fasting_sugar:.0f} mg/dl"],
        ["BMI",               f"{pred.bmi:.1f} kg/m²",
         "Insulin",           f"{pred.insulin:.0f} mu U/ml"],
        ["Hemoglobin",        f"{pred.hemo:.1f} g/dl",
         "Serum Creatinine",  f"{pred.sc:.1f} mg/dl"],
    ]
    params_table = Table(params, colWidths=[32*mm, CW*0.3, 32*mm, CW*0.3],
        style=TableStyle([
            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
            ("FONTNAME",(1,0),(1,-1),"Helvetica"),
            ("FONTNAME",(3,0),(3,-1),"Helvetica"),
            ("TEXTCOLOR",(0,0),(0,-1), GRAY),
            ("TEXTCOLOR",(2,0),(2,-1), GRAY),
            ("FONTSIZE",(0,0),(-1,-1), 8.8),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[white, HexColor("#F8FAFC")]),
            ("GRID",(0,0),(-1,-1), 0.3, LGRAY),
            ("TOPPADDING",(0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING",(0,0),(-1,-1), 8),
        ]))
    S.append(params_table)
    S.append(sp(5))

    # ── DISCLAIMER ────────────────────────────────
    S.append(Table([[
        Paragraph(
            "⚕️  MEDICAL DISCLAIMER: This report is generated by an AI-based screening tool "
            "and is intended for informational purposes only. It does not constitute a medical "
            "diagnosis. Please consult a qualified and certified doctor before making any "
            "medical decisions based on this report.",
            mk("disc", fontName="Helvetica", fontSize=8.5, textColor=GRAY,
               leading=13, alignment=TA_JUSTIFY)),
    ]], colWidths=[CW], style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), HexColor("#FFF7ED")),
        ("BOX",(0,0),(-1,-1), 0.5, ORANGE),
        ("LEFTPADDING",(0,0),(-1,-1), 12),
        ("TOPPADDING",(0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
    ])))
    S.append(sp(4))

    # ── FOOTER ────────────────────────────────────
    S.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY,
                        spaceAfter=3, spaceBefore=3))
    S.append(Paragraph(
        f"HealthGuard  ·  B.Tech Final Year Project  ·  Dept. of CSE  ·  "
        f"Govt. College of Engineering, Odisha  ·  Report ID: HG-{pred.id:05d}",
        mk("foot", fontName="Helvetica", fontSize=7.5, textColor=GRAY,
           leading=11, alignment=TA_CENTER)))

    doc.build(S)
    return buf.getvalue()
