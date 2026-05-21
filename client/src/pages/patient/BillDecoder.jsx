import { useState, useRef } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import {
  FiUploadCloud,
  FiCheckCircle,
  FiXCircle,
  FiDollarSign,
  FiFile,
} from "react-icons/fi";

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const PRIMARY = "#4ecdc4";
const DANGER = "#ff6b6b";
const SUCCESS = "#2ed573";

export default function BillDecoder() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) {
      toast.error("Please upload an image file");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    handleFile(f);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select an image first");
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post("/patient/upload-bill", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      toast.success("Bill decoded successfully!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to decode bill");
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.analysis || {};
  const ocrItems = result?.items || [];
  const llmItems = analysis.line_items || [];
  const items = llmItems.length ? llmItems : ocrItems;
  const summary = {
    total: analysis.total ?? ocrItems.reduce((s, i) => s + (Number(i.amount) || 0), 0),
    covered_amount: analysis.covered_total,
    out_of_pocket: analysis.out_of_pocket,
  };
  const plainSummary = analysis.summary || "";
  const hasCoverage = items.some((it) => typeof it.covered === "boolean");

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 16px" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        Bill Decoder
      </h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 16 }}>
        Upload a medical bill image and we will break it down for you in plain language.
      </p>


      <div
        style={{
          ...cardStyle,
          border: `2px dashed ${dragOver ? PRIMARY : "#dfe6e9"}`,
          background: dragOver ? `${PRIMARY}08` : "#fafafa",
          textAlign: "center",
          cursor: "pointer",
          marginBottom: 24,
          transition: "border-color 0.2s, background 0.2s",
        }}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {preview ? (
          <div>
            <img
              src={preview}
              alt="Bill preview"
              style={{ maxHeight: 200, borderRadius: 8, marginBottom: 12 }}
            />
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, color: "#636e72" }}>
              <FiFile size={16} />
              <span>{file?.name}</span>
            </div>
          </div>
        ) : (
          <div style={{ padding: "32px 0" }}>
            <FiUploadCloud size={48} color={PRIMARY} style={{ marginBottom: 12 }} />
            <div style={{ fontSize: 16, fontWeight: 600, color: "#2d3436", marginBottom: 4 }}>
              Drag and drop your bill image here
            </div>
            <div style={{ fontSize: 14, color: "#636e72" }}>or click to browse files</div>
          </div>
        )}
      </div>


      <div style={{ textAlign: "center", marginBottom: 32 }}>
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          style={{
            background: loading || !file ? "#b2bec3" : PRIMARY,
            color: "#fff",
            border: "none",
            borderRadius: 8,
            padding: "12px 32px",
            fontSize: 16,
            fontWeight: 600,
            cursor: loading || !file ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
        >
          {loading ? "Processing... This may take a moment" : "Upload & Decode"}
        </button>
      </div>


      {loading && (
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div
            style={{
              width: 40,
              height: 40,
              border: `4px solid ${PRIMARY}30`,
              borderTopColor: PRIMARY,
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto 12px",
            }}
          />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <p style={{ color: "#636e72" }}>Running OCR and analyzing your bill...</p>
        </div>
      )}


      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

          {plainSummary && (
            <div style={{ ...cardStyle, borderLeft: `4px solid ${PRIMARY}` }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12, color: "#2d3436" }}>
                Plain Language Summary
              </h3>
              <p style={{ color: "#2d3436", lineHeight: 1.6, margin: 0, whiteSpace: "pre-wrap" }}>
                {plainSummary}
              </p>
            </div>
          )}


          <div style={{ ...cardStyle, background: "#f8f9fa" }}>
            <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: "#2d3436" }}>
              <FiDollarSign style={{ verticalAlign: "middle", marginRight: 8 }} />
              Bill Summary
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16 }}>
              <div style={{ ...cardStyle, textAlign: "center" }}>
                <div style={{ fontSize: 13, color: "#636e72", marginBottom: 4 }}>Total</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#2d3436" }}>
                  {summary.total != null ? `₹${Number(summary.total).toFixed(2)}` : "--"}
                </div>
              </div>
              <div style={{ ...cardStyle, textAlign: "center" }}>
                <div style={{ fontSize: 13, color: "#636e72", marginBottom: 4 }}>Covered Amount</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: SUCCESS }}>
                  {summary.covered_amount != null ? `₹${Number(summary.covered_amount).toFixed(2)}` : "--"}
                </div>
              </div>
              <div
                style={{
                  ...cardStyle,
                  textAlign: "center",
                  background: `${DANGER}10`,
                  border: `1px solid ${DANGER}30`,
                }}
              >
                <div style={{ fontSize: 13, color: "#636e72", marginBottom: 4 }}>Out-of-Pocket</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: DANGER }}>
                  {summary.out_of_pocket != null ? `₹${Number(summary.out_of_pocket).toFixed(2)}` : "--"}
                </div>
              </div>
            </div>
          </div>


          {items.length > 0 && (
            <div style={{ ...cardStyle, overflowX: "auto" }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: "#2d3436" }}>
                Bill Items
              </h3>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #dfe6e9" }}>
                    <th style={{ textAlign: "left", padding: "10px 12px", color: "#636e72", fontSize: 13, fontWeight: 600 }}>
                      Description
                    </th>
                    <th style={{ textAlign: "right", padding: "10px 12px", color: "#636e72", fontSize: 13, fontWeight: 600 }}>
                      Amount
                    </th>
                    <th style={{ textAlign: "center", padding: "10px 12px", color: "#636e72", fontSize: 13, fontWeight: 600 }}>
                      Covered
                    </th>
                    <th style={{ textAlign: "left", padding: "10px 12px", color: "#636e72", fontSize: 13, fontWeight: 600 }}>
                      Explanation
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, idx) => {
                    const label = item.item || item.description || "Unnamed";
                    const knownCoverage = typeof item.covered === "boolean";
                    return (
                      <tr key={idx} style={{ borderBottom: "1px solid #f1f2f6" }}>
                        <td style={{ padding: "12px", color: "#2d3436" }}>{label}</td>
                        <td style={{ padding: "12px", textAlign: "right", color: "#2d3436", fontWeight: 600 }}>
                          ₹{Number(item.amount).toFixed(2)}
                        </td>
                        <td style={{ padding: "12px", textAlign: "center" }}>
                          {knownCoverage ? (
                            item.covered ? (
                              <FiCheckCircle size={20} color={SUCCESS} />
                            ) : (
                              <FiXCircle size={20} color={DANGER} />
                            )
                          ) : (
                            <span style={{ color: "#b2bec3", fontSize: 13 }}>—</span>
                          )}
                        </td>
                        <td style={{ padding: "12px", color: "#636e72", fontSize: 14 }}>
                          {item.explanation || (hasCoverage ? "--" : "Coverage analysis unavailable")}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}


        </div>
      )}
    </div>
  );
}
