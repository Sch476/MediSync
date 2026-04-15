import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FiFileText, FiAlertTriangle, FiMic, FiUpload } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function DoctorDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ totalNotes: 0, patientAlerts: 0 });
  const [recentNotes, setRecentNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [notesRes, alertsRes] = await Promise.all([
        api.get("/doctor/clinical-notes"),
        api.get("/doctor/flagged-health-checks"),
      ]);

      const notes = notesRes.data?.notes || notesRes.data || [];
      const alerts = alertsRes.data?.flagged || alertsRes.data || [];

      setStats({
        totalNotes: notes.length,
        patientAlerts: alerts.length,
      });

      setRecentNotes(notes.slice(0, 5));
    } catch (err) {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { label: "Total Notes", value: stats.totalNotes, icon: <FiFileText size={28} />, color: "#4ecdc4" },
    { label: "Patient Alerts", value: stats.patientAlerts, icon: <FiAlertTriangle size={28} />, color: "#ff6b6b" },
  ];

  const quickActions = [
    { label: "New Consultation", icon: <FiMic size={20} />, path: "/doctor/consultation" },
    { label: "Clinical Notes", icon: <FiFileText size={20} />, path: "/doctor/clinical-notes" },
    { label: "Upload Policy", icon: <FiUpload size={20} />, path: "/doctor/upload-policy" },
  ];

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 400 }}>
        <p style={{ color: "#666", fontSize: 16 }}>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: "0 auto" }}>
      <h1 style={{ color: "#333", marginBottom: 4, fontSize: 28 }}>
        Welcome, Dr. {user?.name || "Doctor"}
      </h1>
      <p style={{ color: "#666", marginBottom: 32, fontSize: 15 }}>
        Here is your dashboard overview
      </p>

      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20, marginBottom: 36 }}>
        {statCards.map((s) => (
          <div key={s.label} style={{ ...card, display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: 12,
                background: `${s.color}18`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: s.color,
              }}
            >
              {s.icon}
            </div>
            <div>
              <p style={{ color: "#666", fontSize: 13, margin: 0 }}>{s.label}</p>
              <p style={{ color: "#333", fontSize: 28, fontWeight: 700, margin: 0 }}>{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div style={{ ...card, marginBottom: 36 }}>
        <h2 style={{ color: "#333", fontSize: 18, marginTop: 0, marginBottom: 16 }}>Quick Actions</h2>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {quickActions.map((a) => (
            <button
              key={a.label}
              onClick={() => navigate(a.path)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "10px 20px",
                background: "#4ecdc4",
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {a.icon}
              {a.label}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Clinical Notes */}
      <div style={card}>
        <h2 style={{ color: "#333", fontSize: 18, marginTop: 0, marginBottom: 16 }}>Recent Clinical Notes</h2>
        {recentNotes.length === 0 ? (
          <p style={{ color: "#666", fontSize: 14 }}>No clinical notes yet. Start a consultation to create one.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #eee" }}>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Date</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Patient</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Diagnosis</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentNotes.map((note, i) => (
                <tr
                  key={note._id || note.id || i}
                  style={{ borderBottom: "1px solid #f0f0f0", cursor: "pointer" }}
                  onClick={() => navigate("/doctor/clinical-notes")}
                >
                  <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                    {note.created_at ? new Date(note.created_at).toLocaleDateString() : "N/A"}
                  </td>
                  <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                    {note.patient_name || "Unknown"}
                  </td>
                  <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                    {note.diagnosis || note.structured_note?.diagnosis || "—"}
                  </td>
                  <td style={{ padding: "10px 8px", fontSize: 14 }}>
                    <span
                      style={{
                        padding: "3px 10px",
                        borderRadius: 12,
                        fontSize: 12,
                        fontWeight: 600,
                        background: note.claim_status === "approved" ? "#4ecdc418" : note.claim_status === "pending" ? "#ffa50218" : "#eee",
                        color: note.claim_status === "approved" ? "#4ecdc4" : note.claim_status === "pending" ? "#ffa502" : "#666",
                      }}
                    >
                      {note.claim_status || "draft"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
