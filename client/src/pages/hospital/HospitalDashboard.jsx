import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FiUsers, FiFileText, FiClipboard, FiUpload, FiActivity } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

const card = { background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" };

export default function HospitalDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ admitted_patients: 0, notes_pending_billing: 0, claims_submitted_today: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/hospital/dashboard-stats")
      .then((r) => setStats(r.data))
      .catch(() => toast.error("Failed to load stats"))
      .finally(() => setLoading(false));
  }, []);

  const statCards = [
    { label: "Admitted Patients", value: stats.admitted_patients, icon: <FiUsers size={28} />, color: "#4ecdc4" },
    { label: "Notes Pending Billing", value: stats.notes_pending_billing, icon: <FiFileText size={28} />, color: "#ffa502" },
    { label: "Claims Submitted Today", value: stats.claims_submitted_today, icon: <FiActivity size={28} />, color: "#2ed573" },
  ];

  const quickActions = [
    { label: "Patient Records", icon: <FiUsers size={18} />, path: "/hospital/patients" },
    { label: "Submit a Claim", icon: <FiClipboard size={18} />, path: "/hospital/submit-claim" },
    { label: "Upload Policy", icon: <FiUpload size={18} />, path: "/hospital/upload-policy" },
  ];

  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 400 }}>
      <p style={{ color: "#666" }}>Loading...</p>
    </div>
  );

  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>
        {user?.hospital_name || "Hospital"} — Admin
      </h1>
      <p style={{ color: "#666", marginBottom: 32, fontSize: 15 }}>Billing & claims management dashboard</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20, marginBottom: 36 }}>
        {statCards.map((s) => (
          <div key={s.label} style={{ ...card, display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 56, height: 56, borderRadius: 12, background: `${s.color}18`, display: "flex", alignItems: "center", justifyContent: "center", color: s.color }}>
              {s.icon}
            </div>
            <div>
              <p style={{ color: "#666", fontSize: 13, margin: 0 }}>{s.label}</p>
              <p style={{ color: "#333", fontSize: 28, fontWeight: 700, margin: 0 }}>{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div style={card}>
        <h2 style={{ color: "#333", fontSize: 18, marginTop: 0, marginBottom: 16 }}>Quick Actions</h2>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {quickActions.map((a) => (
            <button key={a.label} onClick={() => navigate(a.path)}
              style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 20px", background: "#4ecdc4", color: "#fff", border: "none", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" }}>
              {a.icon} {a.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
