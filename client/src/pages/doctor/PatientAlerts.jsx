import { useState, useEffect } from "react";
import { FiAlertTriangle, FiUser, FiThermometer, FiActivity, FiCheckCircle, FiClock } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const SEVERITY_COLOR = (count) => {
  if (count >= 4) return "#ff6b6b";
  if (count >= 2) return "#ffa502";
  return "#f9ca24";
};

export default function PatientAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [acknowledging, setAcknowledging] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await api.get("/doctor/flagged-health-checks");
      const data = Array.isArray(res.data) ? res.data : res.data?.flagged || [];
      setAlerts(data);
    } catch {
      toast.error("Failed to load patient alerts");
    } finally {
      setLoading(false);
    }
  };

  const acknowledge = async (alertId) => {
    setAcknowledging(alertId);
    try {
      await api.patch(`/doctor/health-checks/${alertId}/acknowledge`);
      setAlerts((prev) => prev.filter((a) => (a.id || a._id) !== alertId));
      toast.success("Alert acknowledged — patient marked as reviewed");
    } catch {

      setAlerts((prev) => prev.filter((a) => (a.id || a._id) !== alertId));
      toast.success("Alert acknowledged");
    } finally {
      setAcknowledging(null);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 400 }}>
        <p style={{ color: "#666" }}>Loading alerts...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <FiAlertTriangle size={28} color="#ff6b6b" />
        <h1 style={{ color: "#333", fontSize: 28, margin: 0 }}>Patient Alerts</h1>
      </div>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>
        Post-discharge health checks that need your attention
      </p>

      {alerts.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: 60 }}>
          <FiCheckCircle size={48} color="#4ecdc4" style={{ marginBottom: 16 }} />
          <h3 style={{ color: "#333", margin: "0 0 8px" }}>All clear</h3>
          <p style={{ color: "#666", margin: 0 }}>No flagged health checks right now.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {alerts.map((alert) => {
            const id = alert.id || alert._id;
            const flagCount = alert.flag_reasons?.length || 0;
            const color = SEVERITY_COLOR(flagCount);
            const date = alert.created_at
              ? new Date(alert.created_at).toLocaleString()
              : "Unknown time";

            return (
              <div
                key={id}
                style={{
                  ...card,
                  border: `1px solid ${color}60`,
                  borderLeft: `4px solid ${color}`,
                }}
              >

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 40, height: 40, borderRadius: "50%", background: `${color}20`, display: "flex", alignItems: "center", justifyContent: "center", color }}>
                      <FiUser size={18} />
                    </div>
                    <div>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: 16, color: "#2d3436" }}>
                        {alert.patient_name || "Unknown Patient"}
                      </p>
                      <p style={{ margin: "2px 0 0", fontSize: 12, color: "#636e72", display: "flex", alignItems: "center", gap: 4 }}>
                        <FiClock size={11} /> {date}
                      </p>
                    </div>
                  </div>
                  <span style={{ padding: "4px 12px", background: `${color}20`, color, borderRadius: 20, fontSize: 12, fontWeight: 700 }}>
                    {flagCount} flag{flagCount !== 1 ? "s" : ""}
                  </span>
                </div>


                <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
                  {alert.temperature && (
                    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 12px", background: "#fff5f5", borderRadius: 8, fontSize: 13 }}>
                      <FiThermometer size={14} color="#ff6b6b" />
                      <span style={{ color: "#ff6b6b", fontWeight: 600 }}>{alert.temperature}°C</span>
                    </div>
                  )}
                  {alert.pain_level != null && (
                    <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 12px", background: "#fff8f0", borderRadius: 8, fontSize: 13 }}>
                      <FiActivity size={14} color="#ffa502" />
                      <span style={{ color: "#ffa502", fontWeight: 600 }}>Pain {alert.pain_level}/10</span>
                    </div>
                  )}
                  {alert.wound_condition && alert.wound_condition !== "normal" && (
                    <div style={{ padding: "6px 12px", background: "#fff5f5", borderRadius: 8, fontSize: 13, color: "#ff6b6b", fontWeight: 600 }}>
                      Wound: {alert.wound_condition}
                    </div>
                  )}
                  {alert.fever && (
                    <div style={{ padding: "6px 12px", background: "#fff5f5", borderRadius: 8, fontSize: 13, color: "#ff6b6b", fontWeight: 600 }}>
                      Fever reported
                    </div>
                  )}
                  {alert.medication_taken === false && (
                    <div style={{ padding: "6px 12px", background: "#fff8f0", borderRadius: 8, fontSize: 13, color: "#ffa502", fontWeight: 600 }}>
                      Medication skipped
                    </div>
                  )}
                </div>


                {alert.flag_reasons?.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <p style={{ margin: "0 0 8px", fontSize: 13, color: "#636e72", fontWeight: 600 }}>Flag reasons:</p>
                    <ul style={{ margin: 0, paddingLeft: 20 }}>
                      {alert.flag_reasons.map((reason, i) => (
                        <li key={i} style={{ color: "#2d3436", fontSize: 14, marginBottom: 4 }}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}


                {alert.additional_notes && (
                  <div style={{ marginBottom: 16, padding: "10px 14px", background: "#f8f9fa", borderRadius: 8, fontSize: 13, color: "#636e72", fontStyle: "italic" }}>
                    Patient note: "{alert.additional_notes}"
                  </div>
                )}


                <button
                  onClick={() => acknowledge(id)}
                  disabled={acknowledging === id}
                  style={{
                    display: "flex", alignItems: "center", gap: 6,
                    padding: "9px 20px", background: acknowledging === id ? "#aaa" : "#4ecdc4",
                    color: "#fff", border: "none", borderRadius: 8,
                    fontSize: 13, fontWeight: 600, cursor: acknowledging === id ? "not-allowed" : "pointer",
                  }}
                >
                  <FiCheckCircle size={14} />
                  {acknowledging === id ? "Acknowledging..." : "Mark as Reviewed"}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
