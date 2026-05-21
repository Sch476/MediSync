import { useState, useEffect, useRef } from "react";
import { FiUpload, FiFile, FiCheckCircle, FiTrash2 } from "react-icons/fi";
import toast from "react-hot-toast";
import api from "../../utils/api";

const card = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export default function UploadPolicy() {
  const [policyId, setPolicyId] = useState("");
  const [insurerName, setInsurerName] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [loadingPolicies, setLoadingPolicies] = useState(true);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const res = await api.get("/doctor/policies");
      setPolicies(res.data?.policies || res.data || []);
    } catch {

    } finally {
      setLoadingPolicies(false);
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type !== "application/pdf") {
      toast.error("Please select a PDF file");
      return;
    }
    setFile(selected || null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!policyId.trim()) {
      toast.error("Please enter a Policy ID");
      return;
    }
    if (!insurerName.trim()) {
      toast.error("Please enter an Insurer Name");
      return;
    }
    if (!file) {
      toast.error("Please select a PDF file");
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append("policy_id", policyId.trim());
      formData.append("insurer_name", insurerName.trim());
      formData.append("file", file);

      const res = await api.post("/doctor/upload-policy", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploadResult(res.data);
      toast.success("Policy uploaded successfully");


      setPolicyId("");
      setInsurerName("");
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";


      fetchPolicies();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to upload policy");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: "0 auto" }}>
      <h1 style={{ color: "#333", fontSize: 28, marginBottom: 4 }}>Upload Policy</h1>
      <p style={{ color: "#666", fontSize: 15, marginBottom: 32 }}>
        Upload insurance policy PDFs for AI-powered claim validation
      </p>


      <div style={{ ...card, marginBottom: 24 }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", color: "#666", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              Policy ID *
            </label>
            <input
              type="text"
              value={policyId}
              onChange={(e) => setPolicyId(e.target.value)}
              placeholder="e.g., POL-2026-001"
              style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #ddd",
                borderRadius: 8,
                fontSize: 14,
                color: "#333",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", color: "#666", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              Insurer Name *
            </label>
            <input
              type="text"
              value={insurerName}
              onChange={(e) => setInsurerName(e.target.value)}
              placeholder="e.g., Star Health Insurance"
              style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #ddd",
                borderRadius: 8,
                fontSize: 14,
                color: "#333",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", color: "#666", fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              Policy PDF *
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: "2px dashed #ddd",
                borderRadius: 8,
                padding: "32px 16px",
                textAlign: "center",
                cursor: "pointer",
                background: file ? "#4ecdc408" : "#fafafa",
                transition: "border-color 0.2s",
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
              {file ? (
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                  <FiFile size={20} style={{ color: "#4ecdc4" }} />
                  <span style={{ color: "#333", fontSize: 14 }}>{file.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "#ff6b6b", padding: 4 }}
                  >
                    <FiTrash2 size={16} />
                  </button>
                </div>
              ) : (
                <>
                  <FiUpload size={28} style={{ color: "#999", marginBottom: 8 }} />
                  <p style={{ color: "#666", fontSize: 14, margin: 0 }}>Click to select a PDF file</p>
                  <p style={{ color: "#999", fontSize: 12, margin: "4px 0 0" }}>Only PDF files are accepted</p>
                </>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 28px",
              background: uploading ? "#999" : "#4ecdc4",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 600,
              cursor: uploading ? "not-allowed" : "pointer",
            }}
          >
            <FiUpload size={16} />
            {uploading ? "Uploading..." : "Upload Policy"}
          </button>
        </form>
      </div>


      {uploadResult && (
        <div
          style={{
            ...card,
            marginBottom: 24,
            border: "1px solid #4ecdc4",
            background: "#4ecdc408",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <FiCheckCircle size={20} style={{ color: "#4ecdc4" }} />
            <h3 style={{ color: "#333", fontSize: 16, margin: 0 }}>Upload Successful</h3>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {uploadResult.pages_extracted != null && (
              <p style={{ color: "#666", fontSize: 14, margin: 0 }}>
                Pages extracted: <strong style={{ color: "#333" }}>{uploadResult.pages_extracted}</strong>
              </p>
            )}
            {uploadResult.chunks_indexed != null && (
              <p style={{ color: "#666", fontSize: 14, margin: 0 }}>
                Chunks indexed: <strong style={{ color: "#333" }}>{uploadResult.chunks_indexed}</strong>
              </p>
            )}
            {uploadResult.policy_id && (
              <p style={{ color: "#666", fontSize: 14, margin: 0 }}>
                Policy ID: <strong style={{ color: "#333" }}>{uploadResult.policy_id}</strong>
              </p>
            )}
            {uploadResult.message && (
              <p style={{ color: "#666", fontSize: 14, margin: 0, gridColumn: "1 / -1" }}>
                {uploadResult.message}
              </p>
            )}
          </div>
        </div>
      )}


      <div style={card}>
        <h2 style={{ color: "#333", fontSize: 18, marginTop: 0, marginBottom: 16 }}>Uploaded Policies</h2>
        {loadingPolicies ? (
          <p style={{ color: "#666", fontSize: 14 }}>Loading...</p>
        ) : policies.length === 0 ? (
          <p style={{ color: "#666", fontSize: 14 }}>No policies uploaded yet.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #eee" }}>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Policy ID</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Insurer</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Pages</th>
                <th style={{ textAlign: "left", padding: "10px 8px", color: "#666", fontSize: 13, fontWeight: 600 }}>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((p, i) => (
                <tr key={p._id || p.id || i} style={{ borderBottom: "1px solid #f0f0f0" }}>
                  <td style={{ padding: "10px 8px", color: "#333", fontSize: 14, fontFamily: "monospace" }}>
                    {p.policy_id || p._id || "—"}
                  </td>
                  <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                    {p.insurer_name || "—"}
                  </td>
                  <td style={{ padding: "10px 8px", color: "#333", fontSize: 14 }}>
                    {p.pages_extracted ?? p.pages ?? "—"}
                  </td>
                  <td style={{ padding: "10px 8px", color: "#666", fontSize: 14 }}>
                    {p.created_at ? new Date(p.created_at).toLocaleDateString() : "—"}
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
