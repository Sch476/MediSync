import { useState, useEffect } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import { FiGlobe, FiVolume2, FiDownload, FiSend, FiFileText } from "react-icons/fi";

const SAMPLE_DISCHARGE = `APOLLO CITY HOSPITAL — DISCHARGE SUMMARY

Patient: Priya Patel | Age: 32/F | MRN: 78432
Admission: 12-Apr-2024 | Discharge: 15-Apr-2024
Treating Consultant: Dr. Rajesh Kumar, MD (Internal Medicine)

CHIEF COMPLAINT:
Patient presented to the ED with a 3-day history of productive cough, pyrexia (Tmax 39.2°C), pleuritic chest pain, and progressive dyspnea on exertion.

DIAGNOSIS:
1. Community-Acquired Pneumonia (CAP) — right lower lobe (J18.9)
2. Mild hypoxemia secondary to consolidation
3. Pre-existing controlled essential hypertension (I10)

INVESTIGATIONS:
- CXR (PA view): right lower lobe consolidation
- CBC: WBC 14.2 x10^9/L with neutrophilia
- CRP: 142 mg/L
- Sputum C&S: Streptococcus pneumoniae, sensitive to amoxicillin
- ABG: pH 7.41, PaO2 68 mmHg on room air, SpO2 92%

TREATMENT GIVEN:
- IV Ceftriaxone 1g BD x 3 days, stepped down to PO Amoxicillin-Clavulanate
- IV fluids (NS @ 100 mL/hr) for hydration
- Nebulization with salbutamol q6h PRN
- Paracetamol 650mg PO q6h for antipyresis
- Continued Amlodipine 5mg OD for HTN

DISCHARGE MEDICATIONS:
1. Tab. Amoxicillin-Clavulanate 625mg PO BD x 7 days (complete the course)
2. Tab. Paracetamol 650mg PO PRN for fever/pain (max QDS)
3. Tab. Amlodipine 5mg PO OD (continue as before)
4. Syrup Ambroxol 10mL PO TDS x 5 days
5. Multivitamin OD x 14 days

ADVICE ON DISCHARGE:
- Strict bed rest x 48 hrs, gradual ambulation thereafter
- Adequate hydration (2-3 L/day)
- Avoid smoking and second-hand smoke exposure
- Steam inhalation BD
- Monitor temperature at home; return if fever persists beyond 72 hours
- DVT prophylaxis: ambulation; no anticoagulation indicated
- Diet: high-protein, soft-bland initially

RED FLAG SYMPTOMS — return to ED immediately if:
- Worsening dyspnea or new orthopnea
- Hemoptysis
- Recurrence of fever > 38.5°C
- Chest pain or palpitations
- Confusion or altered sensorium

FOLLOW-UP:
- OPD review with Dr. Rajesh Kumar in 7 days with repeat CBC and CXR
- BP monitoring at home, log daily readings`;

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const PRIMARY = "#4ecdc4";
const API_BASE_URL = "http://localhost:8000";

export default function DischargeSummary() {
  const [summaryText, setSummaryText] = useState("");
  const [languages, setLanguages] = useState({});
  const [targetLanguage, setTargetLanguage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      const res = await api.get("/patient/languages");
      setLanguages(res.data);
      const keys = Object.keys(res.data);
      if (keys.length > 0) setTargetLanguage(keys[0]);
    } catch (err) {
      toast.error("Failed to load languages");
    }
  };

  const handleSubmit = async () => {
    if (!summaryText.trim()) {
      toast.error("Please paste your discharge summary");
      return;
    }
    if (!targetLanguage) {
      toast.error("Please select a target language");
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("summary_text", summaryText);
      formData.append("target_language", targetLanguage);
      const res = await api.post("/patient/translate-discharge", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      toast.success("Translation complete!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to translate summary");
    } finally {
      setLoading(false);
    }
  };

  const audioUrl = result?.audio_path
    ? `${API_BASE_URL}${result.audio_path.startsWith("/") ? "" : "/"}${result.audio_path}`
    : null;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 16px" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        Discharge Summary Translator
      </h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 16 }}>
        Paste your discharge summary below to get a simplified version and translation with audio.
      </p>


      <div style={{ ...cardStyle, marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <label style={{ fontWeight: 600, color: "#2d3436" }}>
            Discharge Summary Text
          </label>
          <button
            type="button"
            onClick={() => setSummaryText(SAMPLE_DISCHARGE)}
            style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "5px 12px", background: "#fffbe6",
              color: "#b8860b", border: "1px dashed #ffd666", borderRadius: 6,
              fontSize: 12, fontWeight: 600, cursor: "pointer",
            }}
          >
            <FiFileText size={12} /> Load Sample
          </button>
        </div>
        <textarea
          value={summaryText}
          onChange={(e) => setSummaryText(e.target.value)}
          placeholder="Paste your discharge summary here..."
          rows={10}
          style={{
            width: "100%",
            padding: 16,
            borderRadius: 8,
            border: "1px solid #dfe6e9",
            fontSize: 15,
            lineHeight: 1.6,
            resize: "vertical",
            fontFamily: "inherit",
            boxSizing: "border-box",
            outline: "none",
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => (e.target.style.borderColor = PRIMARY)}
          onBlur={(e) => (e.target.style.borderColor = "#dfe6e9")}
        />

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginTop: 16,
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, flex: 1, minWidth: 200 }}>
            <FiGlobe size={18} color={PRIMARY} />
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              style={{
                flex: 1,
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid #dfe6e9",
                fontSize: 15,
                background: "#fff",
                cursor: "pointer",
                outline: "none",
              }}
            >
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              background: loading ? "#b2bec3" : PRIMARY,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "12px 24px",
              fontSize: 15,
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "background 0.2s",
            }}
          >
            <FiSend size={16} />
            {loading ? "Translating..." : "Translate & Generate Audio"}
          </button>
        </div>
      </div>


      {loading && (
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div
            style={{
              width: 40,
              height: 40,
              border: `4px solid ${PRIMARY}30`,
              borderTopColor: PRIMARY,
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto 12px",
            }}
          />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <p style={{ color: "#636e72" }}>Translating and generating audio...</p>
        </div>
      )}


      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

          {result.simplified_text && (
            <div style={{ ...cardStyle, borderLeft: `4px solid ${PRIMARY}` }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12, color: "#2d3436" }}>
                Simplified Summary (English)
              </h3>
              <p style={{ color: "#2d3436", lineHeight: 1.7, margin: 0, whiteSpace: "pre-wrap" }}>
                {result.simplified_text}
              </p>
            </div>
          )}


          {result.translated_text && (
            <div style={{ ...cardStyle, borderLeft: "4px solid #a55eea" }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12, color: "#2d3436" }}>
                Translated Text ({languages[targetLanguage] || targetLanguage})
              </h3>
              <p
                style={{
                  color: "#2d3436",
                  lineHeight: 1.7,
                  margin: 0,
                  whiteSpace: "pre-wrap",
                  fontSize: 16,
                }}
              >
                {result.translated_text}
              </p>
            </div>
          )}


          {audioUrl && (
            <div style={{ ...cardStyle, display: "flex", flexDirection: "column", gap: 16 }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, margin: 0, color: "#2d3436" }}>
                <FiVolume2 style={{ verticalAlign: "middle", marginRight: 8 }} />
                Audio Version
              </h3>
              <audio controls style={{ width: "100%" }} src={audioUrl}>
                Your browser does not support the audio element.
              </audio>
              <a
                href={audioUrl}
                download
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  background: PRIMARY,
                  color: "#fff",
                  borderRadius: 8,
                  padding: "10px 20px",
                  fontSize: 14,
                  fontWeight: 600,
                  textDecoration: "none",
                  alignSelf: "flex-start",
                  transition: "opacity 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.85")}
                onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
              >
                <FiDownload size={16} />
                Download MP3
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
