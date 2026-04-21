# Doctor Module — Technical Documentation

## Overview

The Doctor module (Smart Scribe) handles AI-powered clinical note generation from voice/text transcripts. It structures raw consultation data into standardized medical records with prescriptions, ICD codes, safety flags, and FHIR-compliant encounter JSON.

---

## User Flow

```
Doctor speaks/types transcript
        │
        ▼
Browser SpeechRecognition API (real-time)
        │
        ▼
POST /api/doctor/structure-note
        │
        ├──► LLM (Gemini) structures transcript
        │       │
        │       ▼
        │    _post_process_structured_note()
        │    (regex rules catch what Gemini misses)
        │       │
        │       ▼
        │    Structured output: symptoms, diagnosis,
        │    prescriptions, ICD codes, safety flags,
        │    recommended tests
        │
        ├──► RAG policy check (if policy uploaded)
        │    ChromaDB → relevant policy sections → LLM
        │    interprets coverage per medication
        │
        ├──► FHIR Encounter JSON generated
        │
        └──► Saved to MongoDB (clinical_notes collection)
                │
                ▼
        Response returned to frontend
        (structured note + badges + warnings)
```

---

## Frontend Pages

### 1. Smart Scribe (`client/src/pages/doctor/Consultation.jsx`)

**What it does:** Records doctor-patient conversation via browser mic, sends transcript to AI, displays structured clinical note.

**Speech Recording:**
- Uses `window.SpeechRecognition` (Web Speech API)
- Language: `en-IN` (Indian English)
- `continuous: true` — captures full conversation without stopping
- `interimResults: true` — shows live transcript as doctor speaks
- On each `onresult` event, final words are appended to a ref (`finalTranscriptRef`), interim words shown temporarily
- Doctor clicks Stop → transcript is frozen in a textarea for review

**Form Submission:**
- Sends `FormData` (multipart) to `POST /api/doctor/structure-note`
- Fields: `transcript`, `patient_id`, `patient_name`
- On success, renders the structured note

**Structured Note Display:**
- **Symptoms** — teal pill badges
- **Diagnosis** — plain text
- **ICD Codes** — gray monospace badges
- **Safety Flags** — bullet list inside a light-red box
- **Recommended Tests** — orange pill badges
- **Prescriptions table** — columns: Medication, Dosage, Frequency, Duration, Notes
  - Stopped meds: ~~strikethrough~~ + red `STOPPED` badge, gray text, red-tinted row
  - New meds: teal `NEW` badge

---

### 2. Clinical Notes (`client/src/pages/doctor/ClinicalNotes.jsx`)

**What it does:** Lists all saved consultation notes for the logged-in doctor. Click to expand and see full details.

**Table columns:** Date | Patient | Diagnosis | ICD Codes | Warnings | Expand

**Expanded view shows:**
- Policy warnings (red alert boxes if any prescriptions not covered)
- Symptoms (teal pills)
- Safety flags (red bullet list)
- Recommended tests (orange pills)
- Prescriptions table (with STOPPED/NEW badges, Frequency column)
- FHIR Encounter JSON (collapsible `<pre>` block)

---

### 3. Patient Alerts (`client/src/pages/doctor/PatientAlerts.jsx`)

**What it does:** Shows flagged post-discharge health checks that need the doctor's attention.

**Data source:** `GET /api/doctor/flagged-health-checks` — returns health checks where `is_flagged: true` for this doctor's patients.

**Each alert card shows:**
- Patient name + timestamp
- Vitals: temperature, pain level, wound condition, fever status, medication compliance
- Flag reasons as bullet list (e.g. "Wound condition: red — possible infection")
- Patient's own notes (italic gray)
- **Mark as Reviewed** button — calls `PATCH /api/doctor/health-checks/{id}/acknowledge`, removes from list

**Severity color coding:**
- 4+ flags → red
- 2-3 flags → orange
- < 2 flags → yellow

---

### 4. Dashboard (`client/src/pages/doctor/DoctorDashboard.jsx`)

**Stat cards:**
- Total Notes (count from `GET /api/doctor/clinical-notes`)
- Patient Alerts (count from `GET /api/doctor/flagged-health-checks`)

**Quick actions:** New Consultation, Clinical Notes

**Recent notes table:** Last 5 notes with date, patient, diagnosis, claim status badge

---

## Backend Endpoints

### `POST /api/doctor/structure-note`
**File:** `server/routes/doctor.py:26`

| Input | Type | Required |
|---|---|---|
| transcript | Form (string) | Yes |
| patient_id | Form (string) | Yes |
| patient_name | Form (string) | Yes |
| policy_id | Form (string) | No |

**Processing chain:**
1. `structure_clinical_note(transcript)` — LLM extracts structured data
2. `_post_process_structured_note(parsed, transcript)` — regex rules fill in gaps
3. For each prescription, if `policy_id` provided:
   - `check_medication_coverage(policy_id, medication)` — RAG + LLM checks coverage
   - If not covered, adds to `policy_warnings`
4. `_build_fhir_encounter()` — generates FHIR JSON
5. Saves to `db.clinical_notes`

**Response:** Full clinical note object with `id`, `symptoms`, `diagnosis`, `prescriptions`, `icd_codes`, `safety_flags`, `recommended_tests`, `fhir_encounter`, `policy_warnings`

---

### `GET /api/doctor/clinical-notes`
**File:** `server/routes/doctor.py:157`

Returns all notes where `doctor_id` matches current user, sorted by `created_at DESC`, limit 100.

---

### `GET /api/doctor/clinical-notes/{note_id}`
**File:** `server/routes/doctor.py:172`

Returns single note by ID. Verifies doctor ownership. 404 if not found.

---

### `GET /api/doctor/patients`
**File:** `server/routes/doctor.py:184`

Returns all users with `role: "patient"`, excludes hashed_password. Auto-attaches `policy_id` for each patient.

---

### `GET /api/doctor/flagged-health-checks`
**File:** `server/routes/doctor.py:234`

Returns health checks where `doctor_id` matches and `is_flagged: true`, sorted by `created_at DESC`, limit 50.

---

### `POST /api/doctor/upload-policy`
**File:** `server/routes/doctor.py:111`

Uploads insurance policy PDF, saves to disk, indexes in ChromaDB via `index_policy_pdf()`.

---

## AI Pipeline — How `structure_clinical_note` Works

**File:** `server/services/llm_service.py:228`

### Step 1: LLM Call

Sends a detailed prompt to Gemini with the transcript. The prompt instructs the LLM to:

- Ignore greetings and small talk
- Normalize drug names (fix speech-to-text phonetic errors)
- Distinguish new prescriptions from stopped/existing medications
- Validate temperatures for physiological plausibility
- Extract the PRIMARY diagnosis (not rule-outs)
- Extract recommended tests (any mention of test/monitor/X-ray/culture/lab)
- Extract safety flags (drug interactions, contraindications, "avoid X")

**Required output fields:** `symptoms`, `diagnosis`, `prescriptions` (with `medication`, `dosage`, `frequency`, `duration`, `is_new`, `stopped`), `icd_codes`, `recommended_tests`, `safety_flags`, `notes`

### Step 2: JSON Extraction (`_extract_json`)

**File:** `server/services/llm_service.py:207`

Handles messy LLM output:
1. Tries to extract from markdown code blocks: `` ```json ... ``` ``
2. Falls back to finding outermost `{ ... }` braces
3. Parses with `json.loads()`

### Step 3: Post-Processing (`_post_process_structured_note`)

**File:** `server/services/llm_service.py:293`

Gemini's free-tier models often skip supplementary fields. This function uses regex rules on the original transcript to fill gaps:

**A. Stopped Medications**
- Detects patterns: `"stop X immediately"`, `"discontinue X"`, `"stop taking X"`
- Marks matching prescriptions with `stopped: true`

**B. New vs Existing Medications**
- Detects: `"currently on X"`, `"already taking X"` → existing (`is_new: false`)
- Handles "X and Y" lists in "currently on" clauses
- Anything not existing and not stopped → `is_new: true`

**C. Safety Flags**
- Detects: `"do not give X"`, `"avoid X"`, `"don't use X"`
- Skips food-related "avoid" (bananas, coconut water, etc.)
- Extracts the reason text after "as/because"
- Deduplicates by drug name
- Format: `"Avoid {Drug} — {reason}"`

**D. Recommended Tests**
- Detects: `"order/advise/recommend {test/X-ray/ultrasound/culture/scan/referral}"`
- Detects: `"serum/blood/electrolyte ... every N hours"` (monitoring schedules)
- Detects: `"daily {X} monitoring"`, `"blood sugar monitoring"`, `"platelet count monitoring"`
- Detects: `"urine/blood/wound/stool ... test/routine/culture/microscopy"`
- Cleans leading conjunctions ("and", "or"), deduplicates

### Step 4: Gemini Model Fallback Chain

**File:** `server/services/llm_service.py:82`

```
gemini-2.5-flash → gemini-2.5-flash-lite → gemini-2.0-flash-lite → gemini-2.0-flash-001 → gemini-2.0-flash
```

- 3 retries per model
- On 429 (rate limited) or 503 (overloaded): waits 20s / 40s / 65s
- On 404: skips to next model
- If all fail: falls back to mock response for demo

---

## RAG Pipeline — How Policy Coverage Check Works

**File:** `server/services/rag_service.py`

### Indexing (when policy PDF is uploaded)

```
PDF file → PyPDF2 extracts text → chunk_text() splits into 500-word chunks
with 50-word overlap → ChromaDB stores vectors with metadata
```

- Collection name: `policy_{patient_id}`
- Each chunk gets: `policy_id`, `insurer_name`, `chunk_index` as metadata
- ChromaDB uses default embedding model for vectorization

### Querying (during coverage check)

```
Medication name → query_policy() → ChromaDB semantic search
→ top 3 relevant chunks returned → joined with "---" separator
→ sent as context to check_policy_coverage() LLM call
→ LLM returns: is_covered, reason, alternative, alt_reason
```

**Auto re-index:** If ChromaDB returns empty (e.g. after server restart), `_try_reindex()` automatically reloads the PDF from disk and re-indexes it.

**No guessing:** If no policy is uploaded → error (HTTP 404). If RAG returns empty after re-index → error (HTTP 400). LLM prompt explicitly says: "Do NOT assume or guess. If not mentioned in policy, mark as not covered."

---

## Data Models

### Prescription (`server/models/clinical_note.py:7`)

| Field | Type | Description |
|---|---|---|
| medication | str | Drug name (corrected for speech errors) |
| dosage | str | e.g. "500mg", "10ml" |
| frequency | str | e.g. "3 times daily", "every 6 hours" |
| duration | str | e.g. "5 days", "until follow-up" |
| is_new | bool/null | True if newly prescribed this visit |
| stopped | bool/null | True if being discontinued |
| is_covered | bool/null | RAG policy check result |
| alternative | str/null | Suggested covered alternative |

### ClinicalNoteInDB (`server/models/clinical_note.py:29`)

| Field | Type | Description |
|---|---|---|
| doctor_id | str | MongoDB ObjectId of doctor |
| doctor_name | str | Doctor's full name |
| patient_id | str | MongoDB ObjectId of patient |
| patient_name | str | Patient's full name |
| raw_transcript | str | Original voice/text transcript |
| symptoms | [str] | Extracted symptoms list |
| diagnosis | str | Primary diagnosis |
| prescriptions | [Prescription] | Structured prescriptions |
| icd_codes | [str] | ICD-10 codes |
| notes | str | Follow-up instructions |
| recommended_tests | [str] | Tests doctor recommended |
| safety_flags | [str] | Drug interactions, contraindications |
| fhir_encounter | dict | FHIR Encounter resource JSON |
| policy_warnings | [str] | Coverage warnings from RAG check |
| created_at | datetime | Timestamp |

---

## FHIR Encounter JSON

**Generated by:** `_build_fhir_encounter()` in `server/routes/doctor.py:249`

Produces a FHIR R4-compliant Encounter resource:

```json
{
  "resourceType": "Encounter",
  "status": "finished",
  "class": { "code": "AMB", "display": "ambulatory" },
  "subject": { "reference": "Patient/{id}", "display": "{name}" },
  "participant": [{ "individual": { "reference": "Practitioner/{id}", "display": "Dr. {name}" } }],
  "diagnosis": [{ "condition": { "display": "{diagnosis}" }, "rank": 1 }],
  "reasonCode": [{ "text": "{symptom}" }],
  "period": { "start": "ISO datetime", "end": "ISO datetime" },
  "extension": [{ "url": "medications", "valueString": "[prescriptions JSON]" }]
}
```

---

## File Map

| File | Purpose |
|---|---|
| `server/routes/doctor.py` | All doctor API endpoints |
| `server/services/llm_service.py` | LLM calls (Gemini/HF), prompt engineering, post-processing |
| `server/services/rag_service.py` | ChromaDB indexing, policy querying, auto re-index |
| `server/models/clinical_note.py` | Pydantic models for Prescription, ClinicalNote |
| `client/src/pages/doctor/Consultation.jsx` | Smart Scribe UI (recording, submission, results) |
| `client/src/pages/doctor/ClinicalNotes.jsx` | Notes list + expanded detail view |
| `client/src/pages/doctor/PatientAlerts.jsx` | Flagged health check alerts |
| `client/src/pages/doctor/DoctorDashboard.jsx` | Dashboard stats + quick actions |
