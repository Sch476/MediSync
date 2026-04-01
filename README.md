# MediSync

### AI-Powered Healthcare Middleware for Indian Healthcare

> B.Tech Final Year Project | 100% Free Stack — No paid APIs, no OpenAI, no AWS

---

## The Problem

In India, **over 40% of health insurance claims get denied** or delayed because of:

- Doctors prescribe medicines that aren't covered by the patient's policy (they don't check)
- Hospital bills are confusing — patients can't tell what's covered and what's not
- Insurers manually review every claim — takes days, full of errors
- Patients get discharge summaries in English medical jargon they can't understand
- No one checks on patients after discharge — complications go unnoticed

**Result**: Patients pay out of pocket. Doctors waste time on paperwork. Insurers process claims slowly.

---

## The Solution — MediSync

MediSync sits **between** doctors, insurers, and patients as an intelligent middleware layer:

```
  Doctor                    Insurer                   Patient
    |                         |                         |
    |    [Smart Scribe]       |   [Clearinghouse]       |   [Care Companion]
    |    AI structures        |   Auto-adjudicates      |   Decodes bills
    |    clinical notes       |   claims in <60s        |   Translates summaries
    |    Checks policy        |   Flags fraud           |   Monitors recovery
    |    in real-time         |   Shows analytics       |   Alerts doctor
    |                         |                         |
    └─────────────────────────┴─────────────────────────┘
                              |
                        MediSync API
                     (FastAPI + MongoDB)
```

---

## What Each Module Does

### Module A — Smart Scribe (Doctor)

> Doctor talks to patient. AI does the rest.

1. Doctor hits "Record" — browser captures speech-to-text (Web Speech API, free)
2. AI reads the transcript and auto-extracts:
   - Symptoms
   - Diagnosis
   - Prescriptions with dosage
   - ICD-10 codes
3. **The smart part**: If the patient's insurance policy is uploaded, MediSync checks EACH prescription against the policy using RAG (Retrieval-Augmented Generation)
4. If a drug isn't covered, doctor gets an instant alert: *"Atorvastatin 20mg is NOT covered. Switch to Generic Rosuvastatin for claim approval"*
5. Output: FHIR-compliant JSON that insurers can process directly

**Why this matters**: Claim denials drop because the doctor prescribes covered medicines from the start.

### Module B — Clearinghouse (Insurer/TPA)

> Claims that took 3 days now take 60 seconds.

1. Receives structured FHIR claims from doctors
2. Python rule engine auto-checks:
   - Are the ICD-10 codes valid for this diagnosis?
   - Does room rent exceed the policy cap? (e.g., private room at Rs 6000/day but policy covers Rs 4000)
   - Any excluded items? (cosmetic, dental, supplements)
   - Does claim amount exceed policy limit?
3. **Auto-approves** standard procedures instantly
4. **Flags** complex cases (cancer, cardiac, surgery) for human review with specific reasons
5. Dashboard with analytics — claims by status, top diagnoses, monthly trends (Recharts)

**Why this matters**: Routine claims get approved in seconds. Insurers focus only on cases that actually need human judgment.

### Module C — Care Companion (Patient)

> Because patients deserve to understand their own healthcare.

**Bill Decoder**:
- Upload hospital bill photo → OCR extracts every charge → AI explains line by line
- Shows: "Room charges Rs 8000/day — your policy covers Rs 5000. You pay Rs 3000 extra"

**Discharge Translator**:
- Paste English discharge summary → AI simplifies medical jargon
- Translate to Hindi, Bengali, Tamil, Telugu (10 Indian languages)
- Generate audio MP3 the patient can listen to — useful for elderly patients

**Daily Health Check**:
- Patient fills a simple form: wound condition, fever, pain level, appetite
- System auto-flags concerning symptoms (wound bleeding + fever + high pain = immediate alert)
- Doctor gets notified on their dashboard

**Claim Tracker**:
- See claim status with plain-language explanations
- "Your claim for Rs 12,185 needs additional review because room rent exceeds your policy cap"

---

## How It Works (Technical Flow)

```
Patient visits doctor
       |
       v
Doctor records consultation (Web Speech API)
       |
       v
Transcript → LLM (HuggingFace/Gemini free API) → Structured Clinical Note
       |
       v
RAG checks prescriptions against uploaded policy PDF (ChromaDB)
       |
       v
Doctor submits FHIR-compliant claim → MongoDB
       |
       v
Insurer dashboard picks it up → Auto-adjudication rule engine runs
       |
       v
Approved / Rejected / Flagged for manual review
       |
       v
Patient sees status with plain-language explanation
```

---

## Tech Stack

Everything is free. No exceptions.

| Layer | Tech | Why This |
|-------|------|----------|
| Frontend | React.js (Vite) | Fast, single repo, role-based dashboards |
| Backend | Python FastAPI | Async, auto-generates API docs, fast |
| Database | MongoDB Atlas M0 | Free tier, 512MB, enough for demo |
| LLM | HuggingFace / Gemini | Both have free tiers, swappable via .env |
| Vector DB | ChromaDB | Local, no cloud, free — stores policy embeddings |
| OCR | pytesseract | Free, reads hospital bill images |
| Speech | Web Speech API | Built into Chrome, zero cost |
| TTS | gTTS | Google TTS, free, supports Indian languages |
| Translation | deep-translator | Free, uses Google Translate |
| Auth | JWT + bcrypt | No third-party auth service needed |
| Charts | Recharts | Free React charting library |

---

## Quick Start

### You need:
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free M0 cluster) — [cloud.mongodb.com](https://cloud.mongodb.com)
- Tesseract OCR — `brew install tesseract` (macOS) or `apt install tesseract-ocr` (Linux)

### Setup

```bash
# 1. Configure
cp .env.example .env
# Edit .env → add your MongoDB URI, JWT secret, and optionally HF/Gemini API keys

# 2. Backend
cd server
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Seed demo data
python seed_data.py

# 4. Start backend (keep this terminal open)
uvicorn main:app --reload --port 8000

# 5. Frontend (new terminal)
cd client
npm install
npm run dev

# 6. Open http://localhost:5173
```

### Demo Logins (password: `password123`)

| Role | Email | What you'll see |
|------|-------|-----------------|
| Doctor | doctor@demo.com | Smart Scribe, clinical notes, policy upload |
| Insurer | insurer@demo.com | Claims list, auto-adjudication, analytics |
| Patient | patient@demo.com | Bill decoder, translator, health checks, claims |

---

## Project Structure

```
medisync/
├── client/                          # React frontend
│   └── src/
│       ├── pages/
│       │   ├── auth/                # Login, Register
│       │   ├── doctor/              # Smart Scribe, Notes, Policy Upload
│       │   ├── insurer/             # Claims, Analytics
│       │   └── patient/             # Bill Decoder, Translator, Health Check
│       ├── components/              # Layout, ProtectedRoute
│       ├── context/                 # AuthContext (JWT state)
│       └── utils/                   # Axios API client
│
├── server/                          # FastAPI backend
│   ├── routes/                      # API endpoints per role
│   ├── models/                      # Pydantic schemas (User, Claim, etc.)
│   ├── services/
│   │   ├── llm_service.py           # HF/Gemini with retry + mock fallback
│   │   ├── rag_service.py           # ChromaDB + PyPDF2 policy engine
│   │   ├── adjudication_service.py  # Rule-based claim processing
│   │   ├── ocr_service.py           # pytesseract bill extraction
│   │   ├── translation_service.py   # deep-translator + gTTS audio
│   │   └── anonymization_service.py # K-Anonymity for patient data
│   ├── middleware/                   # JWT auth + RBAC
│   ├── seed_data.py                 # Demo data loader
│   └── main.py                      # App entry point
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URI` | Yes | MongoDB Atlas connection string |
| `JWT_SECRET` | Yes | Random secret for JWT tokens |
| `LLM_PROVIDER` | No | `huggingface` or `gemini` (default: huggingface) |
| `HF_API_TOKEN` | No | HuggingFace API token (free at huggingface.co) |
| `GEMINI_API_KEY` | No | Google Gemini key (free at aistudio.google.com) |

The app works with **mock LLM responses** even without API keys — great for demos.

---

## API Docs

Backend auto-generates interactive docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Docker (Alternative)

```bash
cp .env.example .env
# Edit .env
docker-compose up --build
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```
