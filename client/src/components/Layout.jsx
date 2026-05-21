
import { Link, useLocation, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  FiHome, FiMic, FiFileText, FiUpload, FiClipboard,
  FiActivity, FiBarChart2, FiCheckCircle, FiUser, FiLogOut,
  FiHeart, FiGlobe, FiAlertTriangle, FiUsers, FiDollarSign, FiCalendar,
} from "react-icons/fi";

const navItems = {
  doctor: [
    { path: "/doctor", label: "Dashboard", icon: <FiHome /> },
    { path: "/doctor/consultation", label: "Smart Scribe", icon: <FiMic /> },
    { path: "/doctor/clinical-notes", label: "Clinical Notes", icon: <FiFileText /> },
    { path: "/doctor/alerts", label: "Patient Alerts", icon: <FiAlertTriangle /> },
  ],
  hospital: [
    { path: "/hospital",               label: "Dashboard",       icon: <FiHome /> },
    { path: "/hospital/patients",      label: "Patient Records", icon: <FiUsers /> },
    { path: "/hospital/daily-bill",    label: "Daily Bill",      icon: <FiCalendar /> },
    { path: "/hospital/submit-claim",  label: "Submit Claim",    icon: <FiClipboard /> },
    { path: "/hospital/upload-policy", label: "Upload Policy",   icon: <FiUpload /> },
  ],
  insurer: [
    { path: "/insurer", label: "Dashboard", icon: <FiHome /> },
    { path: "/insurer/claims", label: "Claims", icon: <FiClipboard /> },
    { path: "/insurer/analytics", label: "Analytics", icon: <FiBarChart2 /> },
  ],
  patient: [
    { path: "/patient", label: "Dashboard", icon: <FiHome /> },
    { path: "/patient/upload-policy", label: "My Insurance Policy", icon: <FiUpload /> },
    { path: "/patient/bill-decoder", label: "Bill Decoder", icon: <FiFileText /> },
    { path: "/patient/discharge",    label: "Discharge Summary", icon: <FiGlobe /> },
    { path: "/patient/health-check", label: "Health Check",   icon: <FiHeart /> },
    { path: "/patient/claims",       label: "My Claims",       icon: <FiCheckCircle /> },
    { path: "/patient/payable",      label: "My Payable",      icon: <FiDollarSign /> },
  ],
};

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const items = navItems[user?.role] || [];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f0f2f5" }}>

      <aside style={{
        width: 250, background: "#1a1a2e", color: "#fff",
        padding: "20px 0", display: "flex", flexDirection: "column",
      }}>
        <div style={{ padding: "0 20px 20px", borderBottom: "1px solid #333" }}>
          <h2 style={{ margin: 0, fontSize: 22, color: "#4ecdc4" }}>⚕ MediSync</h2>
          <p style={{ margin: "4px 0 0", fontSize: 12, color: "#888" }}>Healthcare Middleware</p>
        </div>

        <nav style={{ flex: 1, padding: "10px 0" }}>
          {items.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "12px 20px", color: isActive ? "#4ecdc4" : "#ccc",
                  textDecoration: "none", fontSize: 14,
                  background: isActive ? "rgba(78,205,196,0.1)" : "transparent",
                  borderLeft: isActive ? "3px solid #4ecdc4" : "3px solid transparent",
                  transition: "all 0.2s",
                }}
              >
                {item.icon} {item.label}
              </Link>
            );
          })}
        </nav>

        <div style={{ padding: "15px 20px", borderTop: "1px solid #333" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <FiUser size={16} />
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{user?.full_name}</div>
              <div style={{ fontSize: 11, color: "#888", textTransform: "capitalize" }}>{user?.role}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              width: "100%", padding: "8px", background: "rgba(255,107,107,0.2)",
              color: "#ff6b6b", border: "1px solid rgba(255,107,107,0.3)",
              borderRadius: 6, cursor: "pointer", display: "flex",
              alignItems: "center", justifyContent: "center", gap: 6, fontSize: 13,
            }}
          >
            <FiLogOut /> Logout
          </button>
        </div>
      </aside>


      <main style={{ flex: 1, padding: 24, overflow: "auto" }}>
        <Outlet />
      </main>
    </div>
  );
}
