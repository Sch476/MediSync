"""OCR Service — Extract text from hospital bill images using pytesseract (free)."""
import pytesseract
from PIL import Image
import re
import json
from typing import List


async def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()
    except Exception as e:
        return f"OCR Error: {str(e)}"


async def extract_bill_items(image_path: str) -> dict:
    """Extract and parse hospital bill line items from an image.

    Returns structured bill data with individual charges.
    """
    raw_text = await extract_text_from_image(image_path)

    if raw_text.startswith("OCR Error"):
        return {"error": raw_text, "raw_text": "", "items": []}

    # Parse line items from OCR text
    items = _parse_bill_text(raw_text)

    return {
        "raw_text": raw_text,
        "items": items,
        "total": sum(item.get("amount", 0) for item in items),
    }


def _parse_bill_text(text: str) -> List[dict]:
    """Parse OCR text to extract bill line items.

    Handles common Indian hospital bill formats.
    """
    items = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Pattern: description followed by amount (common formats)
        # e.g., "Consultation Fee     500.00"
        # e.g., "Room Charges (3 days) ... Rs. 15,000"
        amount_patterns = [
            r'(.+?)\s+(?:Rs\.?\s*)?(\d[\d,]*\.?\d*)\s*$',
            r'(.+?)\s+(?:₹\s*)?(\d[\d,]*\.?\d*)\s*$',
            r'(.+?)\s{2,}(\d[\d,]*\.?\d*)',
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, line)
            if match:
                description = match.group(1).strip()
                amount_str = match.group(2).replace(",", "")

                # Skip header/total lines
                skip_words = ["total", "subtotal", "date", "hospital", "patient", "bill no", "invoice"]
                if any(w in description.lower() for w in skip_words):
                    continue

                try:
                    amount = float(amount_str)
                    if amount > 0:
                        items.append({
                            "description": description,
                            "amount": amount,
                            "category": _categorize_item(description),
                        })
                except ValueError:
                    continue
                break

    # If no items parsed, create a single item with the full text
    if not items and text.strip():
        items.append({
            "description": "Unparsed bill — see raw text",
            "amount": 0,
            "category": "other",
        })

    return items


def _categorize_item(description: str) -> str:
    """Auto-categorize a bill item based on its description."""
    desc_lower = description.lower()

    categories = {
        "consultation": ["consultation", "doctor fee", "physician", "opd"],
        "room": ["room", "bed", "ward", "icu", "accommodation"],
        "medication": ["medicine", "drug", "tablet", "injection", "pharmacy", "medication"],
        "lab": ["lab", "test", "pathology", "blood", "urine", "x-ray", "scan", "mri", "ct"],
        "procedure": ["surgery", "operation", "procedure", "anesthesia", "ot charge"],
        "nursing": ["nursing", "nurse", "care charge"],
        "consumables": ["consumable", "syringe", "glove", "bandage", "dressing"],
    }

    for category, keywords in categories.items():
        if any(kw in desc_lower for kw in keywords):
            return category

    return "other"
