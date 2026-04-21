import { useState, useEffect, useRef } from "react";
import { FiMic, FiMicOff, FiCpu } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function Consultation() {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef("");

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

    finalTranscriptRef.current = "";
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-IN";

    recognition.onresult = (event) => {
      let interimTranscript = "";
      // Only process NEW results starting from event.resultIndex
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscriptRef.current += event.results[i][0].transcript + " ";
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }
      // Show finalized text + current interim at the end
      setTranscript(finalTranscriptRef.current + interimTranscript);
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
      formData.append("patient_name", selectedPatient.full_name || selectedPatient.name);

      const res = await api.post("/doctor/structure-note", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(res.data);
      toast.success("Note saved — hospital will handle billing & insurance check");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to process transcript");
    } finally {
      setProcessing(false);
    }
  };

  const structuredNote = result?.structured_note || result || {};
  const symptoms = structuredNote?.symptoms || [];
  const prescriptions = structuredNote?.prescriptions || [];
  const icdCodes = structuredNote?.icd_codes || [];
  const recommendedTests = structuredNote?.recommended_tests || [];
  const safetyFlags = structuredNote?.safety_flags || [];

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
          {selectedPatient?.policy_id && (
            <span style={{ fontSize: 13, color: "#4ecdc4", padding: "6px 12px", background: "#4ecdc418", borderRadius: 8 }}>
              Policy auto-linked
            </span>
          )}
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

            {/* Safety Flags */}
            {safetyFlags.length > 0 && (
              <div style={{ marginBottom: 16, background: "#fff5f5", border: "1px solid #ff6b6b30", borderRadius: 8, padding: "12px 16px" }}>
                <p style={{ color: "#ff6b6b", fontSize: 13, fontWeight: 600, margin: "0 0 8px" }}>Safety Flags</p>
                {safetyFlags.map((flag, i) => (
                  <p key={i} style={{ margin: "0 0 4px", fontSize: 13, color: "#c0392b" }}>
                    • {typeof flag === "string" ? flag : flag.message || JSON.stringify(flag)}
                  </p>
                ))}
              </div>
            )}

            {/* Recommended Tests */}
            {recommendedTests.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <p style={{ color: "#666", fontSize: 13, marginBottom: 8, fontWeight: 600 }}>Recommended Tests</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {recommendedTests.map((test, i) => (
                    <span key={i} style={{ padding: "5px 14px", background: "#ffa50218", color: "#e67e22", borderRadius: 16, fontSize: 13, fontWeight: 500, border: "1px solid #ffa50240" }}>
                      {typeof test === "string" ? test : test.name || JSON.stringify(test)}
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
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Frequency</th>
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Duration</th>
                      <th style={{ textAlign: "left", padding: "8px", color: "#666", fontSize: 13 }}>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prescriptions.map((p, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid #f0f0f0", background: p.stopped ? "#ff6b6b08" : "transparent" }}>
                        <td style={{ padding: 8, fontSize: 14, color: p.stopped ? "#999" : "#333" }}>
                          <span style={{ textDecoration: p.stopped ? "line-through" : "none" }}>{p.drug || p.name || p.medication}</span>
                          {p.stopped && <span style={{ marginLeft: 8, fontSize: 10, background: "#ff6b6b", color: "#fff", padding: "2px 8px", borderRadius: 10, fontWeight: 700 }}>STOPPED</span>}
                          {p.is_new && !p.stopped && <span style={{ marginLeft: 8, fontSize: 10, background: "#4ecdc4", color: "#fff", padding: "2px 8px", borderRadius: 10, fontWeight: 700 }}>NEW</span>}
                        </td>
                        <td style={{ padding: 8, fontSize: 14, color: p.stopped ? "#999" : "#333" }}>{p.dosage || "—"}</td>
                        <td style={{ padding: 8, fontSize: 14, color: p.stopped ? "#999" : "#333" }}>{p.frequency || "—"}</td>
                        <td style={{ padding: 8, fontSize: 14, color: p.stopped ? "#999" : "#333" }}>{p.duration || "—"}</td>
                        <td style={{ padding: 8, fontSize: 14, color: "#666" }}>{p.notes || p.instructions || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </>
      )}
    </div>
  );
}
