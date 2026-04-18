import { useState, useEffect } from "react";
import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { FiPlus, FiTrash2, FiSend, FiCheckCircle } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = { background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" };
const input = { width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 8, fontSize: 14, color: "#333", boxSizing: "border-box" };

const ROOM_RATES = { general: 1500, "semi-private": 3000, private: 6000, icu: 12000 };

export default function SubmitClaim() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const substitutions = location.state?.substitutions || {};
  const [patients, setPatients] = useState([]);
  const [notes, setNotes] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedNote, setSelectedNote] = useState(null);
  const [roomType, setRoomType] = useState("general");
  const [roomDays, setRoomDays] = useState(1);
  const [extraCharges, setExtraCharges] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.get("/hospital/patients").then((r) => {
      const list = Array.isArray(r.data) ? r.data : [];
      setPatients(list);

      const prePatientId = searchParams.get("patient_id");
      const preNoteId = searchParams.get("note_id");
      if (prePatientId) {
        const p = list.find((x) => (x.id || x._id) === prePatientId);
        if (p) {
          setSelectedPatient(p);
          loadNotes(prePatientId, preNoteId);
        }
      }
    }).catch(() => toast.error("Failed to load patients"));
  }, []);

  const loadNotes = async (patientId, preSelectNoteId = null) => {
    try {
      const r = await api.get("/hospital/clinical-notes");
      const all = Array.isArray(r.data) ? r.data : [];
      const forPatient = all.filter((n) => n.patient_id === patientId && !n.already_billed);
      setNotes(forPatient);
      if (preSelectNoteId) {
        const n = forPatient.find((x) => (x.id || x._id) === preSelectNoteId) || forPatient[0];
        if (n) setSelectedNote(n);
      }
    } catch {
      toast.error("Failed to load notes");
    }
  };

  const onPatientChange = (patientId) => {
    const p = patients.find((x) => (x.id || x._id) === patientId);
    setSelectedPatient(p || null);
    setSelectedNote(null);
    setNotes([]);
    if (patientId) loadNotes(patientId);
  };

  const addExtraCharge = () => setExtraCharges([...extraCharges, { description: "", amount: 0 }]);
  const removeExtra = (i) => setExtraCharges(extraCharges.filter((_, idx) => idx !== i));
  const updateExtra = (i, field, val) => {
    const copy = [...extraCharges];
    copy[i] = { ...copy[i], [field]: field === "amount" ? parseFloat(val) || 0 : val };
    setExtraCharges(copy);
  };

  const roomCharge = ROOM_RATES[roomType] * roomDays;
  const consultFee = 600;
  const medCost = (selectedNote?.prescriptions || []).length * 150;
  const extraTotal = extraCharges.reduce((s, e) => s + (e.amount || 0), 0);
  const total = consultFee + medCost + roomCharge + extraTotal;

  const handleSubmit = async () => {
    if (!selectedPatient || !selectedNote) return toast.error("Select a patient and note");
    const pid = selectedPatient.id || selectedPatient._id;
    if (!selectedPatient.policy_number && !selectedPatient.policy_id) {
      return toast.error("Patient has no insurance policy linked. Upload one first.");
    }
    setSubmitting(true);
    try {
      const payload = {
        patient_id: pid,
        patient_name: selectedPatient.full_name,
        policy_number: selectedPatient.policy_number || "UNKNOWN",
        insurer_name: selectedPatient.insurer_name || "Unknown Insurer",
        clinical_note_id: selectedNote.id || selectedNote._id,
        diagnosis: selectedNote.diagnosis || "",
        icd_codes: selectedNote.icd_codes || [],
        room_type: roomType,
        room_days: roomDays,
        room_charge_per_day: ROOM_RATES[roomType],
        extra_charges: extraCharges
          .filter((e) => e.description)
          .map((e) => ({ description: e.description, amount: e.amount, category: "extra", icd_code: null })),
        medication_substitutions: Object.entries(substitutions).map(
          ([original, replacement]) => ({ original, replacement })
        ),
      };
      const r = await api.post("/hospital/submit-claim", payload);
      setResult(r.data);
      setSubmitted(true);
      toast.success("Claim submitted to insurer!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted && result) return (
    <div style={{ padding: 32, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
      <div style={{ ...card, padding: 48 }}>
        <FiCheckCircle size={56} color="#4ecdc4" style={{ marginBottom: 16 }} />
        <h2 style={{ color: "#333", margin: "0 0 8px" }}>Claim Submitted!</h2>
        <p style={{ color: "#666", marginBottom: 8 }}>Total amount: <strong>Rs {result.total_amount?.toFixed(2)}</strong></p>
        <p style={{ color: "#aaa", fontSize: 13, marginBottom: 24 }}>Claim ID: {result.claim_id}</p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <button onClick={() => navigate("/hospital/patients")}
            style={{ padding: "10px 24px", background: "#4ecdc4", color: "#fff", border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer" }}>
            Back to Records
          </button>
          <button onClick={() => { setSubmitted(false); setSelectedNote(null); setExtraCharges([]); }}
            style={{ padding: "10px 24px", background: "#eee", color: "#666", border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer" }}>
            Submit Another
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>Submit Insurance Claim</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>Select patient, pick the doctor's note, add billing details</p>

      {/* Step 1 — Patient & Note */}
      <div style={{ ...card, marginBottom: 20 }}>
        <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 16 }}>Patient & Clinical Note</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Patient</label>
            <select value={selectedPatient ? (selectedPatient.id || selectedPatient._id) : ""} onChange={(e) => onPatientChange(e.target.value)} style={{ ...input, background: "#fff" }}>
              <option value="">-- Select patient --</option>
              {patients.map((p) => <option key={p.id || p._id} value={p.id || p._id}>{p.full_name}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Doctor's Note</label>
            <select value={selectedNote ? (selectedNote.id || selectedNote._id) : ""} onChange={(e) => { const n = notes.find((x) => (x.id || x._id) === e.target.value); setSelectedNote(n || null); }} style={{ ...input, background: "#fff" }} disabled={!selectedPatient}>
              <option value="">-- Select note --</option>
              {notes.map((n) => <option key={n.id || n._id} value={n.id || n._id}>{n.diagnosis || "Note"} — {n.doctor_name}</option>)}
            </select>
          </div>
        </div>

        {selectedNote && (
          <div style={{ marginTop: 16, padding: "12px 16px", background: "#f8f9fa", borderRadius: 8, fontSize: 13, color: "#636e72" }}>
            <strong style={{ color: "#2d3436" }}>{selectedNote.diagnosis}</strong> &nbsp;·&nbsp; ICD: {(selectedNote.icd_codes || []).join(", ")} &nbsp;·&nbsp; {(selectedNote.prescriptions || []).length} prescription(s)
          </div>
        )}

        {Object.keys(substitutions).length > 0 && (
          <div style={{ marginTop: 12, padding: "10px 14px", background: "#fff9e6", border: "1px solid #ffc107", borderRadius: 8 }}>
            <p style={{ margin: "0 0 6px", fontSize: 12, fontWeight: 700, color: "#856404" }}>Medication Substitutions Applied</p>
            {Object.entries(substitutions).map(([orig, repl]) => (
              <div key={orig} style={{ fontSize: 12, color: "#856404", display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                <span style={{ textDecoration: "line-through", opacity: 0.6 }}>{orig}</span>
                <span>→</span>
                <strong>{repl}</strong>
                <span style={{ color: "#4ecdc4", fontSize: 11 }}>(covered by policy)</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step 2 — Room & Billing */}
      <div style={{ ...card, marginBottom: 20 }}>
        <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 16 }}>Room & Billing</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
          <div>
            <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Room Type</label>
            <select value={roomType} onChange={(e) => setRoomType(e.target.value)} style={{ ...input, background: "#fff" }}>
              <option value="general">General Ward — Rs 1,500/day</option>
              <option value="semi-private">Semi-Private — Rs 3,000/day</option>
              <option value="private">Private — Rs 6,000/day</option>
              <option value="icu">ICU — Rs 12,000/day</option>
            </select>
          </div>
          <div>
            <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Days Admitted</label>
            <input type="number" min={1} value={roomDays} onChange={(e) => setRoomDays(parseInt(e.target.value) || 1)} style={input} />
          </div>
        </div>

        {/* Extra charges */}
        <div style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <label style={{ color: "#666", fontSize: 13, fontWeight: 600 }}>Extra Charges (optional)</label>
            <button onClick={addExtraCharge} style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 12px", background: "#f0f0f0", color: "#333", border: "none", borderRadius: 6, fontSize: 13, cursor: "pointer" }}>
              <FiPlus size={13} /> Add
            </button>
          </div>
          {extraCharges.map((e, i) => (
            <div key={i} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <input placeholder="Description (e.g. Biomedical waste fee)" value={e.description} onChange={(ev) => updateExtra(i, "description", ev.target.value)} style={{ ...input, flex: 2 }} />
              <input type="number" placeholder="Rs" value={e.amount || ""} onChange={(ev) => updateExtra(i, "amount", ev.target.value)} style={{ ...input, width: 100, flex: "none" }} />
              <button onClick={() => removeExtra(i)} style={{ padding: "0 10px", background: "#ff6b6b18", color: "#ff6b6b", border: "1px solid #ff6b6b40", borderRadius: 6, cursor: "pointer" }}>
                <FiTrash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Bill Summary */}
      <div style={{ ...card, marginBottom: 20 }}>
        <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 16 }}>Bill Summary</h3>
        {[
          ["Consultation Fee", consultFee],
          [`Medications (${(selectedNote?.prescriptions || []).length} items)`, medCost],
          [`Room — ${roomType} × ${roomDays} day(s)`, roomCharge],
          ...extraCharges.filter((e) => e.description).map((e) => [e.description, e.amount]),
        ].map(([label, amt], i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f0f0f0", fontSize: 14, color: "#2d3436" }}>
            <span>{label}</span>
            <span>Rs {Number(amt).toLocaleString()}</span>
          </div>
        ))}
        <div style={{ display: "flex", justifyContent: "space-between", padding: "12px 0 0", fontSize: 16, fontWeight: 700, color: "#2d3436" }}>
          <span>Total</span>
          <span>Rs {total.toLocaleString()}</span>
        </div>
      </div>

      <button onClick={handleSubmit} disabled={submitting || !selectedNote}
        style={{ display: "flex", alignItems: "center", gap: 8, padding: "12px 32px", background: submitting || !selectedNote ? "#aaa" : "#4ecdc4", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: submitting || !selectedNote ? "not-allowed" : "pointer" }}>
        <FiSend size={16} />
        {submitting ? "Submitting..." : "Submit Claim to Insurer"}
      </button>
    </div>
  );
}
