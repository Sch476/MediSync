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
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash",
]

async def _query_gemini(prompt: str, max_retries: int) -> str:
    """Query Google Gemini API via REST — tries multiple models on rate limit or overload."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
    }

    for model in GEMINI_MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={settings.GEMINI_API_KEY}"
        )
        for attempt in range(2):  # 2 retries per model, then move on
            try:
                response = requests.post(url, json=payload, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    # Guard against empty response (no parts — e.g. safety block)
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    if parts and parts[0].get("text"):
                        return parts[0]["text"].strip()
                    # Empty response — try next model
                    print(f"Gemini {model} returned empty content, trying next model")
                    break

                elif response.status_code in (429, 503):
                    # Short backoff — move to next model fast
                    wait = [3, 6, 10][attempt]
                    label = "rate limited" if response.status_code == 429 else "overloaded"
                    print(f"Gemini {model} {label} — waiting {wait}s (attempt {attempt+1}/3)")
                    await asyncio.sleep(wait)
                    continue

                elif response.status_code == 404:
                    print(f"Gemini {model} not available — skipping")
                    break  # skip to next model, don't retry

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
        # Coverage check mock — handles both single and batch (array) format
        # Check if this is a batch request (numbered list like "1. Telmisartan\n2. Amlodipine")
        numbered = re.findall(r'\d+\.\s+(\S+)', prompt)
        if len(numbered) > 1:
            # Batch mock — return array, one per medication
            results = []
            for med in numbered:
                med_l = med.lower()
                if "sucralfate" in med_l:
                    results.append({"medication": med, "is_covered": False, "reason": "Excluded under Section 3.3", "alternative": "Pantoprazole 40mg", "alt_reason": "PPI covered under Section 3.2"})
                elif "multivitamin" in med_l or "neurobion" in med_l:
                    results.append({"medication": med, "is_covered": False, "reason": "Nutraceuticals excluded", "alternative": None, "alt_reason": None})
                else:
                    results.append({"medication": med, "is_covered": True, "reason": "Listed in covered formulary under Section 3.2.", "alternative": None, "alt_reason": None})
            return json.dumps(results)

        # Single medication check
        is_sucralfate = "sucralfate" in prompt_lower
        is_multivitamin = "multivitamin" in prompt_lower or "neurobion" in prompt_lower
        if is_sucralfate:
            return json.dumps({
                "is_covered": False,
                "reason": "Sucralfate Suspension is explicitly excluded under Section 3.3.",
                "alternative": "Pantoprazole 40mg",
                "alt_reason": "Pantoprazole (PPI) provides equivalent gastric mucosal protection and is listed as covered in Section 3.2."
            })
        elif is_multivitamin:
            return json.dumps({
                "is_covered": False,
                "reason": "Multivitamins and nutraceuticals are excluded.",
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
1. IGNORE all greetings, small talk, and non-medical conversation.
2. NORMALIZE drug names: speech-to-text often mishears drug names phonetically. Map them to the correct drug:
   - "livo citrzine" / "levocetirizin" → Levocetirizine
   - "hipamudge" / "hepamedge" → flag as [UNVERIFIED DRUG - verify spelling]
3. DISTINGUISH new prescriptions from stopped medications:
   - "stop X" / "discontinue X" / "rather than X, take Y" → X gets stopped: true
   - "currently on X" / "already taking X" → is_new: false
   - "I am adding X" / "starting X" / "prescribing X" → is_new: true
   - If a drug is being dose-changed, list BOTH the old (stopped: true) and new (is_new: true)
4. VALIDATE temperatures: physiologically impossible values should be flagged.
5. DIAGNOSIS must be the PRIMARY condition, not a rule-out. If the doctor says "to rule out osteomyelitis", the diagnosis is the infection itself, NOT osteomyelitis.
6. RECOMMENDED TESTS — this is CRITICAL, never skip:
   - ANY mention of: "test", "monitor", "check", "X-ray", "scan", "culture", "lab", "blood work", "repeat HbA1c", "daily CBC" → extract into recommended_tests
   - Include monitoring instructions like "blood sugar 4 times daily"
7. SAFETY FLAGS — this is CRITICAL, never skip:
   - ANY mention of "avoid", "do not give", "don't use", "contraindicated", "risk of" → extract into safety_flags
   - Also add your own clinical knowledge: e.g. Metformin + renal risk, insulin + hypoglycemia, aspirin + dengue bleeding
   - This field must NEVER be empty if drugs are prescribed — at minimum flag drug interactions

Return ONLY valid JSON with these exact fields. EVERY field is mandatory — never return an empty array for recommended_tests or safety_flags if the transcript mentions tests or drug warnings:
- "symptoms": list of symptoms (correct any obvious speech errors)
- "diagnosis": the PRIMARY diagnosis (what the patient HAS), not what is being ruled out
- "prescriptions": list of objects, each MUST have ALL of these keys:
    - "medication": corrected drug name (string)
    - "dosage": strength/amount e.g. "650mg", "10ml", "1 tablet" (string, never null)
    - "frequency": how often e.g. "every 6 hours", "3 times daily", "once before breakfast" (string, never null)
    - "duration": how long e.g. "5 days", "14 days", "until follow-up" (string, never null)
    - "is_new": true if newly prescribed, false if patient was already on it
    - "stopped": true if being discontinued, false otherwise
- "icd_codes": relevant ICD-10 codes — include codes for ALL conditions mentioned (list of strings)
- "recommended_tests": list of ALL tests/monitoring the doctor mentioned (NEVER empty if transcript mentions any test)
- "safety_flags": list of ALL safety concerns — drugs to avoid, interactions, monitoring warnings (NEVER empty if drugs are prescribed)
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
        # Post-process: fill in what Gemini often skips
        parsed = _post_process_structured_note(parsed, transcript)
        return parsed

    print(f"[LLM] JSON parse failed. Length={len(response)}. Raw response: {response[:600]}")
    return {
        "symptoms": ["Unable to parse from transcript"],
        "diagnosis": "Requires manual review",
        "prescriptions": [],
        "icd_codes": [],
        "notes": f"Auto-structuring failed. Raw transcript: {transcript[:200]}"
    }


def _post_process_structured_note(parsed: dict, transcript: str) -> dict:
    """Rule-based post-processing to catch what Gemini skips."""
    t = transcript.lower()

    # ── Stopped medications ──
    # Detect "stop X", "discontinue X", "rather than X" patterns
    stop_patterns = [
        r'stop\s+(\w[\w\s\-]*?)(?:\s+(?:immediately|as|because|since|due)|\.|,)',
        r'discontinue\s+(\w[\w\s\-]*?)(?:\s+|\.|,)',
        r'stop\s+taking\s+(\w[\w\s\-]*?)(?:\s+|\.|,)',
    ]
    stopped_names = set()
    for pattern in stop_patterns:
        for match in re.finditer(pattern, t):
            stopped_names.add(match.group(1).strip())

    # Detect "currently on X", "already taking X" → existing meds (is_new = false)
    # Capture the full clause after "currently on" to handle "X and Y" lists
    existing_clause_patterns = [
        r'currently\s+on\s+([\w\s\-,]+?)(?:\.\s|she\s|he\s|i\s+am\s|stop)',
        r'already\s+(?:on|taking)\s+([\w\s\-,]+?)(?:\.\s|she\s|he\s|stop)',
    ]
    existing_names = set()
    for pattern in existing_clause_patterns:
        for match in re.finditer(pattern, t):
            clause = match.group(1)
            # Split by "and" to get individual meds
            for part in re.split(r'\s+and\s+', clause):
                # Extract just the drug name (first word before dose)
                drug = re.match(r'(\w[\w\-]*)', part.strip())
                if drug:
                    existing_names.add(drug.group(1).strip())

    # Apply stopped/is_new flags to prescriptions
    for rx in parsed.get("prescriptions", []):
        med = (rx.get("medication") or "").lower()
        # Mark stopped
        if not rx.get("stopped"):
            for name in stopped_names:
                if name in med or med in name:
                    rx["stopped"] = True
                    break
        # Mark is_new
        if rx.get("is_new") is None or rx.get("is_new") is False:
            is_existing = any(name in med for name in existing_names)
            if not is_existing and not rx.get("stopped"):
                rx["is_new"] = True
            elif is_existing:
                rx["is_new"] = False

    # ── Safety flags ──
    safety_flags = parsed.get("safety_flags") or []
    avoid_patterns = [
        r'(?:do\s+not\s+give|don\'?t\s+(?:give|use|prescribe))\s+([\w\s\-]+?)(?:\s+(?:as|because|since|due|—|-))',
        r'(?:strictly\s+)?avoid\s+([\w\s\-]+?)(?:\s+(?:as|because|since|due|—|-))',
    ]
    seen_drugs = set()
    for pattern in avoid_patterns:
        for match in re.finditer(pattern, t):
            drug = match.group(1).strip()
            # Skip non-drug "avoid" phrases (foods, etc.)
            if any(w in drug for w in ["food", "banana", "coconut", "rich"]):
                continue
            drug_key = drug.lower()
            if drug_key in seen_drugs:
                continue
            seen_drugs.add(drug_key)
            rest = t[match.end():]
            reason = rest[:80].split(".")[0].strip() if rest else ""
            flag = f"Avoid {drug.title()}"
            if reason:
                flag += f" — {reason}"
            if not any(drug_key in f.lower() for f in safety_flags):
                safety_flags.append(flag)

    if safety_flags:
        parsed["safety_flags"] = safety_flags

    # ── Recommended tests ──
    rec_tests = parsed.get("recommended_tests") or []
    test_patterns = [
        r'(?:order|advise|recommend|do|run|get|send for|repeat)\s+(?:an?\s+)?(?:urgent\s+)?([\w\s\-]+?(?:test|x[\-\s]?ray|ultrasound|scan|culture|microscopy|panel|profile|monitoring|referral|cbc|hba1c|ecg|echo))',
        r'((?:serum|blood|electrolyte|platelet|vitals?)[\w\s]+?every\s+\d+\s+hours)',
        r'(daily\s+[\w\s]+?monitoring)',
        r'((?:urine|blood|wound|stool)\s+[\w\s]+?(?:test|routine|culture|microscopy))',
        r'([\w\s]*?referral)',
    ]
    for pattern in test_patterns:
        for match in re.finditer(pattern, t):
            test = match.group(1).strip()
            # Clean up leading conjunctions
            test = re.sub(r'^(?:and|or|also|then)\s+', '', test, flags=re.IGNORECASE).strip().title()
            if len(test) > 3 and not any(test.lower() in existing.lower() or existing.lower() in test.lower() for existing in rec_tests):
                rec_tests.append(test)

    # Also catch explicit mentions like "blood sugar monitoring four times a day"
    monitoring_patterns = [
        r'(blood\s+sugar\s+monitoring[\w\s]*?)(?:\.|,|$)',
        r'(platelet\s+(?:count\s+)?monitoring[\w\s]*?)(?:\.|,|$)',
        r'(serum\s+electrolytes[\w\s]*?)(?:\.|,|$)',
    ]
    for pattern in monitoring_patterns:
        for match in re.finditer(pattern, t):
            test = match.group(1).strip().title()
            if not any(test.lower() in existing.lower() for existing in rec_tests):
                rec_tests.append(test)

    if rec_tests:
        parsed["recommended_tests"] = rec_tests

    return parsed


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
    prompt = f"""You are a clinical pharmacist reviewing an insurance policy to check drug/item coverage.

TASK: Check if "{medication}" is covered under this insurance policy, and if it is NOT covered, find the closest therapeutically equivalent drug that IS listed as covered in this same policy.

STRICT RULES:
- ONLY use information explicitly written in the policy text below. Do NOT assume, guess, or infer.
- If the policy text does not mention this item at all, set is_covered to false with reason "Not found in the policy document — cannot verify coverage."
- Do NOT say "assumed to be covered" or "defaulting to standard coverage." Either the policy says it is covered, or it does not.
- Same active ingredient but different brand = equivalent
- Same pharmacological class treating the same condition = equivalent (e.g. Sucralfate excluded but Pantoprazole covered for gastric ulcer = valid substitution)
- Different class treating same condition only if the policy explicitly lists it = acceptable
- Do NOT invent drugs that are not mentioned in the policy text

Policy Information:
{policy_context}

Return ONLY valid JSON, no explanation outside the JSON:
{{
  "is_covered": true or false,
  "reason": "one sentence quoting the specific policy section that covers or excludes this item",
  "alternative": "exact drug name from policy if excluded and equivalent exists, otherwise null",
  "alt_reason": "why this drug is therapeutically equivalent and where the policy covers it, or null"
}}"""

    response = await query_llm(prompt)
    parsed = _extract_json(response)
    if parsed:
        return parsed
    return {"is_covered": False, "reason": "Unable to verify — could not parse LLM response. Marked as not covered for safety.", "alternative": None, "alt_reason": None}
