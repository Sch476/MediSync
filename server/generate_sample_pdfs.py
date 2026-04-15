"""
Generate sample insurance policy PDFs for MediSync RAG testing.

Creates two realistic Indian health insurance policies with:
- Room rent caps, drug formularies, exclusions, sub-limits
- Sucralfate Suspension explicitly excluded in Star Health (triggers doctor warning)
- Levocetirizine covered in both
- Paracetamol covered with dosage limits
"""

from fpdf import FPDF
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class PolicyPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential  -  Insurance Policy Document", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(30, 120, 150)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def body_text(self, text, indent=0):
        self.set_font("Helvetica", "", 10)
        self.set_x(self.l_margin + indent)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def bullet(self, text, indent=8):
        self.set_font("Helvetica", "", 10)
        self.set_x(self.l_margin + indent)
        self.multi_cell(0, 6, f"* {text}")

    def key_value(self, key, value, indent=8):
        self.set_font("Helvetica", "B", 10)
        self.set_x(self.l_margin + indent)
        self.cell(70, 6, f"{key}:")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, value)


# ─────────────────────────────────────────────────────────────────────────────
# PDF 1: Star Health Standard  -  Policy STD-78901 (Priya Patel)
# ─────────────────────────────────────────────────────────────────────────────
def generate_star_health():
    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cover block
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 120, 150)
    pdf.cell(0, 12, "STAR HEALTH AND ALLIED INSURANCE CO. LTD.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, "Star Comprehensive Health Insurance Policy", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Standard Plan  -  Policy Schedule", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_draw_color(30, 120, 150)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # Policy Details
    pdf.section_title("SECTION 1  -  POLICY SCHEDULE")
    pdf.key_value("Policy Number", "STD-78901")
    pdf.key_value("Insured Name", "Ms. Priya Patel")
    pdf.key_value("Date of Birth", "15 March 1990")
    pdf.key_value("Policy Period", "01 April 2025 to 31 March 2026")
    pdf.key_value("Sum Insured", "Rs. 5,00,000 (Five Lakhs only)")
    pdf.key_value("Plan Type", "Standard Health Guard")
    pdf.key_value("Premium Paid", "Rs. 8,200 per annum (incl. GST)")
    pdf.key_value("Network Hospitals", "6,000+ hospitals across India")
    pdf.ln(4)

    # Coverage
    pdf.section_title("SECTION 2  -  IN-PATIENT HOSPITALISATION BENEFITS")
    pdf.body_text(
        "The Company will indemnify the Insured for In-Patient Hospitalisation expenses incurred "
        "in a Network Hospital, provided the hospitalisation exceeds 24 consecutive hours, subject "
        "to the terms, conditions, and exclusions listed herein."
    )
    pdf.ln(2)

    pdf.body_text("2.1  Room Rent and Boarding Charges")
    pdf.bullet("Standard Room: Rs. 4,000 per day (maximum)", indent=14)
    pdf.bullet("ICU / ICCU: Rs. 8,000 per day (maximum)", indent=14)
    pdf.bullet(
        "Proportionate Deduction Clause: If the Insured opts for a room with a rent exceeding "
        "the eligible limit, all associated costs (surgeon fee, anaesthesia, nursing, OT charges) "
        "will be proportionately reduced based on the ratio of eligible room rent to actual room rent.",
        indent=14
    )
    pdf.ln(2)

    pdf.body_text("2.2  ICU Charges")
    pdf.bullet("Covered up to 50% of Sum Insured, subject to Rs. 8,000 per day cap.", indent=14)
    pdf.ln(2)

    pdf.body_text("2.3  Surgeon, Anaesthetist, Medical Practitioner, Consultants, Specialist Fees")
    pdf.bullet("Covered as per actuals subject to reasonable and customary charges.", indent=14)
    pdf.ln(2)

    pdf.body_text("2.4  Nursing Charges")
    pdf.bullet("Covered as part of room rent package up to the eligible room rent limit.", indent=14)
    pdf.ln(2)

    # Pharmacy / Drug Coverage
    pdf.section_title("SECTION 3  -  PHARMACY AND DRUG FORMULARY")
    pdf.body_text(
        "3.1  In-Patient Pharmacy Coverage\n"
        "Medicines, drugs, and consumables purchased during an eligible hospitalisation are covered "
        "subject to a maximum of Rs. 10,000 per hospitalisation event and Rs. 25,000 per policy year."
    )
    pdf.ln(2)

    pdf.body_text("3.2  Covered Medications  -  Formulary List (Non-Exhaustive)")
    covered_drugs = [
        "Paracetamol (Acetaminophen)  -  up to 4g/day; covered for fever and pain management",
        "Levocetirizine  -  covered for allergic rhinitis, urticaria",
        "Amoxicillin, Amoxicillin-Clavulanate  -  covered for bacterial infections",
        "Metformin, Glibenclamide  -  covered for Type 2 Diabetes management",
        "Amlodipine, Losartan, Atenolol  -  covered for hypertension",
        "Omeprazole, Pantoprazole  -  covered as proton pump inhibitors (PPIs) for GERD",
        "Atorvastatin, Rosuvastatin  -  covered for dyslipidaemia",
        "Insulin (Regular, NPH, Glargine)  -  covered for diabetes management",
        "Ceftriaxone (IV)  -  covered for severe bacterial infections (in-patient only)",
        "Ranitidine  -  covered for acid reflux (outpatient, limited to 30 days supply)",
        "Furosemide, Spironolactone  -  covered for heart failure / oedema",
        "Azithromycin  -  covered for respiratory infections up to 5-day course",
        "Ibuprofen, Diclofenac  -  covered for musculoskeletal pain (max 7 days per episode)",
    ]
    for d in covered_drugs:
        pdf.bullet(d, indent=14)
    pdf.ln(2)

    pdf.body_text("3.3  EXCLUDED MEDICATIONS  -  NOT PAYABLE UNDER THIS POLICY")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(200, 0, 0)
    pdf.set_x(pdf.l_margin + 8)
    pdf.cell(0, 7, "The following medications are EXPLICITLY EXCLUDED from coverage:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    excluded_drugs = [
        "Sucralfate Suspension / Sucralfate Tablets  -  Excluded: mucosal protective agents are "
        "classified under outpatient maintenance therapy and are NOT covered under in-patient or "
        "day-care claims. Claims containing Sucralfate will be rejected or deducted.",
        "All antacid suspensions (Gelusil, Digene, Mucaine Gel)  -  Excluded as OTC maintenance items.",
        "Multivitamin supplements and nutraceuticals (e.g., Becosules, Revital, Neurobion)  -  Excluded.",
        "Ayurvedic, Homeopathic, or Unani proprietary formulations  -  Not covered under allopathic policy.",
        "Weight-loss medications (Orlistat, Liraglutide for obesity)  -  Excluded as lifestyle drugs.",
        "Sildenafil, Tadalafil  -  Excluded as lifestyle / erectile dysfunction drugs.",
        "Minoxidil, Finasteride  -  Excluded as cosmetic / hair-loss treatments.",
        "Melatonin, Zolpidem beyond 7 days  -  Excluded unless prescribed under inpatient psychiatry.",
    ]
    for d in excluded_drugs:
        pdf.bullet(d, indent=14)
    pdf.ln(2)

    pdf.body_text(
        "3.4  Pre-authorisation Requirement for High-Cost Drugs\n"
        "Any single drug item exceeding Rs. 2,000 per dose requires prior authorisation from "
        "Star Health Claims team (helpline: 1800-425-2255) before administration."
    )
    pdf.ln(2)

    # Pre-existing diseases
    pdf.section_title("SECTION 4  -  PRE-EXISTING DISEASE (PED) WAITING PERIOD")
    pdf.body_text(
        "4.1  All pre-existing diseases declared and accepted at the time of policy inception are "
        "covered after a waiting period of 36 months of continuous policy renewal without a break."
    )
    pdf.bullet("Declared PED: None at inception.", indent=14)
    pdf.bullet(
        "Undisclosed PED discovered during claim investigation will result in claim repudiation "
        "per IRDAI guidelines.", indent=14
    )
    pdf.ln(2)

    pdf.body_text("4.2  Specific Disease Waiting Period (24 months)")
    specific_waits = [
        "Cataract surgery", "Hernia repair", "Hysterectomy",
        "Joint replacement (knee/hip)", "Varicose veins",
        "Gallstones and kidney stones", "Sinusitis and related surgeries",
    ]
    for s in specific_waits:
        pdf.bullet(s, indent=14)
    pdf.ln(2)

    # General exclusions
    pdf.section_title("SECTION 5  -  GENERAL EXCLUSIONS")
    exclusions = [
        "War, terrorism, nuclear or radioactive contamination.",
        "Self-inflicted injury, suicide attempt.",
        "Alcohol or substance abuse-related treatment.",
        "Cosmetic surgery, plastic surgery (unless reconstructive due to accident/burn).",
        "Dental treatment and spectacles / contact lenses.",
        "Maternity expenses (unless Maternity Rider is opted  -  not included in this policy).",
        "Congenital external diseases and anomalies.",
        "Experimental or investigational treatments not approved by ICMR/CDSCO.",
        "Outpatient / OPD charges (not covered under Standard Plan).",
        "Vaccinations, health check-ups, general wellness services.",
        "Non-prescribed medicines, OTC drugs purchased without doctor prescription.",
    ]
    for e in exclusions:
        pdf.bullet(e, indent=14)
    pdf.ln(2)

    # Claim process
    pdf.section_title("SECTION 6  -  CLAIM PROCEDURE")
    pdf.body_text("6.1  Cashless Hospitalisation (Network Hospitals)")
    pdf.bullet("Inform Star Health TPA Helpdesk at least 3 days before planned admission.", indent=14)
    pdf.bullet("For emergencies, inform within 24 hours of admission.", indent=14)
    pdf.bullet("Hospital sends pre-authorisation form; TPA approves within 2 hours for emergencies.", indent=14)
    pdf.ln(2)

    pdf.body_text("6.2  Reimbursement Claims (Non-Network / Emergency)")
    pdf.bullet("Submit claim within 30 days of discharge.", indent=14)
    pdf.bullet(
        "Required documents: original bills, discharge summary, investigation reports, "
        "prescription copies, KYC documents.", indent=14
    )
    pdf.bullet("Claims portal: www.starhealth.in/claims | Toll-free: 1800-425-2255", indent=14)
    pdf.ln(2)

    # Sub-limits
    pdf.section_title("SECTION 7  -  SPECIFIC SUB-LIMITS (STANDARD PLAN)")
    sub_limits = [
        ("Cataract per eye", "Rs. 25,000"),
        ("Hernia (each)", "Rs. 40,000"),
        ("Knee replacement (per knee)", "Rs. 80,000"),
        ("AYUSH treatment", "Rs. 15,000 per year"),
        ("Ambulance charges", "Rs. 2,000 per hospitalisation"),
        ("Organ donor expenses", "Rs. 1,00,000"),
        ("In-patient pharmacy", "Rs. 10,000 per event / Rs. 25,000 per year"),
    ]
    for item, limit in sub_limits:
        pdf.key_value(item, limit, indent=8)
    pdf.ln(4)

    # Renewal
    pdf.section_title("SECTION 8  -  RENEWAL AND PORTABILITY")
    pdf.body_text(
        "This policy is renewable for life. No-Claim Bonus of 5% of Sum Insured (max 50%) "
        "is applied on renewal for each claim-free year. "
        "Portability rights are available as per IRDAI Portability Guidelines."
    )
    pdf.ln(4)

    # Signature block
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "Authorised Signatory  -  Star Health and Allied Insurance Co. Ltd.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "IRDAI Registration No. 129 | CIN: L66010TN2005PLC056649", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Registered Office: 1, New Tank Street, Valluvarkottam High Road, Nungambakkam, Chennai  -  600034", new_x="LMARGIN", new_y="NEXT")

    out = os.path.join(OUTPUT_DIR, "star_health_STD_78901.pdf")
    pdf.output(out)
    print(f"Generated: {out}")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# PDF 2: HDFC Ergo Premium  -  Policy PREM-45678 (Amit Verma)
# ─────────────────────────────────────────────────────────────────────────────
def generate_hdfc_ergo():
    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cover block
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 65, 130)
    pdf.cell(0, 12, "HDFC ERGO GENERAL INSURANCE COMPANY LIMITED", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, "Optima Restore Health Insurance  -  Premium Plan", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Policy Schedule and Terms & Conditions", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_draw_color(0, 65, 130)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # Policy Details
    pdf.section_title("SECTION 1  -  POLICY SCHEDULE")
    pdf.key_value("Policy Number", "PREM-45678")
    pdf.key_value("Insured Name", "Mr. Amit Verma")
    pdf.key_value("Date of Birth", "22 July 1985")
    pdf.key_value("Policy Period", "01 April 2025 to 31 March 2026")
    pdf.key_value("Sum Insured", "Rs. 10,00,000 (Ten Lakhs only)")
    pdf.key_value("Plan Type", "Optima Restore Premium")
    pdf.key_value("Premium Paid", "Rs. 14,500 per annum (incl. GST)")
    pdf.key_value("Restore Benefit", "100% Sum Insured auto-restored once per year on exhaustion")
    pdf.key_value("Network Hospitals", "10,000+ hospitals across India")
    pdf.ln(4)

    # Coverage
    pdf.section_title("SECTION 2  -  IN-PATIENT HOSPITALISATION BENEFITS")
    pdf.body_text(
        "HDFC Ergo Optima Restore covers all medically necessary in-patient hospitalisation for "
        "illness or accidental injury in India, subject to the terms herein. The Restore Benefit "
        "automatically reinstates the full Sum Insured once exhausted, at no additional premium."
    )
    pdf.ln(2)

    pdf.body_text("2.1  Room Rent and Boarding Charges")
    pdf.bullet("Single Private Air-Conditioned Room: No room rent sub-limit (actuals covered)", indent=14)
    pdf.bullet("ICU / ICCU: No daily sub-limit on ICU (actuals covered up to sum insured)", indent=14)
    pdf.bullet(
        "No Proportionate Deduction: Unlike standard plans, room rent upgrades do NOT "
        "trigger proportionate deductions on other expenses under this Premium Plan.", indent=14
    )
    pdf.ln(2)

    pdf.body_text("2.2  Day Care Procedures")
    pdf.bullet(
        "540+ day care procedures covered without 24-hour hospitalisation requirement "
        "(e.g., dialysis, chemotherapy, cataract, lithotripsy).", indent=14
    )
    pdf.ln(2)

    pdf.body_text("2.3  AYUSH (Alternative Medicine) Coverage")
    pdf.bullet("Ayurvedic / Homeopathic in-patient treatment covered up to Rs. 30,000 per year.", indent=14)
    pdf.ln(2)

    # Pharmacy
    pdf.section_title("SECTION 3  -  PHARMACY AND DRUG FORMULARY")
    pdf.body_text(
        "3.1  In-Patient Pharmacy\n"
        "All prescription medicines administered during an eligible in-patient episode are covered "
        "with no sub-limit, subject to the overall Sum Insured. OPD pharmacy is excluded unless "
        "the optional OPD Rider has been purchased (not included in this policy)."
    )
    pdf.ln(2)

    pdf.body_text("3.2  Covered Medications  -  Premium Formulary (Non-Exhaustive)")
    covered_drugs = [
        "Paracetamol (Acetaminophen)  -  covered without dosage restrictions in in-patient setting",
        "Levocetirizine  -  covered for allergic conditions; outpatient supply up to 30 days",
        "Cetirizine, Fexofenadine  -  covered for allergic rhinitis and urticaria",
        "Amoxicillin, Amoxicillin-Clavulanate, Azithromycin  -  covered for bacterial infections",
        "Ceftriaxone, Meropenem, Piperacillin-Tazobactam  -  covered for severe infections (in-patient)",
        "Metformin, Glibenclamide, Sitagliptin  -  covered for diabetes management",
        "Insulin (all formulations including analogues: Glargine, Detemir, Aspart)  -  covered",
        "Amlodipine, Losartan, Telmisartan, Ramipril  -  covered for hypertension",
        "Atorvastatin, Rosuvastatin, Ezetimibe  -  covered for dyslipidaemia",
        "Omeprazole, Pantoprazole, Esomeprazole, Rabeprazole  -  covered for GERD and gastric ulcer",
        "Sucralfate Suspension (1g/5ml, 2g/5ml)  -  COVERED under Premium Plan for peptic ulcer "
        "and gastric mucosal protection during in-patient stay. Prior authorisation not required.",
        "Ranitidine, Famotidine  -  covered for H2-blocker acid suppression",
        "Furosemide, Torsemide, Spironolactone  -  covered for cardiac and renal oedema",
        "Heparin (IV/SC), Enoxaparin  -  covered for anticoagulation therapy",
        "Ondansetron, Metoclopramide  -  covered for nausea and vomiting",
        "Dexamethasone, Methylprednisolone  -  covered for anti-inflammatory use in-patient",
        "Ibuprofen, Diclofenac, Naproxen  -  covered for pain and inflammation",
        "Morphine, Tramadol  -  covered for moderate to severe pain (in-patient only)",
    ]
    for d in covered_drugs:
        pdf.bullet(d, indent=14)
    pdf.ln(2)

    pdf.body_text("3.3  EXCLUDED MEDICATIONS")
    excluded_drugs = [
        "Multivitamins and tonics not linked to a diagnosed deficiency (e.g., general wellness supplements).",
        "Weight-loss drugs (Orlistat, Liraglutide for obesity)  -  excluded as lifestyle medications.",
        "Sildenafil, Tadalafil  -  excluded for erectile dysfunction (covered only for pulmonary arterial hypertension with documentation).",
        "Hair-loss treatments (Minoxidil topical, Finasteride for AGA)  -  excluded as cosmetic.",
        "Experimental biologics not approved by CDSCO for the claimed indication.",
        "OTC antacids (Gelusil, Digene, Mucaine Gel)  -  excluded as OTC maintenance items when no diagnosed peptic ulcer.",
    ]
    for d in excluded_drugs:
        pdf.bullet(d, indent=14)
    pdf.ln(2)

    # Pre-existing diseases
    pdf.section_title("SECTION 4  -  PRE-EXISTING DISEASE AND WAITING PERIODS")
    pdf.body_text("4.1  Pre-Existing Disease Waiting Period: 24 months (reduced from standard 36 months)")
    pdf.key_value("Declared PED at inception", "Hypertension (controlled)", indent=14)
    pdf.key_value("PED coverage begins", "01 April 2027 (after 24-month waiting period)", indent=14)
    pdf.ln(2)

    pdf.body_text("4.2  Specific Disease Waiting Period: 12 months")
    specific_waits = [
        "Cataract surgery", "Hernia repair", "Gallstones and kidney stones",
        "Sinusitis procedures", "Varicose veins",
    ]
    for s in specific_waits:
        pdf.bullet(s, indent=14)
    pdf.ln(2)

    # General exclusions
    pdf.section_title("SECTION 5  -  GENERAL EXCLUSIONS")
    exclusions = [
        "War, terrorism, nuclear or radioactive contamination.",
        "Self-inflicted injury or suicide attempt.",
        "Alcohol or substance abuse.",
        "Maternity, childbirth (unless Maternity Rider opted  -  not in this policy).",
        "Cosmetic or aesthetic surgeries.",
        "Non-allopathic OPD treatment (AYUSH OPD excluded; in-patient AYUSH partially covered  -  see 2.3).",
        "Dental, ophthalmic (spectacles/lenses), hearing aids.",
        "Congenital conditions present at birth.",
        "Experimental or non-CDSCO approved therapies.",
    ]
    for e in exclusions:
        pdf.bullet(e, indent=14)
    pdf.ln(2)

    # Claim process
    pdf.section_title("SECTION 6  -  CLAIM PROCEDURE")
    pdf.body_text("6.1  Cashless  -  Planned Hospitalisation")
    pdf.bullet("Notify HDFC Ergo Health TPA at least 48 hours before admission.", indent=14)
    pdf.bullet("Pre-auth form submitted by hospital; approval within 1 hour for network hospitals.", indent=14)
    pdf.ln(2)

    pdf.body_text("6.2  Cashless  -  Emergency Hospitalisation")
    pdf.bullet("Notify within 24 hours of admission.", indent=14)
    pdf.bullet("Emergency cashless approved retroactively for network hospitals.", indent=14)
    pdf.ln(2)

    pdf.body_text("6.3  Reimbursement Claims")
    pdf.bullet("Submit within 30 days of discharge with original documents.", indent=14)
    pdf.bullet(
        "Documents: discharge summary, bills, prescriptions, lab reports, KYC.", indent=14
    )
    pdf.bullet("Claims portal: www.hdfcergo.com/health-claims | Toll-free: 1800-2700-700", indent=14)
    pdf.ln(2)

    # Premium plan benefits
    pdf.section_title("SECTION 7  -  PREMIUM PLAN EXCLUSIVE BENEFITS")
    benefits = [
        ("Restore Benefit", "Full Sum Insured (Rs. 10 lakhs) auto-restored once per year on full exhaustion  -  no additional premium"),
        ("No Room Rent Cap", "Private AC room actuals fully reimbursed without proportionate deduction"),
        ("Inflation Guard", "+5% Sum Insured added each renewal year up to 50% total (without claim)"),
        ("Annual Health Check", "Free health check-up once per year at 5,000+ diagnostic centres"),
        ("Global Cover (Emergency)", "Emergency overseas hospitalisation covered up to Rs. 10 lakhs  -  India-based treatment only for planned care"),
        ("Domiciliary Hospitalisation", "Home treatment covered if hospitalisation not possible due to unavailability of beds"),
        ("Mental Health Cover", "In-patient psychiatric treatment covered per Mental Healthcare Act 2017"),
    ]
    for benefit, detail in benefits:
        pdf.key_value(benefit, detail, indent=8)
    pdf.ln(4)

    # Signature block
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "Authorised Signatory  -  HDFC Ergo General Insurance Company Limited", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "IRDAI Registration No. 146 | CIN: U66030MH2007PLC177117", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Registered Office: D-301, 3rd Floor, Eastern Business District, Lake Blvd. Rd., Powai, Mumbai  -  400072", new_x="LMARGIN", new_y="NEXT")

    out = os.path.join(OUTPUT_DIR, "hdfc_ergo_PREM_45678.pdf")
    pdf.output(out)
    print(f"Generated: {out}")
    return out


if __name__ == "__main__":
    f1 = generate_star_health()
    f2 = generate_hdfc_ergo()
    print("\nDone! Upload these via the Hospital Upload Policy page:")
    print(f"  Star Health (STD-78901) → Priya Patel:  {f1}")
    print(f"  HDFC Ergo   (PREM-45678) → Amit Verma: {f2}")
