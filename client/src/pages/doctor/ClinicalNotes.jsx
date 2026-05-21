import { useState, useEffect, Fragment } from "react";
import { FiChevronDown, FiChevronUp, FiAlertTriangle } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function ClinicalNotes() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const res = await api.get("/doctor/clinical-notes");
      setNotes(res.data?.notes || res.data || []);
    } catch (err) {
      toast.error("Failed to load clinical notes");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const hasWarnings = (note) => {
    const structured = note.structured_note || note;
    const warnings = structured.policy_warnings || structured.warnings || [];
    return warnings.length > 0;
  };

  const getWarnings = (note) => {
    const structured = note.structured_note || note;
    return structured.policy_warnings || structured.warnings || [];
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 400 }}>
        <p style={{ color: "#666", fontSize: 16 }}>Loading clinical notes...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>Clinical Notes</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>
        All consultation notes and structured records
      </p>

      <div style={card}>
        {notes.length === 0 ? (
          <p style={{ color: "#666", fontSize: 14 }}>No clinical notes found.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #eee" }}>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Date</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Patient</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Diagnosis</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>ICD Codes</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Warnings</th>
                <th style={{ width: 40 }} />
              </tr>
            </thead>
            <tbody>
              {notes.map((note, i) => {
                const id = note._id || note.id || i;
                const structured = note.structured_note || note;
                const icdCodes = structured.icd_codes || [];
                const warnings = getWarnings(note);
                const isExpanded = expandedId === id;
                const prescriptions = structured.prescriptions || [];

                return (
                  <Fragment key={id}>
                    <tr
                      onClick={() => toggleExpand(id)}
                      style={{
                        borderBottom: isExpanded ? "none" : "1px solid #f0f0f0",
                        cursor: "pointer",
                        background: hasWarnings(note) ? "#fffbe6" : "transparent",
                      }}
                    >
                      <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                        {note.created_at ? new Date(note.created_at).toLocaleDateString() : "N/A"}
                      </td>
                      <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                        {note.patient_name || "Unknown"}
                      </td>
                      <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                        {structured.diagnosis || "—"}
                      </td>
                      <td style={{ padding: "10px 8px", fontSize: 14 }}>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                          {icdCodes.length > 0
                            ? icdCodes.map((code, j) => (
                                <span
                                  key={j}
                                  style={{
                                    padding: "2px 8px",
                                    background: "#eee",
                                    borderRadius: 4,
                                    fontSize: 12,
                                    fontFamily: "monospace",
                                    color: "#333",
                                  }}
                                >
                                  {typeof code === "string" ? code : code.code}
                                </span>
                              ))
                            : <span style={{ color: "#999" }}>—</span>}
                        </div>
                      </td>
                      <td style={{ padding: "10px 8px", fontSize: 14 }}>
                        {warnings.length > 0 ? (
                          <span style={{ display: "flex", alignItems: "center", gap: 4, color: "#ffa502" }}>
                            <FiAlertTriangle size={14} />
                            {warnings.length}
                          </span>
                        ) : (
                          <span style={{ color: "#4ecdc4", fontSize: 13 }}>Clear</span>
                        )}
                      </td>
                      <td style={{ padding: "10px 8px" }}>
                        {isExpanded ? <FiChevronUp size={16} color="#666" /> : <FiChevronDown size={16} color="#666" />}
                      </td>
                    </tr>

                    {isExpanded && (
                      <tr style={{ background: hasWarnings(note) ? "#fffbe6" : "#fafafa" }}>
                        <td colSpan={6} style={{ padding: "16px 24px", borderBottom: "1px solid #f0f0f0" }}>

                          {warnings.length > 0 && (
                            <div style={{ marginBottom: 16 }}>
                              {warnings.map((w, wi) => (
                                <div
                                  key={wi}
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 8,
                                    padding: "8px 12px",
                                    marginBottom: 6,
                                    borderRadius: 6,
                                    background: "#ff6b6b12",
                                    border: "1px solid #ff6b6b40",
                                  }}
                                >
                                  <FiAlertTriangle size={14} style={{ color: "#ff6b6b", flexShrink: 0 }} />
                                  <span style={{ color: "#ff6b6b", fontSize: 13 }}>
                                    {w.message || w.description || (typeof w === "string" ? w : JSON.stringify(w))}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}


                          {structured.symptoms && structured.symptoms.length > 0 && (
                            <div style={{ marginBottom: 12 }}>
                              <p style={{ color: "#666", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Symptoms</p>
                              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                                {structured.symptoms.map((s, si) => (
                                  <span
                                    key={si}
                                    style={{
                                      padding: "4px 12px",
                                      background: "#4ecdc418",
                                      color: "#4ecdc4",
                                      borderRadius: 12,
                                      fontSize: 12,
                                      fontWeight: 500,
                                    }}
                                  >
                                    {typeof s === "string" ? s : s.name}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}


                          {(structured.safety_flags || []).length > 0 && (
                            <div style={{ marginBottom: 12, background: "#fff5f5", border: "1px solid #ff6b6b30", borderRadius: 8, padding: "10px 14px" }}>
                              <p style={{ color: "#ff6b6b", fontSize: 12, fontWeight: 600, margin: "0 0 6px" }}>Safety Flags</p>
                              {structured.safety_flags.map((flag, fi) => (
                                <p key={fi} style={{ margin: "0 0 3px", fontSize: 12, color: "#c0392b" }}>
                                  • {typeof flag === "string" ? flag : flag.message || JSON.stringify(flag)}
                                </p>
                              ))}
                            </div>
                          )}


                          {(structured.recommended_tests || []).length > 0 && (
                            <div style={{ marginBottom: 12 }}>
                              <p style={{ color: "#666", fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Recommended Tests</p>
                              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                                {structured.recommended_tests.map((test, ti) => (
                                  <span key={ti} style={{ padding: "3px 10px", background: "#ffa50218", color: "#e67e22", borderRadius: 14, fontSize: 12, fontWeight: 500, border: "1px solid #ffa50240" }}>
                                    {typeof test === "string" ? test : test.name || JSON.stringify(test)}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}


                          {prescriptions.length > 0 && (
                            <div style={{ marginBottom: 12 }}>
                              <p style={{ color: "#666", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Prescriptions</p>
                              <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff", borderRadius: 8 }}>
                                <thead>
                                  <tr style={{ borderBottom: "1px solid #eee" }}>
                                    <th style={{ textAlign: "left", padding: 8, color: "#666", fontSize: 12 }}>Medication</th>
                                    <th style={{ textAlign: "left", padding: 8, color: "#666", fontSize: 12 }}>Dosage</th>
                                    <th style={{ textAlign: "left", padding: 8, color: "#666", fontSize: 12 }}>Frequency</th>
                                    <th style={{ textAlign: "left", padding: 8, color: "#666", fontSize: 12 }}>Duration</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {prescriptions.map((p, pi) => (
                                    <tr key={pi} style={{ borderBottom: "1px solid #f5f5f5", background: p.stopped ? "#ff6b6b08" : "transparent" }}>
                                      <td style={{ padding: 8, fontSize: 13, color: p.stopped ? "#999" : "#333" }}>
                                        <span style={{ textDecoration: p.stopped ? "line-through" : "none" }}>{p.drug || p.name || p.medication}</span>
                                        {p.stopped && <span style={{ marginLeft: 6, fontSize: 10, background: "#ff6b6b", color: "#fff", padding: "1px 6px", borderRadius: 10, fontWeight: 700 }}>STOPPED</span>}
                                        {p.is_new && !p.stopped && <span style={{ marginLeft: 6, fontSize: 10, background: "#4ecdc4", color: "#fff", padding: "1px 6px", borderRadius: 10, fontWeight: 700 }}>NEW</span>}
                                      </td>
                                      <td style={{ padding: 8, fontSize: 13, color: p.stopped ? "#999" : "#333" }}>{p.dosage || "—"}</td>
                                      <td style={{ padding: 8, fontSize: 13, color: p.stopped ? "#999" : "#333" }}>{p.frequency || "—"}</td>
                                      <td style={{ padding: 8, fontSize: 13, color: p.stopped ? "#999" : "#333" }}>{p.duration || "—"}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}


                          {(structured.fhir || note.fhir) && (
                            <div>
                              <p style={{ color: "#666", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>FHIR Resource</p>
                              <pre
                                style={{
                                  background: "#f5f5f5",
                                  padding: 12,
                                  borderRadius: 8,
                                  fontSize: 12,
                                  color: "#333",
                                  overflow: "auto",
                                  maxHeight: 300,
                                  margin: 0,
                                }}
                              >
                                {JSON.stringify(structured.fhir || note.fhir, null, 2)}
                              </pre>
                            </div>
                          )}
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
