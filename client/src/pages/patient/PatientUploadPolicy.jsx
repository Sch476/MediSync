import { useState, useEffect } from "react";
import { FiUpload, FiCheckCircle, FiShield } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function PatientUploadPolicy() {
  const [file, setFile] = useState(null);
  const [insurerName, setInsurerName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [existing, setExisting] = useState(null);

  useEffect(() => {
    api.get("/patient/my-policy")
      .then((res) => { if (res.data.has_policy) setExisting(res.data); })
      .catch(() => {});
  }, []);

  const handleUpload = async () => {
    if (!file) return toast.error("Please select a PDF file");
    if (!insurerName.trim()) return toast.error("Please enter your insurer name");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("insurer_name", insurerName);

    setUploading(true);
    try {
      await api.post("/patient/upload-policy", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Policy uploaded! Your doctor can now check drug coverage automatically.");
      setExisting({ has_policy: true, insurer_name: insurerName, uploaded_at: new Date().toISOString() });
      setFile(null);
      setInsurerName("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ padding: 32, maxWidth: 600, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>My Insurance Policy</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>
        Upload your policy PDF once. Your doctor will automatically see which medicines are covered during your consultation — no manual checks needed.
      </p>


      {existing && (
        <div style={{ ...card, marginBottom: 24, background: "#4ecdc418", border: "1px solid #4ecdc4" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <FiCheckCircle size={24} color="#4ecdc4" />
            <div>
              <p style={{ margin: 0, fontWeight: 600, color: "#2d3436" }}>Policy linked — {existing.insurer_name}</p>
              <p style={{ margin: "4px 0 0", fontSize: 13, color: "#636e72" }}>
                Uploaded {existing.uploaded_at ? new Date(existing.uploaded_at).toLocaleDateString() : "recently"} · Your doctor sees coverage warnings automatically
              </p>
            </div>
          </div>
        </div>
      )}


      <div style={card}>
        <h3 style={{ color: "#333", fontSize: 16, marginTop: 0, marginBottom: 20 }}>
          {existing ? "Update Policy" : "Upload Policy PDF"}
        </h3>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>
            Insurance Company Name
          </label>
          <input
            type="text"
            placeholder="e.g. Star Health, HDFC Ergo, ICICI Lombard"
            value={insurerName}
            onChange={(e) => setInsurerName(e.target.value)}
            style={{
              width: "100%", padding: "10px 12px", border: "1px solid #ddd",
              borderRadius: 8, fontSize: 14, color: "#333", boxSizing: "border-box",
            }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: "block", color: "#666", fontSize: 13, marginBottom: 6, fontWeight: 600 }}>
            Policy PDF
          </label>
          <label
            style={{
              display: "flex", alignItems: "center", justifyContent: "center",
              flexDirection: "column", gap: 8, padding: 32,
              border: "2px dashed #ddd", borderRadius: 8, cursor: "pointer",
              background: file ? "#4ecdc408" : "#fafafa",
              borderColor: file ? "#4ecdc4" : "#ddd",
            }}
          >
            <FiUpload size={28} color={file ? "#4ecdc4" : "#aaa"} />
            <span style={{ fontSize: 14, color: file ? "#4ecdc4" : "#666" }}>
              {file ? file.name : "Click to select PDF"}
            </span>
            <input
              type="file"
              accept="application/pdf"
              style={{ display: "none" }}
              onChange={(e) => setFile(e.target.files[0] || null)}
            />
          </label>
        </div>

        <button
          onClick={handleUpload}
          disabled={uploading}
          style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "11px 28px", background: uploading ? "#aaa" : "#4ecdc4",
            color: "#fff", border: "none", borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: uploading ? "not-allowed" : "pointer",
          }}
        >
          <FiShield size={16} />
          {uploading ? "Uploading..." : existing ? "Update Policy" : "Upload Policy"}
        </button>
      </div>
    </div>
  );
}
