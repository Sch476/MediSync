import { useState, useEffect } from "react";
import { FiUpload, FiShield } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = { background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" };
const input = { width: "100%", padding: "10px 12px", border: "1px solid #ddd", borderRadius: 8, fontSize: 14, color: "#333", boxSizing: "border-box" };

export default function HospitalUploadPolicy() {
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState("");
  const [insurerName, setInsurerName] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    api.get("/hospital/patients")
      .then((r) => setPatients(Array.isArray(r.data) ? r.data : []))
      .catch(() => toast.error("Failed to load patients"));
  }, []);

  const handleUpload = async () => {
    if (!selectedPatientId) return toast.error("Select a patient");
    if (!insurerName.trim()) return toast.error("Enter insurer name");
    if (!file) return toast.error("Select a PDF file");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("patient_id", selectedPatientId);
    formData.append("insurer_name", insurerName);

    setUploading(true);
    try {
      const r = await api.post("/hospital/upload-policy", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(r.data.message);
      setFile(null);
      setInsurerName("");
      setSelectedPatientId("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ padding: 32, maxWidth: 600, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>Upload Patient Policy</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>
        Hospital reception uploads the patient's insurance PDF at the time of admission.
        The doctor will automatically see coverage warnings during consultation.
      </p>

      <div style={card}>
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Patient</label>
          <select value={selectedPatientId} onChange={(e) => setSelectedPatientId(e.target.value)} style={{ ...input, background: "#fff" }}>
            <option value="">-- Select patient --</option>
            {patients.map((p) => (
              <option key={p.id || p._id} value={p.id || p._id}>
                {p.full_name} {p.has_policy ? "✓ Policy exists" : ""}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Insurance Company</label>
          <input type="text" placeholder="e.g. Star Health, HDFC Ergo, ICICI Lombard" value={insurerName} onChange={(e) => setInsurerName(e.target.value)} style={input} />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>Policy PDF</label>
          <label style={{
            display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 8,
            padding: 32, border: "2px dashed #ddd", borderRadius: 8, cursor: "pointer",
            background: file ? "#4ecdc408" : "#fafafa", borderColor: file ? "#4ecdc4" : "#ddd",
          }}>
            <FiUpload size={28} color={file ? "#4ecdc4" : "#aaa"} />
            <span style={{ fontSize: 14, color: file ? "#4ecdc4" : "#666" }}>{file ? file.name : "Click to select PDF"}</span>
            <input type="file" accept="application/pdf" style={{ display: "none" }} onChange={(e) => setFile(e.target.files[0] || null)} />
          </label>
        </div>

        <button onClick={handleUpload} disabled={uploading}
          style={{ display: "flex", alignItems: "center", gap: 8, padding: "11px 28px", background: uploading ? "#aaa" : "#4ecdc4", color: "#fff", border: "none", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: uploading ? "not-allowed" : "pointer" }}>
          <FiShield size={16} />
          {uploading ? "Uploading..." : "Upload Policy"}
        </button>
      </div>
    </div>
  );
}
