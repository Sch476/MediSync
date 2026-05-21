"""Build the MediSync Viva Guide PDF — technical + non-technical walkthrough of every module."""
from weasyprint import HTML, CSS
from pathlib import Path

OUT = "/Users/sayantan/Documents/ProJ/Medisync/MediSync_Viva_Guide.pdf"

CSS_TEXT = """
@page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #888;
        font-family: 'Helvetica', sans-serif;
    }
    @bottom-left {
        content: "MediSync — Viva Guide";
        font-size: 9pt;
        color: #888;
        font-family: 'Helvetica', sans-serif;
    }
}
@page :first {
    margin: 0;
    @bottom-right { content: none; }
    @bottom-left { content: none; }
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #2d3436;
}

.cover {
    height: 297mm;
    width: 210mm;
    background: linear-gradient(135deg, #0a4d68 0%, #088395 60%, #05bfdb 100%);
    color: #fff;
    padding: 70mm 25mm 30mm 25mm;
    box-sizing: border-box;
    page-break-after: always;
}
.cover h1 {
    font-size: 44pt;
    margin: 0 0 6mm;
    letter-spacing: -1px;
    font-weight: 800;
}
.cover .tag {
    font-size: 16pt;
    font-weight: 300;
    opacity: 0.95;
    margin-bottom: 30mm;
}
.cover .sub {
    font-size: 11pt;
    line-height: 1.7;
    opacity: 0.85;
    border-left: 3px solid #fff;
    padding-left: 12px;
    margin-top: 60mm;
}
.cover .footer {
    position: absolute;
    bottom: 20mm;
    left: 25mm;
    right: 25mm;
    font-size: 10pt;
    opacity: 0.75;
    display: flex;
    justify-content: space-between;
}

h1.section {
    color: #0a4d68;
    font-size: 22pt;
    border-bottom: 3px solid #05bfdb;
    padding-bottom: 6px;
    margin-top: 0;
    page-break-before: always;
}
h1.section:first-of-type { page-break-before: avoid; }

h2 {
    color: #0a4d68;
    font-size: 14pt;
    margin-top: 18px;
    margin-bottom: 6px;
    border-left: 4px solid #05bfdb;
    padding-left: 10px;
}

h3 {
    color: #088395;
    font-size: 11.5pt;
    margin-top: 14px;
    margin-bottom: 4px;
}

p { margin: 6px 0; }

.lead {
    font-size: 11pt;
    color: #555;
    margin: 4px 0 14px;
    font-style: italic;
}

code, .mono {
    font-family: 'Menlo', 'Monaco', monospace;
    font-size: 9pt;
    background: #f1f7fa;
    color: #0a4d68;
    padding: 1px 4px;
    border-radius: 3px;
}

pre {
    background: #1e1e2e;
    color: #d4d4d8;
    padding: 10px 12px;
    border-radius: 6px;
    font-size: 8.5pt;
    line-height: 1.45;
    overflow-x: auto;
    page-break-inside: avoid;
    font-family: 'Menlo', 'Monaco', monospace;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    page-break-inside: avoid;
    font-size: 9.5pt;
}
table th {
    background: #0a4d68;
    color: #fff;
    padding: 7px 10px;
    text-align: left;
    font-weight: 600;
}
table td {
    border: 1px solid #dfe6e9;
    padding: 6px 10px;
    vertical-align: top;
}
table tr:nth-child(even) td { background: #f8fafb; }

.callout {
    border-left: 4px solid #05bfdb;
    background: #effaff;
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
}
.callout.warn {
    border-left-color: #ffa502;
    background: #fff8eb;
}
.callout.danger {
    border-left-color: #ff4757;
    background: #fff0f0;
}
.callout .label {
    font-weight: 700;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
    color: #088395;
}
.callout.warn .label { color: #cf8a00; }
.callout.danger .label { color: #c0392b; }

ul, ol { margin: 5px 0 8px 22px; padding: 0; }
li { margin: 3px 0; }

.kv {
    display: grid;
    grid-template-columns: 35% 65%;
    gap: 4px 12px;
    margin: 8px 0;
    font-size: 10pt;
}
.kv .k { color: #088395; font-weight: 600; }

.toc {
    margin: 20px 0;
}
.toc h2 { margin-bottom: 10px; }
.toc-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dotted #cdd6d8;
    font-size: 10pt;
}
.toc-row .num { color: #088395; font-weight: 600; min-width: 18mm; }
.toc-row .title { flex: 1; }
.toc-row .page { color: #888; }

.flow {
    background: #f8fafb;
    border: 1px solid #e0e8eb;
    border-radius: 6px;
    padding: 12px 16px;
    font-family: 'Menlo', monospace;
    font-size: 9pt;
    line-height: 1.65;
    white-space: pre;
    page-break-inside: avoid;
    margin: 10px 0;
}

.glossary-term {
    page-break-inside: avoid;
    margin: 10px 0;
}
.glossary-term .term {
    color: #0a4d68;
    font-weight: 700;
    font-size: 11pt;
}
.glossary-term .definition {
    margin-top: 2px;
    color: #2d3436;
}

.signoff {
    margin-top: 30px;
    padding: 14px;
    background: linear-gradient(135deg, #0a4d68, #05bfdb);
    color: #fff;
    border-radius: 8px;
    text-align: center;
    font-size: 11pt;
}
"""

HTML_TEXT = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body>

<!-- ============ COVER PAGE ============ -->
<div class="cover">
    <div style="font-size:13pt; opacity:0.85; letter-spacing:2px;">B.TECH FINAL YEAR PROJECT</div>
    <h1>MediSync</h1>
    <div class="tag">AI-Powered Healthcare Middleware<br/>The Complete Viva Guide</div>
    <div class="sub">
        Every module, every endpoint, every important function — explained twice:<br/>
        once in plain English, once in technical detail.<br/><br/>
        Use this document to prepare for examiner questions on architecture,
        AI integration (Gemini, RAG, ChromaDB), data flow, business logic, and
        the design decisions behind every screen.
    </div>
    <div class="footer">
        <span>Generated from source code</span>
        <span>FastAPI · React · MongoDB · ChromaDB · Gemini</span>
    </div>
</div>

<!-- ============ TOC ============ -->
<h1 class="section">Table of Contents</h1>
<div class="toc">
    <div class="toc-row"><span class="num">1.</span><span class="title">What MediSync is — in plain English</span></div>
    <div class="toc-row"><span class="num">2.</span><span class="title">System architecture &amp; tech stack</span></div>
    <div class="toc-row"><span class="num">3.</span><span class="title">Data model — MongoDB collections</span></div>
    <div class="toc-row"><span class="num">4.</span><span class="title">Authentication &amp; role-based access</span></div>
    <div class="toc-row"><span class="num">5.</span><span class="title">Module A — Doctor (Smart Scribe)</span></div>
    <div class="toc-row"><span class="num">6.</span><span class="title">Module B — Hospital (Billing &amp; Claim Submission)</span></div>
    <div class="toc-row"><span class="num">7.</span><span class="title">Module C — Insurer (Clearinghouse)</span></div>
    <div class="toc-row"><span class="num">8.</span><span class="title">Module D — Patient (Care Companion)</span></div>
    <div class="toc-row"><span class="num">9.</span><span class="title">Background services — LLM, RAG, OCR, Adjudication</span></div>
    <div class="toc-row"><span class="num">10.</span><span class="title">Glossary — terms you should be ready to define</span></div>
    <div class="toc-row"><span class="num">11.</span><span class="title">Likely viva questions &amp; how to answer them</span></div>
</div>

<!-- ============ SECTION 1 ============ -->
<h1 class="section">1. What MediSync is — in plain English</h1>

<p class="lead">If you had to explain MediSync in one sentence: it's a middleware layer that sits between doctors, hospitals, insurers, and patients to automate insurance claim processing in Indian healthcare.</p>

<h2>The problem we're solving</h2>
<p>In India, <strong>over 40% of health insurance claims get denied or delayed</strong>. Why?</p>
<ul>
    <li>Doctors prescribe drugs that aren't covered by the patient's policy — they don't check before writing the prescription.</li>
    <li>Hospital bills are confusing — patients can't tell what's covered and what isn't.</li>
    <li>Insurers review every claim manually — takes days, full of errors.</li>
    <li>Patients receive discharge summaries in English medical jargon they can't understand.</li>
    <li>Nobody checks on patients after discharge — complications go unnoticed.</li>
</ul>

<h2>How MediSync solves it</h2>
<p>Four role-specific modules talk to one shared backend:</p>

<table>
    <tr><th>Module</th><th>For Whom</th><th>What it does</th></tr>
    <tr><td><strong>Smart Scribe</strong></td><td>Doctor</td><td>Records consultation → AI structures it into a clinical note → checks each prescription against the patient's policy in real-time.</td></tr>
    <tr><td><strong>Hospital Admin</strong></td><td>Hospital</td><td>Reviews the doctor's note, runs medication-coverage checks, builds the itemized claim, and submits to the insurer.</td></tr>
    <tr><td><strong>Clearinghouse</strong></td><td>Insurer</td><td>Auto-adjudicates claims in seconds using a Python rule engine — approves standard cases, flags complex ones for human review.</td></tr>
    <tr><td><strong>Care Companion</strong></td><td>Patient</td><td>Bill decoder, discharge translator + audio in 10 Indian languages, daily health check, claim tracker.</td></tr>
</table>

<div class="callout">
    <div class="label">Design through-line</div>
    Every screen either <strong>explains</strong> (claims, bills, alerts in plain language) or <strong>acts</strong> (upload, submit, approve). No screen assumes medical literacy from the patient or programming literacy from anyone.
</div>

<h2>The Happy Path — one claim from start to finish</h2>
<div class="flow">Patient uploads policy PDF
        ↓ (indexed once in ChromaDB)
Doctor records consultation
        ↓ (Web Speech API → transcript)
Smart Scribe → Gemini structures the transcript into JSON
        ↓ (symptoms, diagnosis, prescriptions, ICD codes)
RAG checks each prescription against the policy
        ↓ (warns about non-covered drugs)
Hospital reviews → may substitute drugs → builds itemized claim
        ↓
Insurer auto-adjudicates with Python rules
        ↓
Approved / Rejected / Flagged for manual review
        ↓
Patient sees status in plain language</div>


<!-- ============ SECTION 2 ============ -->
<h1 class="section">2. System architecture &amp; tech stack</h1>

<h2>The big picture</h2>
<div class="flow">┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Doctor    │     │  Hospital   │     │   Insurer   │     │   Patient   │
│   (React)   │     │   (React)   │     │   (React)   │     │   (React)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       └───────────────────┴─────────┬─────────┴───────────────────┘
                                     │ (axios + JWT)
                                     ▼
                           ┌──────────────────┐
                           │  FastAPI server  │  ← /api/{doctor|hospital|insurer|patient}
                           │   (Python 3.11)  │
                           └────────┬─────────┘
              ┌─────────────┬───────┴───────┬─────────────┐
              ▼             ▼               ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐
        │ MongoDB  │  │ ChromaDB │  │   Gemini   │  │ pytesseract│
        │ (Atlas)  │  │ (vectors)│  │   (LLM)    │  │   (OCR)   │
        └──────────┘  └──────────┘  └────────────┘  └──────────┘</div>

<h2>Tech stack — every choice has a reason</h2>
<table>
    <tr><th>Layer</th><th>Choice</th><th>Why this and not the alternative</th></tr>
    <tr><td>Frontend</td><td>React 19 + Vite</td><td>One repo for four dashboards via role-based routing. Vite gives sub-second hot reload.</td></tr>
    <tr><td>Backend</td><td>FastAPI (Python)</td><td>Async, auto-generates OpenAPI/Swagger docs, Pydantic for type-safe request bodies.</td></tr>
    <tr><td>Database</td><td>MongoDB Atlas (M0 free)</td><td>Documents fit healthcare records (variable fields per claim). 512 MB free tier enough for demo.</td></tr>
    <tr><td>LLM</td><td>Google Gemini (free tier)</td><td>Free API key from aistudio.google.com. HuggingFace + mock as fallbacks.</td></tr>
    <tr><td>Vector DB</td><td>ChromaDB (local)</td><td>No cloud lock-in, no extra cost. Stores policy PDF embeddings on disk.</td></tr>
    <tr><td>OCR</td><td>pytesseract</td><td>Offline, free Tesseract wrapper. Reads English hospital bills well.</td></tr>
    <tr><td>Speech-to-text</td><td>Web Speech API</td><td>Built into Chrome — zero API cost, runs in the browser.</td></tr>
    <tr><td>Text-to-speech</td><td>gTTS (Google TTS)</td><td>Free, supports Hindi, Bengali, Tamil, Telugu, etc.</td></tr>
    <tr><td>Translation</td><td>deep-translator</td><td>Wraps Google Translate, free, covers 10+ Indian languages.</td></tr>
    <tr><td>Auth</td><td>JWT + bcrypt</td><td>No third-party auth service needed. Token stored in localStorage on the client.</td></tr>
    <tr><td>Charts</td><td>Recharts</td><td>React-native charting; pie, bar, line — all needed for the insurer analytics page.</td></tr>
</table>

<div class="callout warn">
    <div class="label">Likely viva question</div>
    <strong>"Why didn't you use OpenAI or AWS?"</strong> — Both have free tiers that quickly hit limits and require credit cards. The brief was zero paid APIs. Gemini gives 60 req/min free, ChromaDB runs on the same disk, and Tesseract is fully offline. Every component is swappable via <code>.env</code>.
</div>


<!-- ============ SECTION 3 ============ -->
<h1 class="section">3. Data model — MongoDB collections</h1>

<p>Eight collections cover every entity. All identified by Mongo's <code>_id</code> (ObjectId), surfaced to the frontend as a string <code>id</code>.</p>

<table>
    <tr><th>Collection</th><th>Stores</th><th>Key fields</th></tr>
    <tr><td><code>users</code></td><td>Doctors, insurers, patients, hospitals (single collection, <code>role</code> field discriminates)</td><td>email, hashed_password, role, full_name, policy_number (patient only), license_number (doctor only)</td></tr>
    <tr><td><code>clinical_notes</code></td><td>Output of Smart Scribe — structured consultation</td><td>doctor_id, patient_id, transcript, structured (symptoms/diagnosis/prescriptions/ICD), fhir, policy_warnings</td></tr>
    <tr><td><code>claims</code></td><td>Insurance claims, regardless of who submitted</td><td>doctor_id, patient_id, hospital_id, items[], total_amount, status (pending → adjudicated → approved/rejected), flag_reasons, recommended_amount</td></tr>
    <tr><td><code>health_checks</code></td><td>Post-discharge daily check-ins from patients</td><td>patient_id, doctor_id, wound_condition, fever, temperature, pain_level, is_flagged, flag_reasons</td></tr>
    <tr><td><code>policy_documents</code></td><td>Pointer to indexed policy PDFs</td><td>policy_id, patient_id, insurer_name, file_path, chunks_indexed</td></tr>
    <tr><td><code>bill_analyses</code></td><td>OCR + LLM analysis of patient-uploaded bills</td><td>patient_id, raw_text, ocr_items, llm_analysis</td></tr>
    <tr><td><code>daily_bills</code></td><td>Hospital's per-day itemized billing</td><td>hospital_id, patient_id, items[], insurer_items[], patient_items[], insurer_total, patient_total, patient_paid</td></tr>
    <tr><td><code>discharge_translations</code></td><td>Discharge summaries simplified + translated + audio path</td><td>patient_id, original_text, simplified_text, language, translated_text, audio_path</td></tr>
</table>

<h2>Why MongoDB and not Postgres?</h2>
<p>Healthcare records are <strong>inherently variable</strong> — one claim has a room rent line, the next has 14 medications, the third has just an OPD consultation. Document store > rigid schema. Plus FastAPI + Motor gives async Mongo access out of the box.</p>


<!-- ============ SECTION 4 ============ -->
<h1 class="section">4. Authentication &amp; role-based access</h1>

<h2>Login flow (non-technical)</h2>
<p>User types email + password. Server checks the password hash. If valid, server returns a <strong>JWT token</strong> — a signed string the client stores. Every subsequent request attaches this token in the <code>Authorization</code> header so the server knows who's calling.</p>

<h2>The code path</h2>
<div class="kv">
    <span class="k">Frontend entry</span><span><code>client/src/context/AuthContext.jsx</code> — <code>login()</code> + <code>register()</code> functions.</span>
    <span class="k">API client</span><span><code>client/src/utils/api.js</code> — axios instance with request interceptor that auto-attaches the JWT.</span>
    <span class="k">Backend route</span><span><code>POST /api/auth/login</code> in <code>server/routes/auth.py</code>.</span>
    <span class="k">Token creation</span><span><code>create_access_token()</code> in <code>server/middleware/auth_middleware.py</code>.</span>
    <span class="k">Role guard</span><span><code>require_role(["doctor"])</code> dependency in FastAPI routes.</span>
</div>

<h2>Why JWT and not session cookies?</h2>
<ul>
    <li>JWTs are <strong>stateless</strong> — server doesn't need to remember sessions, scales horizontally.</li>
    <li>Self-contained — payload includes user_id + role, so role checks don't require a DB hit.</li>
    <li>bcrypt for password hashing — same algorithm used by Auth0, Django, GitHub. Salt + slow hash = brute-force resistant.</li>
</ul>

<h2>Role-based UI</h2>
<p>Login redirects to <code>/doctor</code>, <code>/hospital</code>, <code>/insurer</code>, or <code>/patient</code> based on <code>user.role</code>. The sidebar (<code>Layout.jsx</code>) renders a different menu per role from a single <code>MENU_BY_ROLE</code> object. <code>ProtectedRoute.jsx</code> blocks unauthorized paths.</p>


<!-- ============ SECTION 5 ============ -->
<h1 class="section">5. Module A — Doctor (Smart Scribe)</h1>

<p class="lead">The doctor talks. The AI does the rest.</p>

<h2>Pages in this module</h2>
<table>
    <tr><th>Page</th><th>Path</th><th>Function</th></tr>
    <tr><td>Doctor Dashboard</td><td>/doctor</td><td>Quick KPIs + nav to other pages.</td></tr>
    <tr><td>Consultation</td><td>/doctor/consultation</td><td>The Smart Scribe page — speech-to-text, AI structuring, real-time policy check.</td></tr>
    <tr><td>Clinical Notes</td><td>/doctor/notes</td><td>Historical record of every consultation, with expandable details (symptoms, ICD codes, FHIR, safety flags).</td></tr>
    <tr><td>Patient Alerts</td><td>/doctor/alerts</td><td>Inbox of post-discharge health checks flagged as concerning.</td></tr>
    <tr><td>Upload Policy</td><td>/doctor/upload-policy</td><td>Optional — most policies are uploaded by the patient or hospital.</td></tr>
</table>

<h2>The Smart Scribe pipeline — step by step</h2>
<ol>
    <li><strong>Record</strong> — doctor clicks 🎤; browser's Web Speech API converts audio → transcript. Zero API cost.</li>
    <li><strong>Process with AI</strong> — transcript sent to <code>POST /api/doctor/structure-note</code>.</li>
    <li><strong>LLM structuring</strong> — <code>structure_clinical_note(transcript)</code> in <code>llm_service.py</code> sends Gemini a strict prompt that mandates: symptoms array, primary diagnosis (not rule-outs), prescriptions with dosage/frequency/duration/<code>is_new</code>/<code>stopped</code>, ICD-10 codes, recommended tests, safety flags.</li>
    <li><strong>Post-processing</strong> — <code>_post_process_structured_note()</code> uses regex on the original transcript to catch monitoring instructions Gemini sometimes skips (e.g. "blood sugar 4 times daily").</li>
    <li><strong>RAG coverage check</strong> — for each prescription, <code>check_medication_coverage()</code> in <code>rag_service.py</code> queries ChromaDB on the patient's policy, sends the relevant chunks to Gemini, gets back <code>{is_covered, alternative}</code>.</li>
    <li><strong>FHIR resource</strong> — <code>_build_fhir_encounter()</code> in <code>doctor.py</code> wraps everything in a FHIR-compliant Encounter JSON — the global standard for healthcare data interoperability.</li>
    <li><strong>Persist</strong> — saved to <code>clinical_notes</code> collection with <code>policy_warnings[]</code> if any meds weren't covered.</li>
</ol>

<h2>Important functions in this module</h2>
<table>
    <tr><th>Function</th><th>File</th><th>What it does</th></tr>
    <tr><td><code>structure_clinical_note()</code></td><td>llm_service.py</td><td>The Gemini call that turns transcript → JSON. Sends a long prompt with extraction rules.</td></tr>
    <tr><td><code>_post_process_structured_note()</code></td><td>llm_service.py</td><td>Regex-based safety net that re-extracts tests / safety flags from the raw transcript if the LLM missed them.</td></tr>
    <tr><td><code>check_medication_coverage()</code></td><td>rag_service.py</td><td>RAG check: pulls policy chunks, asks LLM coverage question per drug.</td></tr>
    <tr><td><code>_build_fhir_encounter()</code></td><td>doctor.py</td><td>Builds a FHIR Encounter resource — interoperable healthcare format.</td></tr>
    <tr><td><code>_evaluate_health_check()</code></td><td>patient.py</td><td>Rule engine for daily check; flagged items show up in Patient Alerts.</td></tr>
</table>

<h2>Patient Alerts — how the rule engine works</h2>
<p>This is a <strong>deterministic rule engine</strong>, not an LLM. Every condition is explicit:</p>
<table>
    <tr><th>Condition</th><th>Flag type</th></tr>
    <tr><td>Wound is bleeding or has discharge</td><td>Severe</td></tr>
    <tr><td>Wound is red or swollen</td><td>Possible infection</td></tr>
    <tr><td>Temperature ≥ 38.5 °C</td><td>Severe</td></tr>
    <tr><td>Pain level ≥ 7 / 10</td><td>Severe</td></tr>
    <tr><td>Appetite = none</td><td>Possible complication</td></tr>
    <tr><td>Mobility = bedridden</td><td>Possible complication</td></tr>
    <tr><td>Medication not taken</td><td>Adherence concern</td></tr>
</table>
<p><code>is_flagged = (len(flags) ≥ 2) OR (any severe flag)</code>. Flagged checks set <code>doctor_notified: true</code> so the doctor sees them in the Patient Alerts inbox.</p>


<!-- ============ SECTION 6 ============ -->
<h1 class="section">6. Module B — Hospital (Billing &amp; Claim Submission)</h1>

<p class="lead">Where the doctor's note becomes money and paperwork.</p>

<h2>Pages</h2>
<table>
    <tr><th>Page</th><th>Path</th><th>Function</th></tr>
    <tr><td>Hospital Dashboard</td><td>/hospital</td><td>KPIs — admitted patients, notes pending billing, claims submitted today.</td></tr>
    <tr><td>Patient Records</td><td>/hospital/patients</td><td>Master list of patients with policy status + latest note.</td></tr>
    <tr><td>Submit Claim</td><td>/hospital/submit-claim</td><td>Discharge-settlement flow: pick clinical note → coverage check → substitute drugs → submit one full claim.</td></tr>
    <tr><td>Daily Bill</td><td>/hospital/daily-bill</td><td>Running tab during the stay; splits insurer vs patient per item.</td></tr>
    <tr><td>Upload Policy</td><td>/hospital/upload-policy</td><td>Reception-side policy upload for walk-in patients.</td></tr>
</table>

<h2>The medication coverage check — RAG in action</h2>
<p>Endpoint: <code>POST /api/hospital/check-medication-coverage</code> — <code>hospital.py</code> lines 189–321.</p>
<ol>
    <li>Look up the patient's policy in <code>policy_documents</code>.</li>
    <li><code>query_policy(policy_id, "drug formulary covered medications excluded ...")</code> — ChromaDB returns the policy chunks most semantically similar to that query.</li>
    <li>Build a strict-pharmacist prompt for Gemini: <em>"For each of these medications, return covered=true/false, quote the exact policy section, and if excluded suggest the closest covered alternative from Section 3.2."</em></li>
    <li>Parse the JSON array, return per-drug status to the frontend.</li>
</ol>

<div class="callout">
    <div class="label">Why this matters</div>
    Without this, the hospital submits a claim, the insurer rejects it three days later for "drug not in formulary", and the patient pays out of pocket. With this, the hospital sees coverage issues <strong>before</strong> the claim is submitted and can swap to a covered drug.
</div>

<h2>Two billing flows — Submit Claim vs Daily Bill</h2>
<table>
    <tr><th></th><th>Submit Claim</th><th>Daily Bill</th></tr>
    <tr><td>When used</td><td>At discharge — one settlement.</td><td>During stay — line-by-line each day.</td></tr>
    <tr><td>Input</td><td>A clinical note (doctor's prescriptions).</td><td>Manual entry, optional demo button.</td></tr>
    <tr><td>Output</td><td>One claim → insurer.</td><td>Two buckets: covered items → insurer claim; uncovered items → patient pays at counter.</td></tr>
    <tr><td>Coverage check</td><td>Per-medication (RAG).</td><td>Per-item (RAG, item by item).</td></tr>
</table>

<h2>Room rate constants</h2>
<p><code>ROOM_RATES</code> in <code>hospital.py</code> — the hospital's standard rates per bed type:</p>
<pre>general:      ₹1,500/day
semi-private: ₹3,000/day
private:      ₹6,000/day
icu:          ₹12,000/day</pre>
<p>The insurer rule engine has its own <strong>caps</strong> (different from the rates) — if the patient's policy is "standard" tier and the hospital charges ₹6,000 for a private room but the cap is ₹4,000, the rule engine flags <strong>₹2,000 excess</strong>. The claim still goes through but at reduced amount.</p>


<!-- ============ SECTION 7 ============ -->
<h1 class="section">7. Module C — Insurer (Clearinghouse)</h1>

<p class="lead">The brain of the operation. Where claims that took 3 days now take 60 seconds.</p>

<h2>Pages</h2>
<table>
    <tr><th>Page</th><th>Path</th><th>Function</th></tr>
    <tr><td>Insurer Dashboard</td><td>/insurer</td><td>Count tiles + single button: "Adjudicate All Pending".</td></tr>
    <tr><td>Claims</td><td>/insurer/claims</td><td>Tabbed worklist: Pending / Adjudicated / Flagged / Approved / Rejected. Single + batch actions. Locked once terminal.</td></tr>
    <tr><td>Analytics</td><td>/insurer/analytics</td><td>Pie (by status), bar (top diagnoses), line (monthly trend) — Recharts.</td></tr>
</table>

<h2>The auto-adjudication rule engine</h2>
<p>File: <code>server/services/adjudication_service.py</code>. <strong>No LLM here</strong> — insurance decisions must be auditable and reproducible. Pure Python rules.</p>

<table>
    <tr><th>#</th><th>Rule</th><th>What it checks</th><th>Effect</th></tr>
    <tr><td>1</td><td>Policy tier</td><td>Policy number prefix (<code>PREM*</code>, <code>STD*</code>, <code>SUP*</code>) → tier.</td><td>Sets per-tier limits.</td></tr>
    <tr><td>2</td><td>Max claim amount</td><td>Total amount vs tier ceiling (basic ₹3L, standard ₹5L, premium ₹10L, super ₹25L).</td><td>Flag + clamp.</td></tr>
    <tr><td>3</td><td>Room rent cap</td><td>For private/deluxe/suite rooms — daily rate vs cap.</td><td>Flag + subtract excess.</td></tr>
    <tr><td>4</td><td>Excluded items</td><td>Item descriptions containing cosmetic / dental / spectacles / vitamins / fertility / ivf.</td><td>Reject the line + deduct.</td></tr>
    <tr><td>5</td><td>Manual-review ICD</td><td>Codes prefixed with <code>C</code> (cancer), <code>Z51</code> (chemo), <code>I21</code> (MI), <code>I63</code> (stroke), <code>K80</code> (gallstones), <code>N20</code> (kidney stones).</td><td>Force manual review.</td></tr>
    <tr><td>6</td><td>Pre-auth keywords</td><td>Diagnosis mentions surgery / chemotherapy / dialysis / transplant / joint replacement / cardiac / angioplasty / bypass.</td><td>Force manual review.</td></tr>
</table>

<h2>Terminal statuses the engine produces</h2>
<div class="kv">
    <span class="k">flagged</span><span>Complex case — needs human review. No recommendation attached. Triggered when manual review is required OR more than 2 flags fire.</span>
    <span class="k">adjudicated</span><span>Rules ran cleanly. The engine attached a recommendation: <code>approve</code> or <code>reject</code>, plus the recommended amount. <strong>The human still presses the final button.</strong></span>
</div>

<div class="callout">
    <div class="label">Key design decision — separation of recommendation and decision</div>
    The engine never writes <code>approved</code> or <code>rejected</code> on its own. It writes <code>adjudicated</code> + a recommendation. The insurer presses the button. This creates an audit trail that regulators love: "machine recommended X, human did Y."
</div>

<h2>Important functions</h2>
<table>
    <tr><th>Function</th><th>File</th><th>What it does</th></tr>
    <tr><td><code>adjudicate_claim(claim)</code></td><td>adjudication_service.py</td><td>The rule engine. Returns status, recommendation, recommended_amount, flag_reasons.</td></tr>
    <tr><td><code>get_policy_tier()</code></td><td>adjudication_service.py</td><td>Maps policy number prefix → tier (basic/standard/premium/super_premium).</td></tr>
    <tr><td><code>auto_adjudicate_claim()</code></td><td>insurer.py</td><td>Runs the engine on one pending claim and persists the result.</td></tr>
    <tr><td><code>adjudicate_all_pending()</code></td><td>insurer.py</td><td>Loops over up to 100 pending claims; returns counts.</td></tr>
    <tr><td><code>batch_approve_claims()</code></td><td>insurer.py</td><td>Bulk-approve at recommended amount; silently skips non-adjudicated claims.</td></tr>
    <tr><td><code>get_analytics()</code></td><td>insurer.py</td><td>Three Mongo aggregation pipelines: status, top diagnoses, monthly trend.</td></tr>
</table>

<h2>The "locked" state</h2>
<p>Once a claim is <code>approved</code> or <code>rejected</code>, both endpoints (<code>/approve</code>, <code>/reject</code>) return 400 instead of mutating it. The frontend hides the action buttons and shows a locked summary with the final amount + date. <strong>Decisions are final by design.</strong></p>


<!-- ============ SECTION 8 ============ -->
<h1 class="section">8. Module D — Patient (Care Companion)</h1>

<p class="lead">Every patient screen either explains or acts. Nothing assumes medical literacy.</p>

<h2>Pages</h2>
<table>
    <tr><th>Page</th><th>Path</th><th>Function</th></tr>
    <tr><td>Patient Dashboard</td><td>/patient</td><td>Tiles + nav.</td></tr>
    <tr><td>Upload Policy</td><td>/patient/upload-policy</td><td>One-time PDF upload — indexed in ChromaDB, reused by every downstream check.</td></tr>
    <tr><td>My Claims</td><td>/patient/claims</td><td>Claim status with plain-language explanations.</td></tr>
    <tr><td>Bill Decoder</td><td>/patient/bill-decoder</td><td>Upload hospital bill image → OCR + LLM analysis.</td></tr>
    <tr><td>Discharge Summary</td><td>/patient/discharge</td><td>Paste English summary → AI simplifies → translates to vernacular → MP3 audio.</td></tr>
    <tr><td>Health Check</td><td>/patient/health-check</td><td>Daily post-discharge form. Rule engine flags concerning answers.</td></tr>
    <tr><td>Payable</td><td>/patient/payable</td><td>Uncovered daily-bill items the patient must pay at the counter.</td></tr>
</table>

<h2>The Bill Decoder pipeline</h2>
<ol>
    <li>Patient uploads a JPEG/PNG/PDF of their hospital bill.</li>
    <li><code>extract_bill_items()</code> in <code>ocr_service.py</code> runs pytesseract on the image, then regex-parses lines like <code>"Paracetamol 500mg ... 120.00"</code> into <code>[{description, amount, category}]</code>.</li>
    <li><code>analyze_bill(items, policy_info)</code> in <code>llm_service.py</code> sends Gemini the line items + policy info and asks for per-item <code>{covered, explanation}</code>, plus total / covered_total / out_of_pocket / plain-English summary.</li>
    <li>Frontend renders three cards (Total / Covered / Out-of-Pocket) and an item table with ✓/✗ icons.</li>
</ol>

<h2>The Discharge Translator pipeline</h2>
<ol>
    <li>Patient pastes English discharge summary (full of jargon: "DVT prophylaxis", "PRN q6h", "antipyresis", etc.)</li>
    <li><code>simplify_discharge_summary()</code> — Gemini rewrites in plain English ("blood thinner to prevent clots").</li>
    <li><code>translate_and_speak()</code> in <code>translation_service.py</code> — <code>deep-translator</code> → target Indian language. Then <code>gTTS</code> generates MP3 saved under <code>audio_files/</code>.</li>
    <li>Frontend shows simplified English, translated text, and a playable audio element with download.</li>
</ol>

<h2>The plain-language claim explainer</h2>
<p><code>_explain_claim_status()</code> in <code>patient.py</code> — a deterministic dict of templates, <strong>not an LLM call</strong>. Reads <code>status</code>, <code>total_amount</code>, <code>approved_amount</code>, <code>rejection_reason</code> and renders sentences like:</p>
<pre>"Your claim for ₹12,185 needs additional review.
 Reason: Room rent ₹6,000/day exceeds cap ₹4,000/day."</pre>
<p>Reason for not using an LLM: response must be instant and 100% predictable. Templates achieve both.</p>

<h2>The Payable flow</h2>
<p>When the hospital saves a daily bill, items that fail coverage land in <code>daily_bills.patient_items[]</code> with a positive <code>patient_total</code>. <code>GET /api/patient/payable</code> queries:</p>
<pre>db.daily_bills.find({
    patient_id: me,
    patient_total: { $gt: 0 },
    patient_paid: { $ne: true }
})</pre>
<p><code>POST /api/patient/payable/{bill_id}/paid</code> sets <code>patient_paid: true</code> after collection at the counter.</p>


<!-- ============ SECTION 9 ============ -->
<h1 class="section">9. Background services — LLM, RAG, OCR, Adjudication</h1>

<h2>LLM Service — <code>server/services/llm_service.py</code></h2>
<p>One module abstracts every LLM call. Provider chosen via <code>LLM_PROVIDER</code> env var: <code>gemini</code> (default), <code>huggingface</code>, or <code>mock</code> (returns hand-crafted JSON for offline demos).</p>

<table>
    <tr><th>Function</th><th>Used by</th><th>What it returns</th></tr>
    <tr><td><code>query_llm(prompt)</code></td><td>Every other function</td><td>Plain text from the LLM. Retry + fallback chain (Gemini → HF → mock).</td></tr>
    <tr><td><code>structure_clinical_note(transcript)</code></td><td>Doctor</td><td>JSON dict with symptoms, diagnosis, prescriptions, etc.</td></tr>
    <tr><td><code>analyze_bill(items, policy_info)</code></td><td>Patient Bill Decoder</td><td>Per-item coverage + summary.</td></tr>
    <tr><td><code>simplify_discharge_summary(text)</code></td><td>Patient Discharge</td><td>Plain English text.</td></tr>
    <tr><td><code>check_policy_coverage(item, policy_context)</code></td><td>Hospital Daily Bill</td><td><code>{is_covered, reason}</code> for one item.</td></tr>
    <tr><td><code>_extract_json(text)</code></td><td>Helper</td><td>Pulls JSON out of LLM responses that may wrap it in markdown code blocks.</td></tr>
</table>

<h2>RAG Service — <code>server/services/rag_service.py</code></h2>
<p>RAG = Retrieval-Augmented Generation. The LLM doesn't know your specific policy PDF, so we <strong>retrieve</strong> the relevant chunks first, then <strong>augment</strong> the LLM prompt with them.</p>

<table>
    <tr><th>Function</th><th>What it does</th></tr>
    <tr><td><code>index_policy_pdf(path, policy_id, insurer)</code></td><td>PyPDF2 reads the PDF → <code>chunk_text()</code> splits into ~500-word overlapping chunks → sentence-transformer embeds them → ChromaDB stores under <code>collection_name = policy_id</code>.</td></tr>
    <tr><td><code>query_policy(policy_id, query, n=3)</code></td><td>Returns the top-3 most semantically similar chunks. This is the "retrieval" half of RAG.</td></tr>
    <tr><td><code>check_medication_coverage(drug, policy_id)</code></td><td>Convenience wrapper — query the policy for that drug, send context to LLM, return covered/excluded + alternative.</td></tr>
</table>

<div class="callout">
    <div class="label">Why RAG and not just one giant LLM call?</div>
    Policy PDFs are 30–60 pages. Sending all of that with every coverage check would (a) blow past context limits, (b) cost a fortune in tokens, (c) be slow. RAG sends only the 3 paragraphs that actually talk about the relevant drug.
</div>

<h2>OCR Service — <code>server/services/ocr_service.py</code></h2>
<p>pytesseract wrapper. <code>extract_bill_items()</code> opens the image with Pillow, runs Tesseract, then <code>_parse_bill_text()</code> regex-extracts line items. Categorization (medication, lab, room, etc.) via a keyword dictionary in <code>_categorize_item()</code>.</p>

<h2>Adjudication Service — <code>server/services/adjudication_service.py</code></h2>
<p>Covered in Section 7. Zero AI. Pure Python rules. ~150 lines. Most-quoted file in viva.</p>

<h2>Translation Service — <code>server/services/translation_service.py</code></h2>
<p><code>translate_and_speak(text, lang)</code> — deep-translator + gTTS → MP3. <code>get_supported_languages()</code> returns the picker options: Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te), Marathi (mr), Gujarati (gu), Kannada (kn), Malayalam (ml), Punjabi (pa), Urdu (ur), plus English.</p>

<h2>Anonymization Service — <code>server/services/anonymization_service.py</code></h2>
<p>Privacy layer used when patient data is aggregated for analytics. Hashes direct identifiers (name, email), generalizes age to 5-year ranges, masks phone numbers, redacts Aadhaar / phone / email patterns from free text. K-anonymity style — patient still uniquely retrievable via ID, but features like name don't appear in analytics outputs.</p>


<!-- ============ SECTION 10 ============ -->
<h1 class="section">10. Glossary — terms you should be ready to define</h1>

<div class="glossary-term">
    <div class="term">FHIR</div>
    <div class="definition">Fast Healthcare Interoperability Resources. A global JSON-based standard from HL7 for sharing healthcare data. We output every clinical note in FHIR Encounter format so any other hospital system could ingest it without translation.</div>
</div>

<div class="glossary-term">
    <div class="term">ICD-10</div>
    <div class="definition">International Classification of Diseases, 10th revision. WHO's standard codes for every diagnosis. <code>J06.9</code> = acute upper respiratory infection. <code>I10</code> = essential hypertension. <code>C50.9</code> = breast cancer. The adjudication engine flags ICD prefixes like <code>C</code> for manual review.</div>
</div>

<div class="glossary-term">
    <div class="term">RAG (Retrieval-Augmented Generation)</div>
    <div class="definition">A pattern where you first retrieve relevant documents from a vector database, then feed those to an LLM as context. Solves the problem of LLMs not knowing private/proprietary data (like a specific insurance policy).</div>
</div>

<div class="glossary-term">
    <div class="term">Vector embedding</div>
    <div class="definition">A list of ~384–1536 floats representing the "meaning" of a piece of text. Texts with similar meanings have vectors with high cosine similarity. ChromaDB stores these so we can search by meaning, not just keyword.</div>
</div>

<div class="glossary-term">
    <div class="term">ChromaDB</div>
    <div class="definition">An open-source embedded vector database. Runs locally — no cloud account needed. We use one collection per policy PDF; chunks are embedded with sentence-transformers (the default).</div>
</div>

<div class="glossary-term">
    <div class="term">JWT (JSON Web Token)</div>
    <div class="definition">A signed token containing user identity. Stateless authentication — server doesn't need to track sessions. Composed of header.payload.signature; signature verifies the server's secret. We store user_id + role in the payload.</div>
</div>

<div class="glossary-term">
    <div class="term">bcrypt</div>
    <div class="definition">Adaptive password hashing function. Slow on purpose — defeats brute force. Includes a salt to defeat rainbow tables. Same algorithm used by Auth0, GitHub, Django.</div>
</div>

<div class="glossary-term">
    <div class="term">Adjudication</div>
    <div class="definition">The insurance term for "deciding whether a claim should be paid." In MediSync, adjudication is the rule-engine step. Result is one of <code>approved</code>, <code>rejected</code>, <code>flagged</code>, or <code>adjudicated</code> (recommendation only, awaiting human).</div>
</div>

<div class="glossary-term">
    <div class="term">Pre-authorization</div>
    <div class="definition">An insurance step where the patient must get insurer approval BEFORE a procedure (typical for surgery, chemo, transplant). The rule engine detects pre-auth-requiring keywords in the diagnosis and forces the claim into manual review.</div>
</div>

<div class="glossary-term">
    <div class="term">Room rent cap</div>
    <div class="definition">A clause in most Indian health policies — the policy will cover up to ₹X per day for room charges. If the patient picks a more expensive room, the excess comes out of pocket. The engine subtracts excess from the recommended amount.</div>
</div>

<div class="glossary-term">
    <div class="term">Formulary</div>
    <div class="definition">The list of drugs an insurance policy covers. RAG checks each prescription against the patient's specific formulary (Section 3.2 of most policies = covered drugs; Section 3.3 = exclusions).</div>
</div>

<div class="glossary-term">
    <div class="term">OCR (Optical Character Recognition)</div>
    <div class="definition">Turning an image of text into actual text characters. We use pytesseract (the Python wrapper for Google's open-source Tesseract engine). Free, offline, works well on printed English bills.</div>
</div>

<div class="glossary-term">
    <div class="term">K-anonymity</div>
    <div class="definition">A privacy principle: any individual should be indistinguishable from at least K others in the dataset. Our anonymization service generalizes age into ranges and hashes direct identifiers to support analytics queries without exposing individuals.</div>
</div>

<div class="glossary-term">
    <div class="term">Motor</div>
    <div class="definition">Async MongoDB driver for Python. Lets FastAPI's async functions await DB queries without blocking. Drop-in replacement for the sync PyMongo client.</div>
</div>

<div class="glossary-term">
    <div class="term">Pydantic</div>
    <div class="definition">Python library for data validation using type hints. Every request body in our API is a Pydantic model — automatic validation, automatic OpenAPI schema generation.</div>
</div>


<!-- ============ SECTION 11 ============ -->
<h1 class="section">11. Likely viva questions &amp; how to answer them</h1>

<div class="callout">
    <div class="label">Q1: "Why use RAG instead of fine-tuning?"</div>
    Fine-tuning needs labeled data, GPU compute, and re-training every time a policy changes. RAG works on day one with zero training — drop a new PDF in, index it, query it. Plus you can cite the exact policy section you used, which is critical for an auditable insurance decision.
</div>

<div class="callout">
    <div class="label">Q2: "Why is the adjudication engine pure Python and not an LLM?"</div>
    Insurance decisions are <strong>legally regulated</strong> and must be 100% reproducible. LLMs are non-deterministic — same input can give different outputs across runs. Pure rules are inspectable: you can show the regulator the exact lines that fired. Also faster (~5 ms vs LLM's 2–3 s).
</div>

<div class="callout">
    <div class="label">Q3: "What happens if Gemini is down or fails to return valid JSON?"</div>
    The fallback chain in <code>llm_service.py</code>: Gemini → HuggingFace → mock. <code>_extract_json()</code> handles three response shapes (markdown code block, bare JSON, embedded). If all fail, the structured note returns a default with <code>diagnosis: "Requires manual review"</code> — the doctor sees this in the UI and re-records.
</div>

<div class="callout">
    <div class="label">Q4: "How do you handle drug name typos from speech-to-text?"</div>
    The Smart Scribe prompt explicitly tells Gemini to <strong>normalize drug names</strong> (e.g. "livo citrzine" → "Levocetirizine") and to flag unverified drugs with <code>[UNVERIFIED DRUG]</code>. The doctor can review and correct before submitting.
</div>

<div class="callout">
    <div class="label">Q5: "Why is the daily bill split per-line and not just a single percentage?"</div>
    Real policies exclude <strong>specific items</strong> (cosmetic, dental, supplements) — not a flat percentage. So the patient owes ₹450 for the multivitamin and ₹800 for the cosmetic cream, NOT 30% of the total. Per-item attribution is what makes the patient's Payable page accurate.
</div>

<div class="callout">
    <div class="label">Q6: "What's the difference between status 'adjudicated' and 'approved'?"</div>
    <strong>adjudicated</strong> = rule engine ran, recommendation attached, awaiting human button-press.<br/>
    <strong>approved</strong> = insurer confirmed; final amount locked. Once approved, no further mutations allowed (backend returns 400; frontend hides buttons).
</div>

<div class="callout">
    <div class="label">Q7: "How does the system know which doctor to alert when a patient submits a flagged health check?"</div>
    The health-check endpoint looks up the patient's <strong>most recent clinical note</strong> and uses its <code>doctor_id</code>. So whoever treated them last gets the alert. If no note exists, <code>doctor_id = "unassigned"</code>.
</div>

<div class="callout">
    <div class="label">Q8: "Can a patient see another patient's claims or notes?"</div>
    No. Every patient route filters by <code>patient_id == current_user.id</code> from the JWT. The role guard <code>require_role(["patient"])</code> blocks anyone but a patient from even reaching these endpoints.
</div>

<div class="callout">
    <div class="label">Q9: "Why not store the policy PDF itself in MongoDB?"</div>
    Two reasons: (1) MongoDB has a 16 MB document limit — fine for most policies but not all; (2) the indexed vectors in ChromaDB are what we actually query against, so the raw PDF is reference data only. We store the file path in <code>policy_documents</code> for re-indexing if needed.
</div>

<div class="callout">
    <div class="label">Q10: "How does the system scale?"</div>
    FastAPI + Motor is async — one process handles ~5,000 concurrent requests. Stateless JWT means horizontal scaling needs no shared session store. MongoDB Atlas auto-scales. ChromaDB can be swapped for hosted Pinecone/Weaviate if needed. Bottleneck would be the Gemini free-tier (60 req/min) — solved by upgrading the API key or routing to the HF fallback.
</div>


<div class="signoff">
    Good luck with your viva. Every screen, every endpoint, every function explained — you've got this.
</div>

</body></html>"""


def build():
    html = HTML(string=HTML_TEXT)
    css = CSS(string=CSS_TEXT)
    html.write_pdf(OUT, stylesheets=[css])
    size_kb = Path(OUT).stat().st_size / 1024
    print(f"Wrote {OUT} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    build()
