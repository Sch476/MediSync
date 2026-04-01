import { useState, useEffect } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import {
  FiCheckCircle,
  FiAlertTriangle,
  FiSend,
  FiThermometer,
  FiClock,
} from "react-icons/fi";

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const PRIMARY = "#4ecdc4";
const DANGER = "#ff6b6b";
const WARNING = "#ffa502";
const SUCCESS = "#2ed573";

const WOUND_OPTIONS = ["normal", "red", "swollen", "discharge", "bleeding"];
const APPETITE_OPTIONS = ["normal", "reduced", "none"];
const MOBILITY_OPTIONS = ["normal", "limited", "bedridden"];

export default function HealthCheck() {
  const [form, setForm] = useState({
    wound_condition: "normal",
    fever: false,
    temperature: "",
    pain_level: 0,
    appetite: "normal",
    mobility: "normal",
    medication_taken: false,
    additional_notes: "",
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get("/patient/health-checks");
      setHistory(res.data || []);
    } catch (err) {
      toast.error("Failed to load health check history");
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const payload = {
        wound_condition: form.wound_condition,
        fever: form.fever,
        pain_level: Number(form.pain_level),
        appetite: form.appetite,
        mobility: form.mobility,
        medication_taken: form.medication_taken,
        additional_notes: form.additional_notes,
      };
      if (form.fever && form.temperature) {
        payload.temperature = Number(form.temperature);
      }
      const res = await api.post("/patient/health-check", payload);
      setResult(res.data);
      if (res.data.flagged) {
        toast.error("Health check flagged - please review the alerts");
      } else {
        toast.success("Health check submitted successfully!");
      }
      fetchHistory();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit health check");
    } finally {
      setLoading(false);
    }
  };

  const radioGroupStyle = {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 8,
  };

  const radioLabelStyle = (selected) => ({
    padding: "8px 16px",
    borderRadius: 8,
    border: `1px solid ${selected ? PRIMARY : "#dfe6e9"}`,
    background: selected ? `${PRIMARY}15` : "#fff",
    color: selected ? PRIMARY : "#2d3436",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: selected ? 600 : 400,
    transition: "all 0.2s",
    textTransform: "capitalize",
  });

  const labelStyle = { fontWeight: 600, color: "#2d3436", marginBottom: 4, display: "block" };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "32px 16px" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        Daily Health Check
      </h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 16 }}>
        Complete your daily health assessment. This helps us monitor your recovery.
      </p>

      {/* Result Alert */}
      {result && (
        <div
          style={{
            ...cardStyle,
            marginBottom: 24,
            background: result.flagged ? `${DANGER}10` : `${SUCCESS}10`,
            border: `1px solid ${result.flagged ? `${DANGER}40` : `${SUCCESS}40`}`,
            display: "flex",
            alignItems: "flex-start",
            gap: 16,
          }}
        >
          {result.flagged ? (
            <FiAlertTriangle size={24} color={DANGER} style={{ flexShrink: 0, marginTop: 2 }} />
          ) : (
            <FiCheckCircle size={24} color={SUCCESS} style={{ flexShrink: 0, marginTop: 2 }} />
          )}
          <div>
            <div
              style={{
                fontWeight: 600,
                color: result.flagged ? DANGER : SUCCESS,
                marginBottom: 8,
                fontSize: 16,
              }}
            >
              {result.flagged ? "Health Check Flagged" : "All Clear!"}
            </div>
            {result.flagged && result.flag_reasons?.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: 20, color: "#2d3436" }}>
                {result.flag_reasons.map((reason, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>{reason}</li>
                ))}
              </ul>
            ) : !result.flagged ? (
              <p style={{ margin: 0, color: "#2d3436" }}>
                Your health check looks good. Keep up the good work!
              </p>
            ) : null}
          </div>
        </div>
      )}

      {/* Health Check Form */}
      <form onSubmit={handleSubmit}>
        <div style={{ ...cardStyle, marginBottom: 24, display: "flex", flexDirection: "column", gap: 24 }}>
          {/* Wound Condition */}
          <div>
            <label style={labelStyle}>Wound Condition</label>
            <div style={radioGroupStyle}>
              {WOUND_OPTIONS.map((opt) => (
                <label key={opt} style={radioLabelStyle(form.wound_condition === opt)}>
                  <input
                    type="radio"
                    name="wound_condition"
                    value={opt}
                    checked={form.wound_condition === opt}
                    onChange={(e) => setForm({ ...form, wound_condition: e.target.value })}
                    style={{ display: "none" }}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>

          {/* Fever */}
          <div>
            <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: 10 }}>
              <input
                type="checkbox"
                checked={form.fever}
                onChange={(e) => setForm({ ...form, fever: e.target.checked, temperature: "" })}
                style={{ width: 18, height: 18, accentColor: PRIMARY }}
              />
              Fever
            </label>
            {form.fever && (
              <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
                <FiThermometer size={18} color={WARNING} />
                <input
                  type="number"
                  step="0.1"
                  min="35"
                  max="43"
                  placeholder="Temperature in Celsius"
                  value={form.temperature}
                  onChange={(e) => setForm({ ...form, temperature: e.target.value })}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 8,
                    border: "1px solid #dfe6e9",
                    fontSize: 15,
                    width: 200,
                    outline: "none",
                  }}
                />
                <span style={{ color: "#636e72", fontSize: 14 }}>°C</span>
              </div>
            )}
          </div>

          {/* Pain Level */}
          <div>
            <label style={labelStyle}>
              Pain Level: <span style={{ color: PRIMARY, fontSize: 18 }}>{form.pain_level}</span>
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 8 }}>
              <span style={{ fontSize: 13, color: "#636e72" }}>0</span>
              <input
                type="range"
                min="0"
                max="10"
                value={form.pain_level}
                onChange={(e) => setForm({ ...form, pain_level: e.target.value })}
                style={{ flex: 1, accentColor: PRIMARY }}
              />
              <span style={{ fontSize: 13, color: "#636e72" }}>10</span>
            </div>
          </div>

          {/* Appetite */}
          <div>
            <label style={labelStyle}>Appetite</label>
            <div style={radioGroupStyle}>
              {APPETITE_OPTIONS.map((opt) => (
                <label key={opt} style={radioLabelStyle(form.appetite === opt)}>
                  <input
                    type="radio"
                    name="appetite"
                    value={opt}
                    checked={form.appetite === opt}
                    onChange={(e) => setForm({ ...form, appetite: e.target.value })}
                    style={{ display: "none" }}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>

          {/* Mobility */}
          <div>
            <label style={labelStyle}>Mobility</label>
            <div style={radioGroupStyle}>
              {MOBILITY_OPTIONS.map((opt) => (
                <label key={opt} style={radioLabelStyle(form.mobility === opt)}>
                  <input
                    type="radio"
                    name="mobility"
                    value={opt}
                    checked={form.mobility === opt}
                    onChange={(e) => setForm({ ...form, mobility: e.target.value })}
                    style={{ display: "none" }}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>

          {/* Medication Taken */}
          <div>
            <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: 10 }}>
              <input
                type="checkbox"
                checked={form.medication_taken}
                onChange={(e) => setForm({ ...form, medication_taken: e.target.checked })}
                style={{ width: 18, height: 18, accentColor: PRIMARY }}
              />
              Medication Taken
            </label>
          </div>

          {/* Additional Notes */}
          <div>
            <label style={labelStyle}>Additional Notes</label>
            <textarea
              value={form.additional_notes}
              onChange={(e) => setForm({ ...form, additional_notes: e.target.value })}
              placeholder="Any additional symptoms or observations..."
              rows={3}
              style={{
                width: "100%",
                padding: 12,
                borderRadius: 8,
                border: "1px solid #dfe6e9",
                fontSize: 15,
                fontFamily: "inherit",
                resize: "vertical",
                boxSizing: "border-box",
                outline: "none",
                marginTop: 8,
              }}
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
              background: loading ? "#b2bec3" : PRIMARY,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "14px 24px",
              fontSize: 16,
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "background 0.2s",
              width: "100%",
            }}
          >
            <FiSend size={16} />
            {loading ? "Submitting..." : "Submit Health Check"}
          </button>
        </div>
      </form>

      {/* Health Check History */}
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16, color: "#2d3436" }}>
        <FiClock style={{ verticalAlign: "middle", marginRight: 8 }} />
        Health Check History
      </h2>
      {historyLoading ? (
        <p style={{ color: "#636e72" }}>Loading history...</p>
      ) : history.length === 0 ? (
        <div style={{ ...cardStyle, textAlign: "center", color: "#636e72" }}>
          No health checks recorded yet. Submit your first check above!
        </div>
      ) : (
        <div style={{ position: "relative", paddingLeft: 24 }}>
          {/* Timeline line */}
          <div
            style={{
              position: "absolute",
              left: 7,
              top: 8,
              bottom: 8,
              width: 2,
              background: "#dfe6e9",
            }}
          />
          {history.map((check, idx) => {
            const date = new Date(check.date || check.created_at);
            const isFlagged = check.flagged;
            return (
              <div key={idx} style={{ position: "relative", marginBottom: 16 }}>
                {/* Timeline dot */}
                <div
                  style={{
                    position: "absolute",
                    left: -20,
                    top: 24,
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    background: isFlagged ? DANGER : SUCCESS,
                    border: "2px solid #fff",
                    boxShadow: "0 0 0 2px " + (isFlagged ? DANGER : SUCCESS),
                  }}
                />
                <div
                  style={{
                    ...cardStyle,
                    borderLeft: `3px solid ${isFlagged ? DANGER : SUCCESS}`,
                    marginLeft: 8,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: 8,
                      flexWrap: "wrap",
                      gap: 8,
                    }}
                  >
                    <span style={{ fontSize: 14, color: "#636e72" }}>
                      {date.toLocaleDateString("en-US", {
                        weekday: "short",
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </span>
                    <span
                      style={{
                        padding: "4px 12px",
                        borderRadius: 20,
                        fontSize: 12,
                        fontWeight: 600,
                        background: isFlagged ? `${DANGER}20` : `${SUCCESS}20`,
                        color: isFlagged ? DANGER : SUCCESS,
                      }}
                    >
                      {isFlagged ? "Flagged" : "OK"}
                    </span>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: 12,
                      fontSize: 13,
                      color: "#2d3436",
                    }}
                  >
                    <span>Wound: <strong>{check.wound_condition || "--"}</strong></span>
                    <span>Pain: <strong>{check.pain_level ?? "--"}/10</strong></span>
                    <span>Appetite: <strong>{check.appetite || "--"}</strong></span>
                    <span>Mobility: <strong>{check.mobility || "--"}</strong></span>
                    {check.fever && <span style={{ color: WARNING }}>Fever{check.temperature ? `: ${check.temperature}°C` : ""}</span>}
                  </div>
                  {isFlagged && check.flag_reasons?.length > 0 && (
                    <div style={{ marginTop: 8, fontSize: 13, color: DANGER }}>
                      {check.flag_reasons.join(" | ")}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
