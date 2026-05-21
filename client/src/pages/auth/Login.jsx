import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.full_name}!`);
      navigate(`/${user.role}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.logo}>⚕ MediSync</h1>
        <p style={styles.subtitle}>AI-Powered Healthcare Middleware</p>

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="doctor@medisync.in" required style={styles.input}
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••" required style={styles.input}
            />
          </div>
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p style={styles.footer}>
          Don't have an account? <Link to="/register" style={styles.link}>Register</Link>
        </p>


        <div style={styles.demo}>
          <p style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>Demo accounts (seeded):</p>
          {[
            { email: "doctor@demo.com", role: "Doctor" },
            { email: "hospital@demo.com", role: "Hospital" },
            { email: "insurer@demo.com", role: "Insurer" },
            { email: "patient@demo.com", role: "Patient 1" },
            { email: "patient2@demo.com", role: "Patient 2" },
          ].map((d) => (
            <button
              key={d.email}
              style={styles.demoBtn}
              onClick={() => { setEmail(d.email); setPassword("password123"); }}
            >
              {d.role}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
    background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
  },
  card: {
    background: "#fff", borderRadius: 16, padding: "40px 36px", width: 400,
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
  },
  logo: { textAlign: "center", fontSize: 28, color: "#1a1a2e", margin: "0 0 4px" },
  subtitle: { textAlign: "center", color: "#888", fontSize: 13, margin: "0 0 30px" },
  field: { marginBottom: 16 },
  label: { display: "block", fontSize: 13, fontWeight: 600, color: "#333", marginBottom: 4 },
  input: {
    width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 8,
    fontSize: 14, outline: "none", boxSizing: "border-box",
  },
  button: {
    width: "100%", padding: 12, background: "#4ecdc4", color: "#fff", border: "none",
    borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: "pointer", marginTop: 8,
  },
  footer: { textAlign: "center", fontSize: 13, color: "#666", marginTop: 20 },
  link: { color: "#4ecdc4", fontWeight: 600 },
  demo: { marginTop: 16, textAlign: "center", borderTop: "1px solid #eee", paddingTop: 16 },
  demoBtn: {
    margin: "0 4px", padding: "4px 12px", background: "#f0f0f0", border: "1px solid #ddd",
    borderRadius: 4, cursor: "pointer", fontSize: 11,
  },
};
