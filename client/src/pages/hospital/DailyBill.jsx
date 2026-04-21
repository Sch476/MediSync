import { useState, useEffect } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import {
  FiPlus, FiTrash2, FiSend, FiCheckCircle, FiXCircle, FiRefreshCw, FiZap,
} from "react-icons/fi";

const CATEGORIES = ["medication", "procedure", "lab", "room", "consultation", "other"];
const CONSULT_FEE = 600;
const MED_UNIT_COST = 150;

function buildItemsFromNote(note) {
  const items = [];

  // Consultation fee
  items.push({
    _uid: Date.now() + Math.random(),
    description: "Doctor Consultation Fee",
    category: "consultation",
    amount: CONSULT_FEE,
    auto: true,
    checking: false, checked: false, is_covered: null, reason: "", alternative: null,
  });

  // One row per prescription
  (note.prescriptions || []).forEach((rx, i) => {
    items.push({
      _uid: Date.now() + i + 1 + Math.random(),
      description: rx.medication || rx.drug || rx.name || "Medication",
      category: "medication",
      amount: MED_UNIT_COST,
      auto: true,
      checking: false, checked: false, is_covered: null, reason: "", alternative: null,
    });
  });

  return items;
}

export default function DailyBill() {
  const [patients, setPatients]       = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [billDate, setBillDate]       = useState(new Date().toISOString().split("T")[0]);
  const [items, setItems]             = useState([]);
  const [form, setForm]               = useState({ description: "", category: "medication", amount: "" });
  const [checkingAll, setCheckingAll] = useState(false);
  const [submitting, setSubmitting]   = useState(false);
  const [submitted, setSubmitted]     = useState(null);

  useEffect(() => {
    api.get("/hospital/patients").then((r) => setPatients(r.data)).catch(() => {});
  }, []);

  // Auto-populate from clinical note when patient changes
  const onPatientChange = (patientId) => {
    const p = patients.find((x) => (x.id || x._id) === patientId) || null;
    setSelectedPatient(p);
    setItems([]);
    if (p?.latest_note) {
      setItems(buildItemsFromNote(p.latest_note));
      toast.success(`Loaded ${(p.latest_note.prescriptions || []).length + 1} items from latest clinical note`);
    }
  };

  const checkedItems  = items.filter((i) => i.checked);
  const insurer_items = checkedItems.filter((i) => i.is_covered);
  const patient_items = checkedItems.filter((i) => !i.is_covered);
  const insurer_total = insurer_items.reduce((s, i) => s + Number(i.amount), 0);
  const patient_total = patient_items.reduce((s, i) => s + Number(i.amount), 0);
  const anyChecking   = items.some((i) => i.checking);
  const allChecked    = items.length > 0 && items.every((i) => i.checked);

  // Check all unchecked items in parallel
  const checkAllCoverage = async () => {
    if (!selectedPatient) return toast.error("Select a patient first");
    const unchecked = items.filter((i) => !i.checked && !i.checking);
    if (unchecked.length === 0) return toast("All items already checked");

    // Mark them all as checking at once
    setCheckingAll(true);
    setItems((prev) =>
      prev.map((i) => (!i.checked && !i.checking ? { ...i, checking: true } : i))
    );

    const patientId = selectedPatient.id || selectedPatient._id;

    await Promise.all(
      unchecked.map(async (item) => {
        try {
          const res = await api.post("/hospital/daily-bill/check-coverage", {
            patient_id: patientId,
            description: item.description,
            category: item.category,
          });
          setItems((prev) =>
            prev.map((i) =>
              i._uid === item._uid
                ? { ...i, checking: false, checked: true, is_covered: res.data.is_covered, reason: res.data.reason, alternative: res.data.alternative }
                : i
            )
          );
        } catch {
          setItems((prev) =>
            prev.map((i) =>
              i._uid === item._uid
                ? { ...i, checking: false, checked: true, is_covered: true, reason: "Coverage check failed — defaulting to covered" }
                : i
            )
          );
        }
      })
    );

    setCheckingAll(false);
  };

  // Add a single extra item (still checks individually)
  const addExtraItem = () => {
    if (!form.description.trim() || !form.amount) return toast.error("Fill in description and amount");
    if (!selectedPatient) return toast.error("Select a patient first");

    setItems((prev) => [
      ...prev,
      {
        _uid: Date.now() + Math.random(),
        description: form.description.trim(),
        category: form.category,
        amount: Number(form.amount),
        auto: false,
        checking: false, checked: false, is_covered: null, reason: "", alternative: null,
      },
    ]);
    setForm((f) => ({ ...f, description: "", amount: "" }));
  };

  const removeItem = (uid) => setItems((prev) => prev.filter((i) => i._uid !== uid));

  const handleSubmit = async () => {
    if (!selectedPatient) return toast.error("Select a patient");
    if (items.length === 0) return toast.error("No items to bill");
    if (anyChecking) return toast.error("Wait for coverage checks to finish");
    if (!allChecked) return toast.error("Run coverage check before submitting");

    setSubmitting(true);
    try {
      const billRes = await api.post("/hospital/daily-bill", {
        patient_id: selectedPatient.id || selectedPatient._id,
        bill_date: billDate,
        items: checkedItems.map((i) => ({
          description: i.description,
          category: i.category,
          amount: i.amount,
          is_covered: i.is_covered,
          coverage_reason: i.reason,
          alternative: i.alternative,
        })),
      });

      const submitRes = await api.post(`/hospital/daily-bill/${billRes.data.id}/submit`);
      setSubmitted(submitRes.data);
      toast.success("Bill saved and covered items sent to insurer!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Success screen ──────────────────────────────────────────────────
  if (submitted) {
    return (
      <div style={{ padding: 32, maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
        <div style={card}>
          <FiCheckCircle size={52} color="#4ecdc4" style={{ marginBottom: 16 }} />
          <h2 style={{ color: "#2d3436", margin: "0 0 20px" }}>Daily Bill Processed</h2>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
            <div style={{ background: "#f0fffe", border: "1px solid #4ecdc440", borderRadius: 10, padding: 16 }}>
              <p style={{ color: "#4ecdc4", fontSize: 11, fontWeight: 700, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: 1 }}>Insurance Claim</p>
              <p style={{ fontSize: 24, fontWeight: 700, color: "#2d3436", margin: 0 }}>₹{submitted.insurer_total?.toLocaleString()}</p>
              <p style={{ color: "#aaa", fontSize: 11, margin: "4px 0 0" }}>Claim ID: ...{submitted.claim_id?.slice(-8)}</p>
            </div>
            <div style={{ background: "#fff5f5", border: "1px solid #ff6b6b40", borderRadius: 10, padding: 16 }}>
              <p style={{ color: "#ff6b6b", fontSize: 11, fontWeight: 700, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: 1 }}>Patient Pays Now</p>
              <p style={{ fontSize: 24, fontWeight: 700, color: "#2d3436", margin: 0 }}>₹{submitted.patient_total?.toLocaleString()}</p>
              <p style={{ color: "#aaa", fontSize: 11, margin: "4px 0 0" }}>Collect at counter</p>
            </div>
          </div>

          {submitted.patient_items?.length > 0 && (
            <div style={{ background: "#fff9f9", border: "1px solid #ffd0d0", borderRadius: 8, padding: 14, marginBottom: 20, textAlign: "left" }}>
              <p style={{ fontSize: 12, fontWeight: 700, color: "#cc0000", margin: "0 0 8px" }}>Collect from patient at counter:</p>
              {submitted.patient_items.map((item, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: "#555", padding: "5px 0", borderBottom: i < submitted.patient_items.length - 1 ? "1px solid #ffe0e0" : "none" }}>
                  <span>{item.description}</span>
                  <strong>₹{Number(item.amount).toLocaleString()}</strong>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => { setSubmitted(null); setItems([]); setSelectedPatient(null); }}
            style={{ padding: "10px 28px", background: "#4ecdc4", color: "#fff", border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer" }}
          >
            New Daily Bill
          </button>
        </div>
      </div>
    );
  }

  // ── Main form ───────────────────────────────────────────────────────
  return (
    <div style={{ padding: 32, maxWidth: 960, margin: "0 auto" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 4, color: "#2d3436" }}>Daily Bill</h1>
      <p style={{ color: "#636e72", fontSize: 15, marginBottom: 28 }}>
        Select a patient — today's items are auto-loaded from their latest clinical note. Add any extras, then run one coverage check to split the bill.
      </p>

      {/* Patient + Date */}
      <div style={{ ...card, marginBottom: 20 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <label style={labelSt}>Patient</label>
            <select
              value={selectedPatient ? (selectedPatient.id || selectedPatient._id) : ""}
              onChange={(e) => onPatientChange(e.target.value)}
              style={{ ...inputSt, background: "#fff" }}
            >
              <option value="">-- Select patient --</option>
              {patients.map((p) => (
                <option key={p.id || p._id} value={p.id || p._id}>{p.full_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={labelSt}>Bill Date</label>
            <input type="date" value={billDate} onChange={(e) => setBillDate(e.target.value)} style={inputSt} />
          </div>
        </div>

        {selectedPatient && (
          <div style={{ marginTop: 12, padding: "8px 12px", background: "#f8f9fa", borderRadius: 8, fontSize: 13, color: "#636e72", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>
              Policy: <strong>{selectedPatient.policy_number || "None"}</strong>
              &nbsp;·&nbsp;
              Insurer: <strong>{selectedPatient.insurer_name || "None"}</strong>
              {!selectedPatient.has_policy && (
                <span style={{ color: "#ffa502", marginLeft: 10 }}>⚠ No policy uploaded — medication checks will default to covered</span>
              )}
            </span>
            {selectedPatient.latest_note && (
              <span style={{ fontSize: 12, color: "#4ecdc4", fontWeight: 600 }}>
                Note: {selectedPatient.latest_note.diagnosis}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Items Table */}
      {items.length > 0 && (
        <div style={{ ...card, padding: 0, overflow: "hidden", marginBottom: 20 }}>
          {/* Table header with Check All button */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 20px", borderBottom: "1px solid #f0f0f0", background: "#fafafa" }}>
            <span style={{ fontSize: 14, fontWeight: 600, color: "#2d3436" }}>
              {items.length} item{items.length !== 1 ? "s" : ""}
              {selectedPatient?.latest_note && (
                <span style={{ fontSize: 12, color: "#aaa", fontWeight: 400, marginLeft: 8 }}>
                  (auto-loaded from clinical note)
                </span>
              )}
            </span>
            {!allChecked && (
              <button
                onClick={checkAllCoverage}
                disabled={anyChecking}
                style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "8px 18px", background: anyChecking ? "#eee" : "#1a1a2e",
                  color: anyChecking ? "#aaa" : "#fff", border: "none",
                  borderRadius: 8, fontWeight: 600, fontSize: 13, cursor: anyChecking ? "not-allowed" : "pointer",
                }}
              >
                <FiZap size={13} />
                {anyChecking ? "Checking coverage..." : "Check All Coverage"}
              </button>
            )}
            {allChecked && (
              <span style={{ fontSize: 13, color: "#2ed573", fontWeight: 600, display: "flex", alignItems: "center", gap: 5 }}>
                <FiCheckCircle size={14} /> All items verified
              </span>
            )}
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8f9fa" }}>
                {["Item", "Category", "Amount", "Coverage", "Paid By", ""].map((h, i) => (
                  <th key={i} style={{ padding: "10px 16px", textAlign: i >= 2 ? "right" : "left", fontSize: 11, fontWeight: 700, color: "#636e72", textTransform: "uppercase", letterSpacing: 0.5 }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr
                  key={item._uid}
                  style={{
                    borderBottom: "1px solid #f5f5f5",
                    background: item.checked
                      ? (item.is_covered ? "rgba(46,213,115,0.04)" : "rgba(255,71,87,0.04)")
                      : "#fff",
                  }}
                >
                  <td style={{ padding: "11px 16px", verticalAlign: "top", maxWidth: 280 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ fontWeight: 500, color: "#2d3436", fontSize: 14 }}>{item.description}</span>
                      {item.auto && (
                        <span style={{ fontSize: 10, background: "#e8f4fd", color: "#4ecdc4", padding: "1px 6px", borderRadius: 4, fontWeight: 600 }}>AUTO</span>
                      )}
                    </div>
                    {item.checked && item.reason && (
                      <div style={{ fontSize: 11, color: "#888", marginTop: 3 }}>{item.reason}</div>
                    )}
                    {item.checked && !item.is_covered && item.alternative && (
                      <div style={{ fontSize: 11, color: "#4ecdc4", marginTop: 4, display: "flex", alignItems: "center", gap: 8 }}>
                        <span>Covered alt: <strong>{item.alternative}</strong></span>
                        <button
                          onClick={() => setItems((prev) => prev.map((it) =>
                            it._uid === item._uid
                              ? { ...it, description: item.alternative, is_covered: true, reason: `Substituted from ${item.description}`, alternative: null, checked: true }
                              : it
                          ))}
                          style={{ padding: "2px 10px", background: "#4ecdc4", color: "#fff", border: "none", borderRadius: 4, fontSize: 10, fontWeight: 700, cursor: "pointer" }}
                        >
                          Switch
                        </button>
                      </div>
                    )}
                  </td>
                  <td style={{ padding: "11px 16px", fontSize: 13, color: "#636e72", verticalAlign: "top" }}>{item.category}</td>
                  <td style={{ padding: "11px 16px", textAlign: "right", fontWeight: 600, fontSize: 14, color: "#2d3436", verticalAlign: "top" }}>
                    ₹{Number(item.amount).toLocaleString()}
                  </td>
                  <td style={{ padding: "11px 16px", textAlign: "right", verticalAlign: "top" }}>
                    {item.checking ? (
                      <span style={{ color: "#aaa", fontSize: 12, display: "inline-flex", alignItems: "center", gap: 4 }}>
                        <FiRefreshCw size={12} /> Checking...
                      </span>
                    ) : item.checked ? (
                      item.is_covered ? (
                        <span style={{ color: "#2ed573", fontSize: 12, display: "inline-flex", alignItems: "center", gap: 4 }}>
                          <FiCheckCircle size={13} /> Covered
                        </span>
                      ) : (
                        <span style={{ color: "#ff4757", fontSize: 12, display: "inline-flex", alignItems: "center", gap: 4 }}>
                          <FiXCircle size={13} /> Not Covered
                        </span>
                      )
                    ) : (
                      <span style={{ fontSize: 11, color: "#ccc" }}>Pending check</span>
                    )}
                  </td>
                  <td style={{ padding: "11px 16px", textAlign: "right", verticalAlign: "top" }}>
                    {item.checked && (
                      <span style={{ fontSize: 12, fontWeight: 700, color: item.is_covered ? "#4ecdc4" : "#ff6b6b" }}>
                        {item.is_covered ? "Insurer" : "Patient"}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: "11px 16px", textAlign: "center", verticalAlign: "top" }}>
                    <button onClick={() => removeItem(item._uid)} style={{ background: "none", border: "none", color: "#ddd", cursor: "pointer", padding: 4 }}>
                      <FiTrash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Extra Item */}
      {selectedPatient && (
        <div style={{ ...card, marginBottom: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, color: "#636e72", margin: "0 0 12px", textTransform: "uppercase", letterSpacing: 0.5 }}>
            Add Extra Item
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 130px auto", gap: 10, alignItems: "end" }}>
            <div>
              <label style={labelSt}>Description</label>
              <input
                placeholder="e.g. Room charges, X-Ray, ECG..."
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                onKeyDown={(e) => e.key === "Enter" && addExtraItem()}
                style={inputSt}
              />
            </div>
            <div>
              <label style={labelSt}>Category</label>
              <select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} style={{ ...inputSt, background: "#fff" }}>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelSt}>Amount (₹)</label>
              <input
                type="number" placeholder="0" value={form.amount}
                onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                onKeyDown={(e) => e.key === "Enter" && addExtraItem()}
                style={inputSt}
              />
            </div>
            <button
              onClick={addExtraItem}
              style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 18px", background: "#f0f0f0", color: "#333", border: "1px solid #ddd", borderRadius: 8, fontWeight: 600, fontSize: 13, cursor: "pointer", whiteSpace: "nowrap" }}
            >
              <FiPlus size={14} /> Add Item
            </button>
          </div>
        </div>
      )}

      {/* Split Summary */}
      {checkedItems.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
          <div style={{ background: "#f0fffe", border: "1px solid #4ecdc440", borderRadius: 12, padding: 20 }}>
            <p style={{ color: "#4ecdc4", fontSize: 11, fontWeight: 700, margin: "0 0 6px", textTransform: "uppercase", letterSpacing: 1 }}>Insurance Pays</p>
            <p style={{ fontSize: 32, fontWeight: 800, color: "#2d3436", margin: 0 }}>₹{insurer_total.toLocaleString()}</p>
            <p style={{ color: "#888", fontSize: 12, margin: "6px 0 0" }}>{insurer_items.length} item(s) — itemized claim sent to insurer</p>
          </div>
          <div style={{ background: "#fff5f5", border: "1px solid #ff6b6b40", borderRadius: 12, padding: 20 }}>
            <p style={{ color: "#ff6b6b", fontSize: 11, fontWeight: 700, margin: "0 0 6px", textTransform: "uppercase", letterSpacing: 1 }}>Patient Pays at Counter</p>
            <p style={{ fontSize: 32, fontWeight: 800, color: "#2d3436", margin: 0 }}>₹{patient_total.toLocaleString()}</p>
            <p style={{ color: "#888", fontSize: 12, margin: "6px 0 0" }}>{patient_items.length} item(s) not covered by policy</p>
          </div>
        </div>
      )}

      {items.length > 0 && (
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <button
            onClick={handleSubmit}
            disabled={submitting || anyChecking || !allChecked}
            style={{
              display: "flex", alignItems: "center", gap: 8, padding: "12px 32px",
              background: (submitting || anyChecking || !allChecked) ? "#aaa" : "#1a1a2e",
              color: "#fff", border: "none", borderRadius: 8, fontSize: 15, fontWeight: 600,
              cursor: (submitting || anyChecking || !allChecked) ? "not-allowed" : "pointer",
            }}
          >
            <FiSend size={16} />
            {submitting ? "Processing..." : !allChecked ? "Run Coverage Check First" : "Save Bill & Submit to Insurer"}
          </button>
          <button
            onClick={() => { setItems([]); toast("Bill cleared"); }}
            style={{
              padding: "12px 24px", background: "#fff", color: "#ff6b6b",
              border: "1px solid #ff6b6b40", borderRadius: 8, fontSize: 14,
              fontWeight: 600, cursor: "pointer",
            }}
          >
            Clear Bill
          </button>
        </div>
      )}
    </div>
  );
}

const card    = { background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" };
const labelSt = { display: "block", fontSize: 11, fontWeight: 700, color: "#636e72", marginBottom: 5, textTransform: "uppercase", letterSpacing: 0.5 };
const inputSt = { width: "100%", padding: "9px 12px", border: "1px solid #ddd", borderRadius: 8, fontSize: 14, outline: "none", boxSizing: "border-box" };
