import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FiUser, FiFileText, FiClipboard, FiChevronDown, FiChevronUp, FiShield, FiAlertCircle, FiCheckCircle, FiXCircle, FiRefreshCw } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = { background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" };

export default function PatientRecords() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);

  const [coverageChecking, setCoverageChecking] = useState({});
  const [coverageResults, setCoverageResults] = useState({});

  const [acceptedSubs, setAcceptedSubs] = useState({});

  useEffect(() => {
    api.get("/hospital/patients")
      .then((r) => setPatients(Array.isArray(r.data) ? r.data : []))
      .catch(() => toast.error("Failed to load patients"))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id) => setExpanded(expanded === id ? null : id);

  const acceptSubstitution = (patientId, original, replacement) => {
    setAcceptedSubs((prev) => ({
      ...prev,
      [patientId]: { ...(prev[patientId] || {}), [original]: replacement },
    }));
    toast.success(`Switched to ${replacement}`);
  };

  const checkCoverage = async (patientId, noteId) => {
    setCoverageChecking((prev) => ({ ...prev, [patientId]: true }));
    try {
      const r = await api.post("/hospital/check-medication-coverage", {
        patient_id: patientId,
        note_id: noteId,
      });
      setCoverageResults((prev) => ({ ...prev, [patientId]: r.data }));
    } catch (err) {
      toast.error(err.response?.data?.detail || "Coverage check failed");
    } finally {
      setCoverageChecking((prev) => ({ ...prev, [patientId]: false }));
    }
  };

  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 400 }}>
      <p style={{ color: "#666" }}>Loading patient records...</p>
    </div>
  );

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>Patient Records</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>All admitted patients and their latest clinical notes</p>

      {patients.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: 60, color: "#666" }}>No patients found.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {patients.map((p) => {
            const id = p.id || p._id;
            const note = p.latest_note;
            const isOpen = expanded === id;
            return (
              <div key={id} style={{ ...card, padding: 0, overflow: "hidden" }}>

                <div
                  style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 24px", cursor: "pointer" }}
                  onClick={() => toggle(id)}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{ width: 40, height: 40, borderRadius: "50%", background: "#4ecdc418", display: "flex", alignItems: "center", justifyContent: "center", color: "#4ecdc4" }}>
                      <FiUser size={18} />
                    </div>
                    <div>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: 15, color: "#2d3436" }}>{p.full_name}</p>
                      <p style={{ margin: "2px 0 0", fontSize: 12, color: "#636e72" }}>{p.email}</p>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    {p.has_policy ? (
                      <span style={{ fontSize: 12, color: "#4ecdc4", background: "#4ecdc418", padding: "3px 10px", borderRadius: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <FiShield size={11} /> Policy linked
                      </span>
                    ) : (
                      <span style={{ fontSize: 12, color: "#ffa502", background: "#ffa50218", padding: "3px 10px", borderRadius: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <FiAlertCircle size={11} /> No policy
                      </span>
                    )}
                    {note ? (
                      <span style={{ fontSize: 12, color: "#636e72", background: "#f0f0f0", padding: "3px 10px", borderRadius: 12, display: "flex", alignItems: "center", gap: 4 }}>
                        <FiFileText size={11} /> {note.diagnosis || "Note available"}
                      </span>
                    ) : (
                      <span style={{ fontSize: 12, color: "#aaa", background: "#f8f8f8", padding: "3px 10px", borderRadius: 12 }}>No notes yet</span>
                    )}
                    {isOpen ? <FiChevronUp color="#636e72" /> : <FiChevronDown color="#636e72" />}
                  </div>
                </div>


                {isOpen && note && (
                  <div style={{ borderTop: "1px solid #f0f0f0", padding: "20px 24px", background: "#fafafa" }}>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
                      <div>
                        <p style={{ color: "#636e72", fontSize: 12, margin: "0 0 4px", fontWeight: 600 }}>DIAGNOSIS</p>
                        <p style={{ color: "#2d3436", fontSize: 14, margin: 0 }}>{note.diagnosis || "—"}</p>
                      </div>
                      <div>
                        <p style={{ color: "#636e72", fontSize: 12, margin: "0 0 4px", fontWeight: 600 }}>ICD CODES</p>
                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                          {(note.icd_codes || []).map((c, i) => (
                            <span key={i} style={{ padding: "2px 8px", background: "#eee", borderRadius: 4, fontSize: 12, fontFamily: "monospace" }}>{c}</span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p style={{ color: "#636e72", fontSize: 12, margin: "0 0 4px", fontWeight: 600 }}>SYMPTOMS</p>
                        <p style={{ color: "#2d3436", fontSize: 14, margin: 0 }}>{(note.symptoms || []).join(", ") || "—"}</p>
                      </div>
                      <div>
                        <p style={{ color: "#636e72", fontSize: 12, margin: "0 0 4px", fontWeight: 600 }}>PRESCRIBED MEDICATIONS</p>
                        <p style={{ color: "#2d3436", fontSize: 14, margin: 0 }}>
                          {(note.prescriptions || []).map((rx) => rx.medication || rx.drug).join(", ") || "—"}
                        </p>
                      </div>
                    </div>


                    {p.has_policy && (note.prescriptions || []).length > 0 && (
                      <div style={{ marginBottom: 20 }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                          <p style={{ color: "#636e72", fontSize: 12, margin: 0, fontWeight: 600 }}>INSURANCE COVERAGE CHECK</p>
                          <button
                            onClick={() => checkCoverage(id, note.id)}
                            disabled={coverageChecking[id]}
                            style={{
                              display: "flex", alignItems: "center", gap: 6,
                              padding: "6px 14px",
                              background: coverageChecking[id] ? "#eee" : "#1a1a2e",
                              color: coverageChecking[id] ? "#999" : "#4ecdc4",
                              border: "1px solid #4ecdc4",
                              borderRadius: 6, fontSize: 12, fontWeight: 600,
                              cursor: coverageChecking[id] ? "not-allowed" : "pointer",
                            }}
                          >
                            <FiRefreshCw size={12} style={{ animation: coverageChecking[id] ? "spin 1s linear infinite" : "none" }} />
                            {coverageChecking[id] ? "Checking..." : coverageResults[id] ? "Re-check" : "Check Coverage"}
                          </button>
                        </div>

                        {coverageResults[id] && (
                          <div style={{ background: "#fff", border: "1px solid #e0e0e0", borderRadius: 8, overflow: "hidden" }}>
                            <div style={{ padding: "8px 14px", background: "#f8f9fa", borderBottom: "1px solid #e0e0e0", fontSize: 12, color: "#636e72" }}>
                              Policy: <strong>{coverageResults[id].insurer_name}</strong> &nbsp;|&nbsp; {coverageResults[id].policy_id}
                            </div>
                            {coverageResults[id].results.map((item, i) => (
                              <div key={i} style={{
                                padding: "12px 14px",
                                borderBottom: i < coverageResults[id].results.length - 1 ? "1px solid #f0f0f0" : "none",
                                background: item.is_covered ? "#f0fffe" : "#fff8f8",
                              }}>
                                <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                                  {item.is_covered
                                    ? <FiCheckCircle size={16} color="#4ecdc4" style={{ marginTop: 2, flexShrink: 0 }} />
                                    : <FiXCircle size={16} color="#ff6b6b" style={{ marginTop: 2, flexShrink: 0 }} />
                                  }
                                  <div style={{ flex: 1 }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                                      <span style={{ fontWeight: 700, fontSize: 13, color: "#2d3436" }}>{item.medication}</span>
                                      {item.dosage && <span style={{ fontSize: 12, color: "#636e72" }}>{item.dosage}</span>}
                                      <span style={{
                                        fontSize: 11, fontWeight: 600, padding: "1px 8px", borderRadius: 10,
                                        background: item.is_covered ? "#4ecdc420" : "#ff6b6b20",
                                        color: item.is_covered ? "#4ecdc4" : "#ff6b6b",
                                      }}>
                                        {item.is_covered ? "Covered" : "Excluded"}
                                      </span>
                                    </div>
                                    <p style={{ margin: 0, fontSize: 12, color: "#636e72" }}>{item.reason}</p>


                                    {!item.is_covered && item.alternative && (() => {
                                      const isAccepted = acceptedSubs[id]?.[item.medication] === item.alternative;
                                      return (
                                        <div style={{
                                          marginTop: 8, padding: "10px 12px",
                                          background: isAccepted ? "#f0fff4" : "#fff9e6",
                                          border: `1px solid ${isAccepted ? "#4ecdc4" : "#ffc107"}`,
                                          borderRadius: 6,
                                          display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10,
                                        }}>
                                          <div>
                                            <p style={{ margin: "0 0 2px", fontSize: 12, fontWeight: 700, color: isAccepted ? "#2d6a4f" : "#856404" }}>
                                              {isAccepted ? `✓ Switched to ${item.alternative}` : `Use instead: ${item.alternative}`}
                                            </p>
                                            <p style={{ margin: 0, fontSize: 11, color: isAccepted ? "#52b788" : "#856404" }}>{item.alt_reason}</p>
                                          </div>
                                          {!isAccepted && (
                                            <button
                                              onClick={() => acceptSubstitution(id, item.medication, item.alternative)}
                                              style={{
                                                flexShrink: 0, padding: "5px 14px",
                                                background: "#ffc107", color: "#1a1a2e",
                                                border: "none", borderRadius: 6,
                                                fontSize: 12, fontWeight: 700, cursor: "pointer",
                                              }}
                                            >
                                              Switch
                                            </button>
                                          )}
                                        </div>
                                      );
                                    })()}

                                    {!item.is_covered && !item.alternative && (
                                      <div style={{ marginTop: 6, fontSize: 12, color: "#ff6b6b", fontStyle: "italic" }}>
                                        No covered equivalent found in this policy — patient pays out of pocket.
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {!p.has_policy && (
                      <div style={{ marginBottom: 16, padding: "10px 14px", background: "#ffa50218", border: "1px solid #ffa50260", borderRadius: 8, fontSize: 13, color: "#856404" }}>
                        No insurance policy uploaded for this patient. Patient will be billed directly — no insurance claim will be filed.
                      </div>
                    )}

                    {p.has_policy ? (
                      <button
                        onClick={() => navigate(
                          `/hospital/submit-claim?note_id=${note.id}&patient_id=${id}`,
                          { state: { substitutions: acceptedSubs[id] || {} } }
                        )}
                        disabled={note.already_billed}
                        style={{
                          display: "flex", alignItems: "center", gap: 8,
                          padding: "9px 20px",
                          background: note.already_billed ? "#aaa" : "#4ecdc4",
                          color: "#fff", border: "none", borderRadius: 8,
                          fontSize: 13, fontWeight: 600,
                          cursor: note.already_billed ? "not-allowed" : "pointer",
                        }}
                      >
                        <FiClipboard size={14} />
                        {note.already_billed ? "Already Billed" : "Submit Claim to Insurer"}
                      </button>
                    ) : (
                      <button
                        onClick={() => navigate(
                          `/hospital/daily-bill?note_id=${note.id}&patient_id=${id}`
                        )}
                        disabled={note.already_billed}
                        style={{
                          display: "flex", alignItems: "center", gap: 8,
                          padding: "9px 20px",
                          background: note.already_billed ? "#aaa" : "#ffa502",
                          color: "#fff", border: "none", borderRadius: 8,
                          fontSize: 13, fontWeight: 600,
                          cursor: note.already_billed ? "not-allowed" : "pointer",
                        }}
                      >
                        <FiFileText size={14} />
                        {note.already_billed ? "Already Billed" : "Bill Patient Directly"}
                      </button>
                    )}
                  </div>
                )}

                {isOpen && !note && (
                  <div style={{ borderTop: "1px solid #f0f0f0", padding: "16px 24px", background: "#fafafa", color: "#aaa", fontSize: 14 }}>
                    No clinical notes from any doctor yet for this patient.
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
