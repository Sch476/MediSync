# MediSync — Happy Flow Walkthrough

Complete end-to-end demo showing all 4 roles in sequence.

**Scenario:** Patient P1 visits the hospital with a respiratory infection. All stakeholders interact through MediSync from admission to claim settlement.

**Demo credentials (all use password `password123`):**

| Role | Email |
|---|---|
| Patient | patient@demo.com |
| Doctor | doctor@demo.com |
| Hospital | hospital@demo.com |
| Insurer | insurer@demo.com |

---

## Step 1 — Patient Uploads Insurance Policy

**Login:** `patient@demo.com`

**Sidebar → My Insurance Policy**

1. Enter insurer name: `Star Health Insurance`
2. Drag and drop the policy PDF into the upload area
3. Click **Upload Policy**
4. Green success card appears:
   - Insurer: Star Health Insurance
   - Upload date shown
   - Message: "Your doctor sees coverage warnings automatically"

> This indexes the PDF in ChromaDB. Every coverage check from this point reads the actual policy — no guessing.

**What the patient dashboard looks like:**

```
Welcome back, P1
Here is your health overview for today

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Active Claims│ │ Health Check │ │ Last Check   │
│      0       │ │   Streak: 0  │ │    N/A       │
└──────────────┘ └──────────────┘ └──────────────┘

Quick Actions:
[Bill Decoder] [Discharge Summary] [Health Check] [My Claims]
```

---

## Step 2 — Doctor Records Consultation

**Login:** `doctor@demo.com`

**Sidebar → Smart Scribe**

1. Select patient: **P1**
2. Click the red **mic button** to start recording
3. Speak (or paste into the transcript box):

> "Patient complains of fever for 3 days, cough with yellowish sputum, and body aches. Temperature 101 degrees Fahrenheit. Chest is clear on auscultation. Prescribing Paracetamol 500mg three times daily for 5 days, Azithromycin 500mg once daily for 3 days, and Cetirizine 10mg at bedtime for 5 days."

4. Click **Stop Recording**, then **Structure Note**
5. Gemini processes the transcript and returns:

```
Symptoms:     fever, cough with yellowish sputum, body aches
Diagnosis:    Acute Upper Respiratory Infection
ICD Code:     J06.9

Prescriptions:
  ✅ Paracetamol 500mg    — 1 tablet, 3× daily, 5 days
  ✅ Azithromycin 500mg   — 1 tablet, 1× daily, 3 days
  ✅ Cetirizine 10mg      — 1 tablet, bedtime, 5 days

Coverage: checked against P1's uploaded Star Health policy
```

6. Click **Save Note**

**What the doctor dashboard shows after saving:**

```
Welcome, Dr. Test Doctor

┌──────────────┐ ┌──────────────┐
│ Total Notes  │ │Patient Alerts│
│      1       │ │      0       │
└──────────────┘ └──────────────┘

Recent Clinical Notes:
DATE        PATIENT   DIAGNOSIS                         STATUS
Today       P1        Acute Upper Respiratory Infection  Draft
```

---

## Step 3 — Hospital Creates Daily Bill

**Login:** `hospital@demo.com`

**Sidebar → Daily Bill**

1. Select patient: **P1**
2. Items auto-load from the latest clinical note:

```
AUTO  Doctor Consultation Fee    consultation   ₹600     Pending check
AUTO  Paracetamol 500mg          medication     ₹150     Pending check
AUTO  Azithromycin 500mg         medication     ₹150     Pending check
AUTO  Cetirizine 10mg            medication     ₹150     Pending check
```

3. (Optional) Add extra items manually:

```
      CBC Blood Test              lab            ₹300     Pending check
```

4. Click **Check All Coverage** — all 5 items are verified against the real policy in parallel:

```
AUTO  Doctor Consultation Fee    consultation   ₹600   ✅ Covered    Insurer
AUTO  Paracetamol 500mg          medication     ₹150   ✅ Covered    Insurer
AUTO  Azithromycin 500mg         medication     ₹150   ✅ Covered    Insurer
AUTO  Cetirizine 10mg            medication     ₹150   ✅ Covered    Insurer
      CBC Blood Test              lab            ₹300   ✅ Covered    Insurer
```

5. Split summary appears:

```
┌──────────────────────────┐  ┌──────────────────────────┐
│  INSURANCE PAYS          │  │  PATIENT PAYS AT COUNTER │
│  ₹1,350                  │  │  ₹0                      │
│  5 items → claim sent    │  │  0 items                 │
└──────────────────────────┘  └──────────────────────────┘
```

6. Click **Save Bill & Submit to Insurer**

7. Success screen:

```
        ✅ Daily Bill Processed

┌─────────────────┐  ┌─────────────────┐
│ Insurance Claim  │  │ Patient Pays Now│
│ ₹1,350           │  │ ₹0              │
│ Claim: ...a3f8   │  │ Collect at ctr  │
└─────────────────┘  └─────────────────┘

        [New Daily Bill]
```

---

## Step 4 — Insurer Adjudicates the Claim

**Login:** `insurer@demo.com`

**Sidebar → Claims**

1. Find the new claim in the table:

```
DATE     PATIENT  DOCTOR       DIAGNOSIS              AMOUNT     STATUS
Today    P1       Test Doctor  Daily Bill — 2026-04-21 ₹1,350.00  Pending
```

2. Click the row to expand → see the 5 itemized line items
3. Click **Auto-Adjudicate**

The rule engine runs:
- ₹1,350 is within STD policy limit (₹5,00,000) ✅
- No excluded items ✅
- No private/deluxe room ✅
- ICD code J06.9 is in the auto-approve list ✅

Result: **Approved** — approved amount ₹1,350

```
Status: ✅ Approved
Notes: "Auto-approved: standard procedure with valid ICD codes"
```

**Sidebar → Analytics** — charts update:
- Total Claims count +1
- Approval Rate shown
- "Acute Upper Respiratory Infection" appears in Top Diagnoses bar chart
- Monthly trend line updates

---

## Step 5 — Patient Checks Claim Status

**Login:** `patient@demo.com`

**Sidebar → My Claims**

```
✅ APPROVED    Today

Daily Bill — 2026-04-21
"Great news! Your claim has been approved for ₹1,350."

Amount: ₹1,350.00
```

**Sidebar → My Payable**

```
┌──────────────────────────────────────────┐
│  TOTAL AMOUNT PAYABLE AT COUNTER         │
│  ₹0  ✅  Nothing outstanding!            │
└──────────────────────────────────────────┘

No outstanding payable items.
```

> Everything was covered — nothing to pay at the counter.

---

## Step 6 — Patient Submits Post-Discharge Health Check

**Sidebar → Health Check**

1. Fill out the daily recovery form:
   - Wound condition: **Normal**
   - Fever: **No**
   - Temperature: **36.8°C**
   - Pain level: **2/10**
   - Appetite: **Normal**
   - Mobility: **Normal**
   - Medication taken: **Yes**
   - Notes: "Feeling much better today"

2. Click **Submit**

Result: "Health check submitted. Everything looks good!" — no flags, doctor is NOT notified.

---

## Step 7 — Patient Uses Bill Decoder (Optional)

**Sidebar → Bill Decoder**

1. Upload a hospital bill image (e.g. `sample_hospital_bill.png`)
2. OCR extracts line items from the image
3. LLM analyzes each charge against the patient's policy
4. Result shows:

```
Plain Language Summary:
"Most of your charges are covered under your Star Health policy..."

Bill Summary:
┌──────────┐ ┌──────────────┐ ┌──────────────┐
│  Total   │ │ Covered Amt  │ │ Out-of-Pocket│
│ ₹11,707  │ │ ₹8,707       │ │ ₹3,000       │
└──────────┘ └──────────────┘ └──────────────┘

Items:
Consultation Fee     ₹500    ✅  Standard consultation
Room (Deluxe)        ₹8,000  ❌  Exceeds room rent cap
...
```

---

## Step 8 — Patient Uses Discharge Summary (Optional)

**Sidebar → Discharge Summary**

1. Paste the doctor's discharge notes
2. Select language: **Hindi** (or Bengali, Tamil, etc.)
3. Click **Translate**
4. Result:
   - Simplified plain-language explanation (no medical jargon)
   - Translated text in selected language
   - Downloadable **MP3 audio** of the translation

---

## End-to-End Flow Diagram

```
PATIENT              DOCTOR              HOSPITAL             INSURER
───────              ──────              ────────             ───────
Upload Policy ─┐
               │
               ├──► Smart Scribe ──► Daily Bill ──────► Claims
               │    (records note)   (auto-loads items,  (auto-adjudicate
               │                      checks coverage,    → approved)
               │                      submits claim)
               │
My Claims ◄────┼──────────────────────────────────────── ₹1,350 approved
               │
My Payable ◄───┘    ₹0 due (all covered)

Health Check ──► Doctor sees "All OK" in Patient Alerts
Bill Decoder ──► OCR + LLM analysis of any bill image
Discharge ─────► Simplified + translated + audio MP3
```

---

## Key Points for Demo

| What to show | Where |
|---|---|
| Policy is actually read, not guessed | Coverage check quotes specific policy sections |
| Items auto-load from doctor's note | Hospital doesn't type anything manually |
| Itemized bill sent to insurer | Insurer sees 5 line items, not a lump sum |
| Patient knows exactly what they owe | My Payable shows ₹0 with green banner |
| Auto-adjudication with real rules | ICD codes, room caps, exclusions all checked |
| Post-discharge monitoring | Health Check flags alert the doctor |
