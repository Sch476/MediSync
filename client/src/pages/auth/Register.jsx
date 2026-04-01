import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";

export default function Register() {
  const [form, setForm] = useState({
    email: "", password: "", full_name: "", role: "patient",
    license_number: "", specialization: "", policy_number: "", insurer_name: "",
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await register(form);
      toast.success(`Welcome, ${user.full_name}!`);
      navigate(`/${user.role}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.logo}>⚕ MediSync</h1>
        <p style={styles.subtitle}>Create your account</p>

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Full Name</label>
            <input name="full_name" value={form.full_name} onChange={handleChange} required style={styles.input} />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input name="email" type="email" value={form.email} onChange={handleChange} required style={styles.input} />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input name="password" type="password" value={form.password} onChange={handleChange} required minLength={6} style={styles.input} />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Role</label>
            <select name="role" value={form.role} onChange={handleChange} style={styles.input}>
              <option value="patient">Patient</option>
              <option value="doctor">Doctor</option>
              <option value="insurer">Insurer / TPA</option>
            </select>
          </div>

          {form.role === "doctor" && (
            <>
              <div style={styles.field}>
                <label style={styles.label}>License Number</label>
                <input name="license_number" value={form.license_number} onChange={handleChange} style={styles.input} />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Specialization</label>
                <input name="specialization" value={form.specialization} onChange={handleChange} style={styles.input} />
              </div>
            </>
          )}

          {form.role === "patient" && (
            <>
              <div style={styles.field}>
                <label style={styles.label}>Policy Number</label>
                <input name="policy_number" value={form.policy_number} onChange={handleChange} placeholder="e.g., STD-12345" style={styles.input} />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Insurer Name</label>
                <input name="insurer_name" value={form.insurer_name} onChange={handleChange} placeholder="e.g., Star Health" style={styles.input} />
              </div>
            </>
          )}

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p style={styles.footer}>
          Already have an account? <Link to="/login" style={styles.link}>Sign In</Link>
        </p>
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
    background: "#fff", borderRadius: 16, padding: "36px 36px", width: 420,
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)", maxHeight: "90vh", overflowY: "auto",
  },
  logo: { textAlign: "center", fontSize: 28, color: "#1a1a2e", margin: "0 0 4px" },
  subtitle: { textAlign: "center", color: "#888", fontSize: 13, margin: "0 0 24px" },
  field: { marginBottom: 14 },
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
};
