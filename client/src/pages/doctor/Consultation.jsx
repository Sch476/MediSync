import { useState, useEffect, useRef } from "react";
import { FiMic, FiMicOff, FiCpu, FiSend, FiAlertCircle } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function Consultation() {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [showClaimForm, setShowClaimForm] = useState(false);
  const [policyId, setPolicyId] = useState("");
  const [claimForm, setClaimForm] = useState({
    policy_number: "",
    insurer_name: "",
    room_type: "",
  });
  const recognitionRef = useRef(null);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const res = await api.get("/doctor/patients");
      setPatients(res.data?.patients || res.data || []);
    } catch (err) {
      toast.error("Failed to load patients");
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast.error("Speech recognition is not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let finalTranscript = "";
      let interimTranscript = "";
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript + " ";
        } else {
          interimTranscript += result[0].transcript;
        }
      }
      setTranscript((prev) => {
        const base = prev.replace(/\[listening\.\.\.\]$/, "").trimEnd();
        const combined = base + (base ? " " : "") + finalTranscript;
        return interimTranscript ? combined + interimTranscript : combined;
      });
    };

    recognition.onerror = (event) => {
      toast.error("Speech recognition error: " + event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
    toast.success("Recording started");
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsRecording(false);
    toast.success("Recording stopped");
  };

  const processWithAI = async () => {
    if (!transcript.trim()) {
      toast.error("Please provide a transcript first");
      return;
    }
    if (!selectedPatient) {
      toast.error("Please select a patient");
      return;
    }

    setProcessing(true);
    try {
      const formData = new FormData();
      formData.append("transcript", transcript);
      formData.append("patient_id", selectedPatient._id || selectedPatient.id);
      formData.append("patient_name", selectedPatient.name);
      if (policyId) formData.append("policy_id", policyId);

      const res = await api.post("/doctor/structure-note", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(res.data);
      toast.success("Note structured successfully");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to process transcript");
    } finally {
      setProcessing(false);
    }
  };

  const submitClaim = async () => {
    if (!claimForm.policy_number || !claimForm.insurer_name) {
      toast.error("Please fill in required claim fields");
      return;
    }

    try {
      const structuredNote = result?.structured_note || result;
      const prescriptions = structuredNote?.prescriptions || [];
      const claimItems = prescriptions.map((p) => ({
        name: p.drug || p.name || p.medication,
        dosage: p.dosage || "",
        duration: p.duration || "",
        cost: p.cost || 0,
      }));

      const payload = {
        ...claimForm,
        patient_id: selectedPatient._id || selectedPatient.id,
        patient_name: selectedPatient.name,
        diagnosis: structuredNote?.diagnosis || "",
        icd_codes: structuredNote?.icd_codes || [],
        items: claimItems,
        note_id: result?.note_id || result?._id,
      };

      await api.post("/doctor/submit-claim", payload);
      toast.success("Claim submitted successfully");
      setShowClaimForm(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit claim");
    }
  };

  const structuredNote = result?.structured_note || result || {};
  const symptoms = structuredNote?.symptoms || [];
  const prescriptions = structuredNote?.prescriptions || [];
  const icdCodes = structuredNote?.icd_codes || [];
  const warnings = structuredNote?.policy_warnings || structuredNote?.warnings || [];

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>Smart Scribe</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>
        AI-powered consultation note generator
      </p>

      {/* Patient Selector */}
      <div style={{ ...card, marginBottom: 20 }}>
        <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 12 }}>Select Patient</h3>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <select
            value={selectedPatient ? (selectedPatient._id || selectedPatient.id || "") : ""}
            onChange={(e) => {
              const p = patients.find((p) => (p._id || p.id) === e.target.value);
              setSelectedPatient(p || null);
            }}
            style={{
              flex: 1,
              minWidth: 200,
              padding: "10px 12px",
              border: "1px solid #ddd",
              borderRadius: 8,
              fontSize: 14,
              color: "#333",
              background: "#fff",
            }}
          >
            <option value="">-- Select a patient --</option>
            {patients.map((p) => (
              <option key={p._id || p.id} value={p._id || p.id}>
                {p.name} {p.email ? `(${p.email})` : ""}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Policy ID (optional)"
            value={policyId}
            onChange={(e) => setPolicyId(e.target.value)}
            style={{
              padding: "10px 12px",
              border: "1px solid #ddd",
              borderRadius: 8,
              fontSize: 14,
              width: 200,
              color: "#333",
            }}
          />
        </div>
      </div>

      {/* Speech-to-Text */}
      <div style={{ ...card, marginBottom: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h3 style={{ color: "#333", fontSize: 16, margin: 0 }}>Consultation Transcript</h3>
          <button
            onClick={toggleRecording}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 20px",
              background: isRecording ? "#ff6b6b" : "#4ecdc4",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {isRecording ? <FiMicOff size={16} /> : <FiMic size={16} />}
            {isRecording ? "Stop Recording" : "Start Recording"}
          </button>
        </div>
        {isRecording && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: "#ff6b6b",
                display: "inline-block",
                animation: "pulse 1.5s infinite",
              }}
            />
            <span style={{ color: "#ff6b6b", fontSize: 13, fontWeight: 600 }}>Recording in progress...</span>
          </div>
        )}
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Start recording or type your consultation notes here..."
          rows={8}
          style={{
            width: "100%",
            padding: 12,
            border: "1px solid #ddd",
            borderRadius: 8,
            fontSize: 14,
            color: "#333",
            resize: "vertical",
            fontFamily: "inherit",
            lineHeight: 1.6,
            boxSizing: "border-box",
          }}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 12 }}>
          <button
            onClick={processWithAI}
            disabled={processing}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 24px",
              background: processing ? "#999" : "#4ecdc4",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: processing ? "not-allowed" : "pointer",
            }}
          >
            <FiCpu size={16} />
            {processing ? "Processing..." : "Process with AI"}
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Policy Warnings */}
          {warnings.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              {warnings.map((w, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 10,
                    padding: 16,
                    marginBottom: 8,
                    borderRadius: 10,
                    background: w.severity === "high" ? "#ff6b6b18" : "#ffa50218",
                    border: `1px solid ${w.severity === "high" ? "#ff6b6b" : "#ffa502"}`,
                  }}
                >
                  <FiAlertCircle
                    size={20}
                    style={{ color: w.severity === "high" ? "#ff6b6b" : "#ffa502", flexShrink: 0, marginTop: 2 }}
                  />
                  <div>
                    <p style={{ margin: 0, fontWeight: 600, color: w.severity === "high" ? "#ff6b6b" : "#ffa502", fontSize: 14 }}>
                      {w.title || "Policy Warning"}
                    </p>
                    <p style={{ margin: "4px 0 0", color: "#666", fontSize: 13 }}>
                      {w.message || w.description || (typeof w === "string" ? w : JSON.stringify(w))}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Structured Note */}
          <div style={{ ...card, marginBottom: 20 }}>
            <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 16 }}>Structured Note</h3>

            {/* Symptoms */}
            {symptoms.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <p style={{ color: "#666", fontSize: 13, marginBottom: 8, fontWeight: 600 }}>Symptoms</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {symptoms.map((s, i) => (
                    <span
                      key={i}
                      style={{
                        padding: "5px 14px",
                        background: "#4ecdc418",
                        color: "#4ecdc4",
                        borderRadius: 16,
                        fontSize: 13,
                        fontWeight: 500,
                      }}
                    >
                      {typeof s === "string" ? s : s.name || s.description}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Diagnosis */}
            {structuredNote.diagnosis && (
              <div style={{ marginBottom: 16 }}>
                <p style={{ color: "#666", fontSize: 13, marginBottom: 4, fontWeight: 600 }}>Diagnosis</p>
                <p style={{ color: "#333", fontSize: 15, margin: 0 }}>{structuredNote.diagnosis}</p>
              </div>
            )}

            {/* ICD Codes */}
            {icdCodes.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <p style={{ color: "#666", fontSize: 13, marginBottom: 8, fontWeight: 600 }}>ICD Codes</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {icdCodes.map((code, i) => (
                    <span
                      key={i}
                      style={{
                        padding: "4px 12px",
                        background: "#eee",
                        color: "#333",
                        borderRadius: 6,
                        fontSize: 13,
                        fontFamily: "monospace",
                      }}
                    >
                      {typeof code === "string" ? code : `${code.code} - ${code.description}`}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Prescriptions Table */}
            {prescriptions.length > 0 && (
              <div>
                <p style={{ color: "#666", fontSize: 13, marginBottom: 8, fontWeight: 600 }}>Prescriptions</p>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #eee" }}>
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Medication</th>
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Dosage</th>
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Duration</th>
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prescriptions.map((p, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid #f0f0f0" }}>
                        <td style={{ padding: 8, fontSize: 14, color: "#333" }}>{p.drug || p.name || p.medication}</td>
                        <td style={{ padding: 8, fontSize: 14, color: "#333" }}>{p.dosage || "—"}</td>
                        <td style={{ padding: 8, fontSize: 14, color: "#333" }}>{p.duration || "—"}</td>
                        <td style={{ padding: 8, fontSize: 14, color: "#666" }}>{p.notes || p.instructions || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Submit Claim */}
          <div style={{ ...card, marginBottom: 20 }}>
            {!showClaimForm ? (
              <button
                onClick={() => setShowClaimForm(true)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "10px 24px",
                  background: "#4ecdc4",
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                <FiSend size={16} />
                Submit Claim
              </button>
            ) : (
              <div>
                <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 16 }}>Claim Details</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                  <div>
                    <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 4 }}>Policy Number *</label>
                    <input
                      type="text"
                      value={claimForm.policy_number}
                      onChange={(e) => setClaimForm({ ...claimForm, policy_number: e.target.value })}
                      style={{
                        width: "100%",
                        padding: "10px 12px",
                        border: "1px solid #ddd",
                        borderRadius: 8,
                        fontSize: 14,
                        color: "#333",
                        boxSizing: "border-box",
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 4 }}>Insurer Name *</label>
                    <input
                      type="text"
                      value={claimForm.insurer_name}
                      onChange={(e) => setClaimForm({ ...claimForm, insurer_name: e.target.value })}
                      style={{
                        width: "100%",
                        padding: "10px 12px",
                        border: "1px solid #ddd",
                        borderRadius: 8,
                        fontSize: 14,
                        color: "#333",
                        boxSizing: "border-box",
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 4 }}>Room Type</label>
                    <select
                      value={claimForm.room_type}
                      onChange={(e) => setClaimForm({ ...claimForm, room_type: e.target.value })}
                      style={{
                        width: "100%",
                        padding: "10px 12px",
                        border: "1px solid #ddd",
                        borderRadius: 8,
                        fontSize: 14,
                        color: "#333",
                        background: "#fff",
                        boxSizing: "border-box",
                      }}
                    >
                      <option value="">-- Select --</option>
                      <option value="general">General Ward</option>
                      <option value="semi-private">Semi-Private</option>
                      <option value="private">Private</option>
                      <option value="icu">ICU</option>
                    </select>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 12 }}>
                  <button
                    onClick={submitClaim}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: "10px 24px",
                      background: "#4ecdc4",
                      color: "#fff",
                      border: "none",
                      borderRadius: 8,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    <FiSend size={16} />
                    Submit
                  </button>
                  <button
                    onClick={() => setShowClaimForm(false)}
                    style={{
                      padding: "10px 24px",
                      background: "#eee",
                      color: "#666",
                      border: "none",
                      borderRadius: 8,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
