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


GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]

async def _query_gemini(prompt: str, max_retries: int) -> str:
    """Query Google Gemini API via REST — tries multiple models on rate limit."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
    }

    for model in GEMINI_MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={settings.GEMINI_API_KEY}"
        )
        for attempt in range(2):  # max 2 retries per model
            try:
                response = requests.post(url, json=payload, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()

                elif response.status_code == 429:
                    wait = 3 * (attempt + 1)
                    print(f"Gemini {model} rate limited — waiting {wait}s")
                    await asyncio.sleep(wait)
                    continue

                else:
                    print(f"Gemini {model} HTTP {response.status_code}: {response.text[:150]}")
                    break  # try next model

            except Exception as e:
                print(f"Gemini {model} error: {e}")
                break

    return _mock_llm_response(prompt)


def _mock_llm_response(prompt: str) -> str:
    """Mock LLM response for demo when no API keys are configured."""
    prompt_lower = prompt.lower()

    if "therapeutically equivalent" in prompt_lower or ("coverage" in prompt_lower and "formulary" in prompt_lower):
        # Coverage check mock — mark Sucralfate as excluded, suggest Pantoprazole
        med = ""
        for line in prompt.splitlines():
            if line.strip().startswith('"') and "is covered" in prompt_lower:
                med = line.strip().strip('"')
                break
        is_sucralfate = "sucralfate" in prompt_lower
        is_multivitamin = "multivitamin" in prompt_lower or "neurobion" in prompt_lower
        if is_sucralfate:
            return json.dumps({
                "is_covered": False,
                "reason": "Sucralfate Suspension is explicitly excluded under Section 3.3 — classified as outpatient mucosal maintenance therapy.",
                "alternative": "Pantoprazole 40mg",
                "alt_reason": "Pantoprazole (PPI) provides equivalent gastric mucosal protection and is listed as covered in Section 3.2 of this policy."
            })
        elif is_multivitamin:
            return json.dumps({
                "is_covered": False,
                "reason": "Multivitamins and nutraceuticals are excluded unless tied to a diagnosed deficiency.",
                "alternative": None,
                "alt_reason": None
            })
        else:
            return json.dumps({
                "is_covered": True,
                "reason": "Medication appears in the covered formulary under Section 3.2.",
                "alternative": None,
                "alt_reason": None
            })

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


def _extract_json(text: str) -> Optional[dict]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Strip ```json ... ``` wrapper — extract everything between the fences
    code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback: find the outermost { ... } in raw text (greedy)
    brace_match = re.search(r'\{[\s\S]*\}', text)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    return None


async def structure_clinical_note(transcript: str) -> dict:
    """Use LLM to structure a doctor-patient conversation transcript into clinical note fields."""
    prompt = f"""You are a clinical AI assistant that extracts structured medical data from real doctor-patient conversation transcripts (which may include speech-to-text errors and informal language).

EXTRACTION RULES:
1. IGNORE all greetings, small talk, and non-medical conversation ("hello", "how are you", "okay", "please sit", "thank you", etc.)
2. NORMALIZE drug names: speech-to-text often mishears drug names phonetically. Map them to the correct drug:
   - "livo citrzine" / "levocetirizin" → Levocetirizine
   - "hipamudge" / "hepamedge" → flag as [UNVERIFIED DRUG - verify spelling]
   - Always correct obvious phonetic errors to proper drug names
3. DISTINGUISH new prescriptions from stopped medications:
   - "rather than X, take Y" → X is STOPPED, Y is new prescription
   - "instead of X" / "stop taking X" → mark X as discontinued
4. VALIDATE temperatures: "2 degrees centigrade" is physiologically impossible for a fever. If temperature seems wrong (below 35°C or stated ambiguously), flag it as: "Reported as [X] — likely [corrected value]. Verify with patient."
5. EXTRACT recommended tests: "get it tested", "run a blood test" → add to a "recommended_tests" field
6. FLAG clinical safety issues: e.g. if Paracetamol is prescribed alongside suspected liver disease/jaundice, add a safety warning

Return ONLY valid JSON with these exact fields:
- "symptoms": list of symptoms (correct any obvious speech errors)
- "diagnosis": primary diagnosis or "Suspected [X] — awaiting tests" if unconfirmed
- "prescriptions": list of objects with "medication" (corrected name), "dosage", "frequency", "duration", "is_new" (true/false), "stopped" (true if being discontinued)
- "icd_codes": relevant ICD-10 codes
- "recommended_tests": list of tests the doctor recommended
- "safety_flags": list of any clinical safety concerns (drug interactions, contraindications)
- "notes": follow-up instructions

Transcript:
{transcript}

Return ONLY the JSON, no other text."""

    response = await query_llm(prompt)

    parsed = _extract_json(response)
    if parsed:
        # Normalise symptoms — LLM sometimes returns a string instead of a list
        if isinstance(parsed.get("symptoms"), str):
            parsed["symptoms"] = [s.strip() for s in parsed["symptoms"].split(",") if s.strip()]
        return parsed

    print(f"[LLM] JSON parse failed. Length={len(response)}. Raw response: {response[:600]}")
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
    """Check if a medication is covered and, if not, find a covered equivalent from the same policy."""
    prompt = f"""You are a clinical pharmacist reviewing an insurance policy to check drug coverage.

TASK: Check if "{medication}" is covered under this insurance policy, and if it is NOT covered, find the closest therapeutically equivalent drug that IS listed as covered in this same policy.

Rules for finding an equivalent:
- Same active ingredient but different brand = equivalent
- Same pharmacological class treating the same condition = equivalent (e.g. Sucralfate excluded but Pantoprazole covered for gastric ulcer = valid substitution)
- Different class treating same condition only if the policy explicitly lists it = acceptable
- Do NOT invent drugs that are not mentioned in the policy text

Policy Information:
{policy_context}

Return ONLY valid JSON, no explanation outside the JSON:
{{
  "is_covered": true or false,
  "reason": "one sentence: why it is covered or why it is excluded, quoting the policy section",
  "alternative": "exact drug name from policy if excluded and equivalent exists, otherwise null",
  "alt_reason": "why this drug is therapeutically equivalent and where the policy covers it, or null"
}}"""

    response = await query_llm(prompt)
    parsed = _extract_json(response)
    if parsed:
        return parsed
    return {"is_covered": True, "reason": "Unable to verify — defaulting to covered", "alternative": None, "alt_reason": None}
