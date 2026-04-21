import { useState, useEffect } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import { FiChevronDown, FiChevronUp, FiShield, FiFileText } from "react-icons/fi";

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

const STATUS_COLORS = {
  pending: { bg: "#ffa50220", text: WARNING, label: "Pending" },
  approved: { bg: "#2ed57320", text: SUCCESS, label: "Approved" },
  rejected: { bg: "#ff6b6b20", text: DANGER, label: "Rejected" },
  flagged: { bg: "#ffa50220", text: "#e67e22", label: "Flagged" },
};

export default function MyClaims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      const res = await api.get("/patient/claims");
      setClaims(res.data || []);
    } catch (err) {
      toast.error("Failed to load claims");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getStatusStyle = (status) => {
    const s = STATUS_COLORS[status] || STATUS_COLORS.pending;
    return {
      display: "inline-block",
      padding: "4px 14px",
      borderRadius: 20,
      fontSize: 12,
      fontWeight: 600,
      background: s.bg,
      color: s.text,
      textTransform: "capitalize",
    };
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
        <div style={{ fontSize: 18, color: "#666" }}>Loading claims...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 16px" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        <FiShield style={{ verticalAlign: "middle", marginRight: 10 }} />
        My Claims
      </h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 16 }}>
        Track the status of your insurance claims.
      </p>

      {claims.length === 0 ? (
        <div style={{ ...cardStyle, textAlign: "center", padding: 48 }}>
          <FiFileText size={48} color="#dfe6e9" style={{ marginBottom: 16 }} />
          <div style={{ fontSize: 18, fontWeight: 600, color: "#636e72", marginBottom: 8 }}>
            No Claims Found
          </div>
          <div style={{ color: "#b2bec3" }}>Your insurance claims will appear here.</div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {claims.map((claim) => {
            const claimId = claim._id || claim.id;
            const isExpanded = expandedId === claimId;
            const date = claim.date || claim.created_at;
            const items = claim.items || claim.claim_items || [];

            return (
              <div key={claimId} style={{ ...cardStyle, transition: "box-shadow 0.2s" }}>
                {/* Claim Header */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: 12,
                    cursor: items.length > 0 ? "pointer" : "default",
                  }}
                  onClick={() => items.length > 0 && toggleExpand(claimId)}
                >
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 12,
                        marginBottom: 8,
                        flexWrap: "wrap",
                      }}
                    >
                      <span style={getStatusStyle(claim.status)}>
                        {STATUS_COLORS[claim.status]?.label || claim.status}
                      </span>
                      {date && (
                        <span style={{ fontSize: 13, color: "#636e72" }}>
                          {new Date(date).toLocaleDateString("en-US", {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          })}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: 16, fontWeight: 600, color: "#2d3436", marginBottom: 4 }}>
                      {claim.diagnosis || "Insurance Claim"}
                    </div>
                    {claim.status_explanation && (
                      <p style={{ margin: "8px 0 0", fontSize: 14, color: "#636e72", lineHeight: 1.5 }}>
                        {claim.status_explanation}
                      </p>
                    )}
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 13, color: "#636e72" }}>Amount</div>
                      <div style={{ fontSize: 22, fontWeight: 700, color: "#2d3436" }}>
                        ₹{(claim.total_amount ?? claim.amount) != null ? Number(claim.total_amount ?? claim.amount).toFixed(2) : "--"}
                      </div>
                    </div>
                    {items.length > 0 && (
                      <div style={{ color: "#636e72" }}>
                        {isExpanded ? <FiChevronUp size={20} /> : <FiChevronDown size={20} />}
                      </div>
                    )}
                  </div>
                </div>

                {/* Expandable Claim Items */}
                {isExpanded && items.length > 0 && (
                  <div
                    style={{
                      marginTop: 20,
                      paddingTop: 20,
                      borderTop: "1px solid #f1f2f6",
                    }}
                  >
                    <div style={{ fontSize: 14, fontWeight: 600, color: "#636e72", marginBottom: 12 }}>
                      Claim Items
                    </div>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ borderBottom: "1px solid #dfe6e9" }}>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "8px 12px",
                              fontSize: 12,
                              color: "#636e72",
                              fontWeight: 600,
                            }}
                          >
                            Description
                          </th>
                          <th
                            style={{
                              textAlign: "right",
                              padding: "8px 12px",
                              fontSize: 12,
                              color: "#636e72",
                              fontWeight: 600,
                            }}
                          >
                            Amount
                          </th>
                          <th
                            style={{
                              textAlign: "center",
                              padding: "8px 12px",
                              fontSize: 12,
                              color: "#636e72",
                              fontWeight: 600,
                            }}
                          >
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map((item, idx) => (
                          <tr key={idx} style={{ borderBottom: "1px solid #f1f2f6" }}>
                            <td style={{ padding: "10px 12px", fontSize: 14, color: "#2d3436" }}>
                              {item.description || item.name || "--"}
                            </td>
                            <td
                              style={{
                                padding: "10px 12px",
                                textAlign: "right",
                                fontSize: 14,
                                fontWeight: 600,
                                color: "#2d3436",
                              }}
                            >
                              {item.amount != null ? `₹${Number(item.amount).toFixed(2)}` : "--"}
                            </td>
                            <td style={{ padding: "10px 12px", textAlign: "center" }}>
                              {item.status ? (
                                <span style={getStatusStyle(item.status)}>
                                  {STATUS_COLORS[item.status]?.label || item.status}
                                </span>
                              ) : (
                                "--"
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
