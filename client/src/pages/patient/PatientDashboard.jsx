import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../utils/api";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import {
  FiFileText,
  FiClipboard,
  FiActivity,
  FiShield,
  FiAlertTriangle,
  FiCheckCircle,
  FiTrendingUp,
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

export default function PatientDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    activeClaims: 0,
    healthStreak: 0,
    lastCheckStatus: null,
  });
  const [lastCheck, setLastCheck] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [claimsRes, checksRes] = await Promise.all([
        api.get("/patient/claims"),
        api.get("/patient/health-checks"),
      ]);

      const claims = claimsRes.data || [];
      const checks = checksRes.data || [];

      const activeClaims = claims.filter(
        (c) => c.status === "pending" || c.status === "flagged"
      ).length;

      let streak = 0;
      if (checks.length > 0) {
        const sorted = [...checks].sort(
          (a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at)
        );
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        for (let i = 0; i < sorted.length; i++) {
          const checkDate = new Date(sorted[i].date || sorted[i].created_at);
          checkDate.setHours(0, 0, 0, 0);
          const expected = new Date(today);
          expected.setDate(expected.getDate() - i);
          if (checkDate.getTime() === expected.getTime()) {
            streak++;
          } else {
            break;
          }
        }
        setLastCheck(sorted[0]);
      }

      const lastStatus = checks.length > 0 ? checks[0] : null;

      setStats({
        activeClaims,
        healthStreak: streak,
        lastCheckStatus: lastStatus?.flagged ? "Flagged" : lastStatus ? "OK" : "N/A",
      });
    } catch (err) {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: "Bill Decoder",
      description: "Upload and decode medical bills",
      icon: <FiFileText size={28} />,
      to: "/patient/bill-decoder",
      color: PRIMARY,
    },
    {
      title: "Discharge Summary",
      description: "Translate discharge summaries",
      icon: <FiClipboard size={28} />,
      to: "/patient/discharge-summary",
      color: "#a55eea",
    },
    {
      title: "Health Check",
      description: "Complete your daily health check",
      icon: <FiActivity size={28} />,
      to: "/patient/health-check",
      color: SUCCESS,
    },
    {
      title: "My Claims",
      description: "Track your insurance claims",
      icon: <FiShield size={28} />,
      to: "/patient/claims",
      color: WARNING,
    },
  ];

  const statCards = [
    {
      label: "Active Claims",
      value: stats.activeClaims,
      icon: <FiShield size={24} />,
      color: PRIMARY,
    },
    {
      label: "Health Check Streak",
      value: `${stats.healthStreak} day${stats.healthStreak !== 1 ? "s" : ""}`,
      icon: <FiTrendingUp size={24} />,
      color: SUCCESS,
    },
    {
      label: "Last Check Status",
      value: stats.lastCheckStatus || "N/A",
      icon:
        stats.lastCheckStatus === "Flagged" ? (
          <FiAlertTriangle size={24} />
        ) : (
          <FiCheckCircle size={24} />
        ),
      color: stats.lastCheckStatus === "Flagged" ? DANGER : SUCCESS,
    },
  ];

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
        <div style={{ fontSize: 18, color: "#666" }}>Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 16px" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        Welcome back, {user?.name || "Patient"}
      </h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 16 }}>
        Here is your health overview for today.
      </p>

      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20, marginBottom: 32 }}>
        {statCards.map((stat) => (
          <div key={stat.label} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: `${stat.color}20`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: stat.color,
              }}
            >
              {stat.icon}
            </div>
            <div>
              <div style={{ fontSize: 13, color: "#636e72", marginBottom: 4 }}>{stat.label}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: "#2d3436" }}>{stat.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Flagged Alert */}
      {lastCheck?.flagged && (
        <div
          style={{
            ...cardStyle,
            background: `${DANGER}10`,
            border: `1px solid ${DANGER}40`,
            marginBottom: 32,
            display: "flex",
            alignItems: "flex-start",
            gap: 16,
          }}
        >
          <FiAlertTriangle size={24} color={DANGER} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ fontWeight: 600, color: DANGER, marginBottom: 8, fontSize: 16 }}>
              Health Check Flagged
            </div>
            {lastCheck.flag_reasons && lastCheck.flag_reasons.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: 20, color: "#2d3436" }}>
                {lastCheck.flag_reasons.map((reason, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>{reason}</li>
                ))}
              </ul>
            ) : (
              <p style={{ margin: 0, color: "#2d3436" }}>
                Your last health check was flagged. Please consult your doctor.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16, color: "#2d3436" }}>Quick Actions</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20 }}>
        {quickActions.map((action) => (
          <Link
            key={action.title}
            to={action.to}
            style={{ textDecoration: "none" }}
          >
            <div
              style={{
                ...cardStyle,
                cursor: "pointer",
                transition: "transform 0.2s, box-shadow 0.2s",
                border: "1px solid transparent",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.12)";
                e.currentTarget.style.borderColor = action.color;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.08)";
                e.currentTarget.style.borderColor = "transparent";
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 12,
                  background: `${action.color}20`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: action.color,
                  marginBottom: 16,
                }}
              >
                {action.icon}
              </div>
              <div style={{ fontWeight: 600, fontSize: 16, color: "#2d3436", marginBottom: 4 }}>
                {action.title}
              </div>
              <div style={{ fontSize: 13, color: "#636e72" }}>{action.description}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
