import { useState, useEffect } from "react";
import api from "../../utils/api";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";
import { FiFileText, FiClock, FiCheckCircle, FiXCircle, FiZap } from "react-icons/fi";

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function InsurerDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adjudicating, setAdjudicating] = useState(false);
  const [batchResult, setBatchResult] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get("/insurer/analytics");
      setStats(res.data);
    } catch (err) {
      toast.error("Failed to load dashboard stats");
    } finally {
      setLoading(false);
    }
  };

  const handleAutoAdjudicateAll = async () => {
    setAdjudicating(true);
    setBatchResult(null);
    try {
      const res = await api.post("/insurer/adjudicate-all-pending");
      setBatchResult(res.data);
      toast.success("Batch adjudication complete");
      fetchStats();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Batch adjudication failed");
    } finally {
      setAdjudicating(false);
    }
  };

  const statCards = stats
    ? [
        { label: "Total Claims", value: stats.total_claims ?? 0, icon: <FiFileText size={28} />, color: "#4ecdc4" },
        { label: "Pending", value: stats.pending ?? 0, icon: <FiClock size={28} />, color: "#ffa502" },
        { label: "Adjudicated", value: stats.adjudicated ?? 0, icon: <FiFileText size={28} />, color: "#3742fa" },
        { label: "Approved", value: stats.approved ?? 0, icon: <FiCheckCircle size={28} />, color: "#2ed573" },
        { label: "Rejected", value: stats.rejected ?? 0, icon: <FiXCircle size={28} />, color: "#ff6b6b" },
      ]
    : [];

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
        <p style={{ fontSize: 18, color: "#888" }}>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: "0 auto" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        Welcome back, {user?.name || "Insurer"}
      </h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 15 }}>
        Here is an overview of your claims dashboard.
      </p>


      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20, marginBottom: 32 }}>
        {statCards.map((card) => (
          <div key={card.label} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: 12,
                background: card.color + "18",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: card.color,
              }}
            >
              {card.icon}
            </div>
            <div>
              <p style={{ fontSize: 13, color: "#636e72", margin: 0 }}>{card.label}</p>
              <p style={{ fontSize: 28, fontWeight: 700, margin: 0, color: "#2d3436" }}>{card.value}</p>
            </div>
          </div>
        ))}
      </div>


      <div style={{ ...cardStyle, marginBottom: 32 }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 12, color: "#2d3436" }}>Quick Actions</h2>
        <p style={{ color: "#636e72", marginBottom: 16, fontSize: 14 }}>
          Run AI-powered auto-adjudication on all pending claims at once.
        </p>
        <button
          onClick={handleAutoAdjudicateAll}
          disabled={adjudicating}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "12px 24px",
            background: adjudicating ? "#b2bec3" : "#4ecdc4",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 15,
            fontWeight: 600,
            cursor: adjudicating ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
        >
          <FiZap size={18} />
          {adjudicating ? "Processing..." : "Auto-Adjudicate All Pending"}
        </button>
      </div>


      {batchResult && (
        <div style={{ ...cardStyle }}>
          <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16, color: "#2d3436" }}>
            Batch Adjudication Results
          </h2>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            <div style={{ padding: "12px 20px", borderRadius: 8, background: "#3742fa18", color: "#3742fa", fontWeight: 600 }}>
              {batchResult.adjudicated ?? 0} Adjudicated (awaiting your decision)
            </div>
            <div style={{ padding: "12px 20px", borderRadius: 8, background: "#ff634818", color: "#ff6348", fontWeight: 600 }}>
              {batchResult.flagged ?? 0} Flagged (manual review)
            </div>
          </div>
          <p style={{ marginTop: 12, fontSize: 13, color: "#636e72" }}>
            Go to the Claims page and use the checkboxes to batch-approve or batch-reject adjudicated claims.
          </p>
        </div>
      )}
    </div>
  );
}
