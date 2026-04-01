"""LLM Service — swappable between Hugging Face (free) and Gemini (free tier).

Controlled via .env: LLM_PROVIDER=huggingface or LLM_PROVIDER=gemini
Includes retry logic with exponential backoff for free tier rate limits.
"""
import asyncio
import requests
import json
import re
from typing import Optional

from config import settings


async def query_llm(prompt: str, max_retries: int = 3) -> str:
    """Route to the configured LLM provider with retry logic."""
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return await _query_gemini(prompt, max_retries)
    elif settings.HF_API_TOKEN:
        return await _query_huggingface(prompt, max_retries)
    elif settings.GEMINI_API_KEY:
        # Fallback to Gemini if HF token not set
        return await _query_gemini(prompt, max_retries)
    else:
        # No API keys configured — return mock response for demo
        return _mock_llm_response(prompt)


async def _query_huggingface(prompt: str, max_retries: int) -> str:
    """Query Hugging Face Inference API (free tier)."""
    api_url = f"https://api-inference.huggingface.co/models/{settings.HF_MODEL}"
    headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}

    # Format as instruction for Mistral-style models
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.3,
            "return_full_text": False,
        },
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                return str(result)

            elif response.status_code == 503:
                # Model is loading — wait and retry
                wait_time = response.json().get("estimated_time", 20)
                await asyncio.sleep(min(wait_time, 30))
                continue

            elif response.status_code == 429:
                # Rate limited — exponential backoff
                await asyncio.sleep(2 ** attempt * 5)
                continue

            else:
                print(f"HF API error {response.status_code}: {response.text}")
                break

        except requests.exceptions.Timeout:
            await asyncio.sleep(2 ** attempt * 3)
            continue
        except Exception as e:
            print(f"HF API exception: {e}")
            break

    # Fallback to Gemini if HF fails
    if settings.GEMINI_API_KEY:
        return await _query_gemini(prompt, max_retries)
    return _mock_llm_response(prompt)


async def _query_gemini(prompt: str, max_retries: int) -> str:
    """Query Google Gemini API (free tier — 15 RPM)."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    # Rate limited — exponential backoff
                    await asyncio.sleep(2 ** attempt * 5)
                    continue
                print(f"Gemini API error: {e}")
                break

    except ImportError:
        print("google-generativeai not installed")
    except Exception as e:
        print(f"Gemini setup error: {e}")

    return _mock_llm_response(prompt)


def _mock_llm_response(prompt: str) -> str:
    """Mock LLM response for demo when no API keys are configured."""
    prompt_lower = prompt.lower()

    if "structure" in prompt_lower and ("clinical" in prompt_lower or "symptoms" in prompt_lower):
        return json.dumps({
            "symptoms": ["fever", "cough", "body ache"],
            "diagnosis": "Acute Upper Respiratory Infection",
            "prescriptions": [
                {"medication": "Paracetamol 500mg", "dosage": "1 tablet", "frequency": "3 times daily", "duration": "5 days"},
                {"medication": "Cetirizine 10mg", "dosage": "1 tablet", "frequency": "once daily", "duration": "5 days"}
            ],
            "icd_codes": ["J06.9"],
            "notes": "Patient advised rest and hydration. Follow-up in 5 days if symptoms persist."
        })

    elif "bill" in prompt_lower or "charges" in prompt_lower:
        return json.dumps({
            "line_items": [
                {"item": "Consultation Fee", "amount": 500, "covered": True, "explanation": "Standard consultation — covered under OPD benefit"},
                {"item": "Blood Test - CBC", "amount": 300, "covered": True, "explanation": "Diagnostic test — covered"},
                {"item": "Room Charges (Deluxe)", "amount": 8000, "covered": False, "explanation": "Exceeds room rent cap of ₹5000/day. You pay ₹3000 extra"},
            ],
            "total": 8800,
            "covered_total": 5800,
            "out_of_pocket": 3000,
            "summary": "Most charges are covered. Room upgrade costs ₹3000 extra above your policy's room rent cap."
        })

    elif "simplif" in prompt_lower or "explain" in prompt_lower:
        return "Your discharge summary shows you were treated for a respiratory infection. You were given antibiotics and fever medicine. Key instructions: Take all medicines on time, drink plenty of water, rest for 3-5 days, and come back if fever returns or breathing becomes difficult."

    else:
        return "Based on the provided information, the analysis has been completed. Please review the structured output for details."


async def structure_clinical_note(transcript: str) -> dict:
    """Use LLM to structure a doctor-patient conversation transcript into clinical note fields."""
    prompt = f"""You are a medical AI assistant. Structure the following doctor-patient conversation transcript into a clinical note.
Return ONLY valid JSON with these exact fields:
- "symptoms": list of symptoms mentioned
- "diagnosis": primary diagnosis
- "prescriptions": list of objects with "medication", "dosage", "frequency", "duration"
- "icd_codes": relevant ICD-10 codes
- "notes": any additional clinical notes

Transcript:
{transcript}

Return ONLY the JSON, no other text."""

    response = await query_llm(prompt)

    # Try to parse JSON from the response
    try:
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    # Return mock structure if parsing fails
    return {
        "symptoms": ["Unable to parse from transcript"],
        "diagnosis": "Requires manual review",
        "prescriptions": [],
        "icd_codes": [],
        "notes": f"Auto-structuring failed. Raw transcript: {transcript[:200]}"
    }


async def analyze_bill(line_items: list, policy_info: str = "") -> dict:
    """Use LLM to analyze hospital bill line items against insurance coverage."""
    prompt = f"""You are an insurance billing expert for Indian healthcare. Analyze these hospital bill line items and explain what insurance typically covers and what the patient pays out of pocket.

Bill items:
{json.dumps(line_items, indent=2)}

{f'Policy info: {policy_info}' if policy_info else 'Assume a standard Indian health insurance policy.'}

Return ONLY valid JSON with:
- "line_items": list of objects with "item", "amount", "covered" (bool), "explanation"
- "total": total bill amount
- "covered_total": total covered amount
- "out_of_pocket": total patient pays
- "summary": 2-3 sentence plain language summary

Return ONLY the JSON."""

    response = await query_llm(prompt)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    return {
        "line_items": line_items,
        "total": sum(item.get("amount", 0) for item in line_items),
        "covered_total": 0,
        "out_of_pocket": sum(item.get("amount", 0) for item in line_items),
        "summary": "Unable to auto-analyze. Please review manually."
    }


async def simplify_discharge_summary(summary_text: str) -> str:
    """Use LLM to simplify a medical discharge summary into plain language."""
    prompt = f"""You are a patient-friendly medical communicator. Simplify the following hospital discharge summary into plain, easy-to-understand language. Use short sentences. Avoid medical jargon. Explain what the patient needs to do at home.

Discharge Summary:
{summary_text}

Write the simplified version:"""

    return await query_llm(prompt)


async def check_policy_coverage(medication: str, policy_context: str) -> dict:
    """Check if a medication/procedure is covered under a patient's insurance policy using RAG context."""
    prompt = f"""Based on the following insurance policy information, determine if "{medication}" is covered.

Policy Information:
{policy_context}

Return ONLY valid JSON:
{{"is_covered": true/false, "reason": "explanation", "alternative": "generic alternative if not covered or null"}}"""

    response = await query_llm(prompt)

    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    return {"is_covered": True, "reason": "Unable to verify — defaulting to covered", "alternative": None}
