"""Generate a sample Indian hospital bill image for testing the Bill Decoder."""
from PIL import Image, ImageDraw, ImageFont
import os

def generate_bill():
    width, height = 800, 1100
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_bold  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        font_med   = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except Exception:
        font_bold  = ImageFont.load_default()
        font_title = font_bold
        font_small = font_bold
        font_med   = font_bold

    draw.rectangle([0, 0, width, 90], fill=(0, 82, 136))
    draw.text((40, 18), "APOLLO CITY HOSPITAL", font=font_title, fill="white")
    draw.text((40, 54), "123, MG Road, Bengaluru - 560001  |  Ph: 080-4567-8900", font=font_small, fill=(200, 230, 255))

    draw.rectangle([0, 90, width, 92], fill=(200, 200, 200))

    y = 110
    draw.text((40, y),        "HOSPITAL BILL / TAX INVOICE",  font=font_bold,  fill=(0,0,0))
    draw.text((540, y),       "Bill No: APL-2024-08821",       font=font_small, fill=(80,80,80))

    y += 34
    draw.text((40,  y),       "Patient Name:",  font=font_small, fill=(100,100,100))
    draw.text((170, y),       "Priya Patel",    font=font_med,   fill=(0,0,0))
    draw.text((480, y),       "Date:",          font=font_small, fill=(100,100,100))
    draw.text((530, y),       "15-Apr-2024",    font=font_med,   fill=(0,0,0))

    y += 28
    draw.text((40,  y),       "Age / Gender:",  font=font_small, fill=(100,100,100))
    draw.text((170, y),       "32 Yrs / Female",font=font_med,   fill=(0,0,0))
    draw.text((480, y),       "Ward:",          font=font_small, fill=(100,100,100))
    draw.text((530, y),       "Semi-Private",   font=font_med,   fill=(0,0,0))

    y += 28
    draw.text((40,  y),       "Policy No:",     font=font_small, fill=(100,100,100))
    draw.text((170, y),       "STD-78901",      font=font_med,   fill=(0,0,0))
    draw.text((480, y),       "Insurer:",       font=font_small, fill=(100,100,100))
    draw.text((530, y),       "Star Health",    font=font_med,   fill=(0,0,0))

    y += 28
    draw.text((40,  y),       "Diagnosis:",     font=font_small, fill=(100,100,100))
    draw.text((170, y),       "Acute Upper Respiratory Infection (J06.9)", font=font_med, fill=(0,0,0))

    y += 44
    draw.rectangle([30, y, width-30, y+32], fill=(0, 82, 136))
    draw.text((40,  y+7),  "DESCRIPTION",       font=font_small, fill="white")
    draw.text((380, y+7),  "QTY",               font=font_small, fill="white")
    draw.text((440, y+7),  "UNIT RATE",         font=font_small, fill="white")
    draw.text((600, y+7),  "AMOUNT (Rs.)",      font=font_small, fill="white")

    items = [
        ("Doctor Consultation Fee",             "",    "",      "600.00"),
        ("Room Charges - Semi-Private (2 days)","2",   "3000",  "6000.00"),
        ("Nursing Care Charges",                "2",   "500",   "1000.00"),
        ("Paracetamol 500mg Tablets",           "15",  "8",     "120.00"),
        ("Azithromycin 500mg Tablets",          "3",   "45",    "135.00"),
        ("Cetirizine 10mg Tablets",             "5",   "6",     "30.00"),
        ("IV Fluids - Normal Saline 500ml",     "4",   "80",    "320.00"),
        ("CBC Blood Test",                      "1",   "300",   "300.00"),
        ("Chest X-Ray (PA View)",               "1",   "450",   "450.00"),
        ("Sputum Culture & Sensitivity",        "1",   "650",   "650.00"),
        ("Nebulisation Charges",                "3",   "200",   "600.00"),
        ("Disposables & Consumables",           "",    "",      "480.00"),
        ("Pharmacy - Misc Medications",         "",    "",      "215.00"),
        ("Admission Charges",                   "",    "",      "250.00"),
    ]

    y += 32
    row_colors = [(255,255,255), (245,248,252)]
    for idx, (desc, qty, rate, amt) in enumerate(items):
        row_y = y + idx * 30
        draw.rectangle([30, row_y, width-30, row_y+29], fill=row_colors[idx % 2])
        draw.text((40,  row_y+7), desc, font=font_small, fill=(30,30,30))
        draw.text((385, row_y+7), qty,  font=font_small, fill=(30,30,30))
        draw.text((445, row_y+7), rate, font=font_small, fill=(30,30,30))
        draw.text((610, row_y+7), amt,  font=font_small, fill=(30,30,30))

    y += len(items) * 30 + 10
    draw.rectangle([30, y, width-30, y+1], fill=(180,180,180))

    y += 12
    draw.text((440, y),  "Sub Total:",          font=font_small, fill=(80,80,80))
    draw.text((610, y),  "Rs. 11,150.00",       font=font_med,   fill=(0,0,0))

    y += 28
    draw.text((440, y),  "Tax (GST 5%):",       font=font_small, fill=(80,80,80))
    draw.text((610, y),  "Rs.   557.50",        font=font_med,   fill=(0,0,0))

    y += 28
    draw.rectangle([430, y, width-30, y+36], fill=(0, 82, 136))
    draw.text((440, y+8),  "TOTAL AMOUNT:",     font=font_bold,  fill="white")
    draw.text((600, y+8),  "Rs. 11,707.50",     font=font_bold,  fill=(255, 220, 100))

    y += 56
    draw.rectangle([30, y, width-30, y+1], fill=(200,200,200))
    y += 12
    draw.text((40, y),   "Payment Mode: Insurance (Star Health STD-78901) + Cash", font=font_small, fill=(80,80,80))
    y += 24
    draw.text((40, y),   "This is a computer-generated invoice. No signature required.", font=font_small, fill=(150,150,150))
    y += 24
    draw.text((40, y),   "For queries: billing@apollocityhospital.com | 080-4567-8900 Ext. 201", font=font_small, fill=(150,150,150))

    os.makedirs("uploads", exist_ok=True)
    out = "uploads/sample_hospital_bill.png"
    img.save(out, "PNG", dpi=(150, 150))
    print(f"Saved: {out}")
    return out

if __name__ == "__main__":
    generate_bill()
