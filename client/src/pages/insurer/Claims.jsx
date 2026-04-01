import { useState, useEffect, Fragment } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import {
  FiChevronDown,
  FiChevronUp,
  FiCheckCircle,
  FiXCircle,
  FiZap,
  FiFilter,
} from "react-icons/fi";

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const STATUS_COLORS = {
  pending: { bg: "#ffa50220", text: "#ffa502", label: "Pending" },
  approved: { bg: "#2ed57320", text: "#2ed573", label: "Approved" },
  rejected: { bg: "#ff4757", text: "#fff", label: "Rejected" },
  flagged: { bg: "#ff634820", text: "#ff6348", label: "Flagged" },
};

const TABS = ["all", "pending", "approved", "rejected", "flagged"];

export default function Claims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const [expandedId, setExpandedId] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [approveAmounts, setApproveAmounts] = useState({});
  const [rejectReasons, setRejectReasons] = useState({});

  useEffect(() => {
    fetchClaims();
  }, [activeTab]);

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const params = activeTab !== "all" ? { status: activeTab } : {};
      const res = await api.get("/insurer/claims", { params });
      setClaims(res.data);
    } catch (err) {
      toast.error("Failed to load claims");
    } finally {
      setLoading(false);
    }
  };

  const handleAutoAdjudicate = async (claimId) => {
    setActionLoading(claimId + "-adjudicate");
    try {
      await api.post(`/insurer/claims/${claimId}/adjudicate`);
      toast.success("Claim adjudicated");
      fetchClaims();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Adjudication failed");
    } finally {
      setActionLoading(null);
    }
  };

  const handleApprove = async (claimId) => {
    setActionLoading(claimId + "-approve");
    try {
      const body = {};
      if (approveAmounts[claimId]) {
        body.approved_amount = parseFloat(approveAmounts[claimId]);
      }
      await api.post(`/insurer/claims/${claimId}/approve`, body);
      toast.success("Claim approved");
      setApproveAmounts((prev) => ({ ...prev, [claimId]: "" }));
      fetchClaims();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Approval failed");
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (claimId) => {
    if (!rejectReasons[claimId]?.trim()) {
      toast.error("Please provide a rejection reason");
      return;
    }
    setActionLoading(claimId + "-reject");
    try {
      await api.post(`/insurer/claims/${claimId}/reject`, {
        reason: rejectReasons[claimId],
      });
      toast.success("Claim rejected");
      setRejectReasons((prev) => ({ ...prev, [claimId]: "" }));
      fetchClaims();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Rejection failed");
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatAmount = (amount) => {
    if (amount == null) return "N/A";
    return "$" + Number(amount).toLocaleString("en-US", { minimumFractionDigits: 2 });
  };

  const getBadge = (status) => {
    const s = STATUS_COLORS[status] || STATUS_COLORS.pending;
    return (
      <span
        style={{
          display: "inline-block",
          padding: "4px 12px",
          borderRadius: 20,
          fontSize: 12,
          fontWeight: 600,
          background: s.bg,
          color: s.text,
        }}
      >
        {s.label}
      </span>
    );
  };

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: "0 auto" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>
        Claims Management
      </h1>
      <p style={{ color: "#636e72", marginBottom: 24, fontSize: 15 }}>
        Review, adjudicate, and manage insurance claims.
      </p>

      {/* Filter Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "8px 20px",
              borderRadius: 8,
              border: "none",
              fontSize: 14,
              fontWeight: 600,
              cursor: "pointer",
              background: activeTab === tab ? "#4ecdc4" : "#f1f2f6",
              color: activeTab === tab ? "#fff" : "#636e72",
              transition: "all 0.2s",
            }}
          >
            <FiFilter size={12} style={{ marginRight: 6, verticalAlign: "middle" }} />
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Claims Table */}
      <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
        {loading ? (
          <div style={{ padding: 48, textAlign: "center", color: "#888" }}>Loading claims...</div>
        ) : claims.length === 0 ? (
          <div style={{ padding: 48, textAlign: "center", color: "#888" }}>No claims found.</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8f9fa" }}>
                {["Date", "Patient", "Doctor", "Diagnosis", "Amount", "Status", ""].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: "14px 16px",
                      textAlign: "left",
                      fontSize: 13,
                      fontWeight: 600,
                      color: "#636e72",
                      borderBottom: "1px solid #eee",
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {claims.map((claim) => {
                const isExpanded = expandedId === claim.id;
                return (
                  <Fragment key={claim.id}>
                    <tr
                      onClick={() => setExpandedId(isExpanded ? null : claim.id)}
                      style={{
                        cursor: "pointer",
                        background: isExpanded ? "#f8f9fa" : "#fff",
                        transition: "background 0.15s",
                      }}
                      onMouseEnter={(e) => {
                        if (!isExpanded) e.currentTarget.style.background = "#fafafa";
                      }}
                      onMouseLeave={(e) => {
                        if (!isExpanded) e.currentTarget.style.background = "#fff";
                      }}
                    >
                      <td style={cellStyle}>{formatDate(claim.date || claim.created_at)}</td>
                      <td style={cellStyle}>{claim.patient_name || "N/A"}</td>
                      <td style={cellStyle}>{claim.doctor_name || "N/A"}</td>
                      <td style={cellStyle}>{claim.diagnosis || "N/A"}</td>
                      <td style={cellStyle}>{formatAmount(claim.amount || claim.total_amount)}</td>
                      <td style={cellStyle}>{getBadge(claim.status)}</td>
                      <td style={cellStyle}>
                        {isExpanded ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
                      </td>
                    </tr>

                    {/* Expanded Detail Panel */}
                    {isExpanded && (
                      <tr>
                        <td colSpan={7} style={{ padding: 0 }}>
                          <div style={{ padding: 24, background: "#f8f9fa", borderTop: "1px solid #eee" }}>
                            {/* Items Breakdown */}
                            {claim.items && claim.items.length > 0 && (
                              <div style={{ marginBottom: 16 }}>
                                <h4 style={{ fontSize: 14, fontWeight: 600, color: "#2d3436", marginBottom: 8 }}>
                                  Items Breakdown
                                </h4>
                                <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff", borderRadius: 8, overflow: "hidden" }}>
                                  <thead>
                                    <tr>
                                      {["Description", "Quantity", "Unit Price", "Total"].map((h) => (
                                        <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontSize: 12, color: "#636e72", borderBottom: "1px solid #eee" }}>
                                          {h}
                                        </th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {claim.items.map((item, idx) => (
                                      <tr key={idx}>
                                        <td style={{ padding: "8px 12px", fontSize: 13 }}>{item.description || item.name}</td>
                                        <td style={{ padding: "8px 12px", fontSize: 13 }}>{item.quantity ?? 1}</td>
                                        <td style={{ padding: "8px 12px", fontSize: 13 }}>{formatAmount(item.unit_price || item.price)}</td>
                                        <td style={{ padding: "8px 12px", fontSize: 13 }}>{formatAmount(item.total || item.amount)}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            )}

                            {/* ICD Codes */}
                            {claim.icd_codes && claim.icd_codes.length > 0 && (
                              <div style={{ marginBottom: 16 }}>
                                <h4 style={{ fontSize: 14, fontWeight: 600, color: "#2d3436", marginBottom: 8 }}>
                                  ICD Codes
                                </h4>
                                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                                  {claim.icd_codes.map((code, idx) => (
                                    <span
                                      key={idx}
                                      style={{
                                        padding: "4px 12px",
                                        background: "#4ecdc418",
                                        color: "#4ecdc4",
                                        borderRadius: 6,
                                        fontSize: 13,
                                        fontWeight: 600,
                                      }}
                                    >
                                      {typeof code === "string" ? code : code.code}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Adjudication Notes */}
                            {claim.adjudication_notes && (
                              <div style={{ marginBottom: 16 }}>
                                <h4 style={{ fontSize: 14, fontWeight: 600, color: "#2d3436", marginBottom: 8 }}>
                                  Adjudication Notes
                                </h4>
                                <p style={{ fontSize: 13, color: "#636e72", background: "#fff", padding: 12, borderRadius: 8, margin: 0 }}>
                                  {claim.adjudication_notes}
                                </p>
                              </div>
                            )}

                            {/* Action Buttons */}
                            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end", marginTop: 16 }}>
                              {claim.status === "pending" && (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleAutoAdjudicate(claim.id);
                                  }}
                                  disabled={actionLoading === claim.id + "-adjudicate"}
                                  style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "8px 16px",
                                    background: "#4ecdc4",
                                    color: "#fff",
                                    border: "none",
                                    borderRadius: 6,
                                    fontSize: 13,
                                    fontWeight: 600,
                                    cursor: "pointer",
                                  }}
                                >
                                  <FiZap size={14} />
                                  {actionLoading === claim.id + "-adjudicate" ? "Processing..." : "Auto-Adjudicate"}
                                </button>
                              )}

                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <input
                                  type="number"
                                  placeholder="Approved amount"
                                  value={approveAmounts[claim.id] || ""}
                                  onClick={(e) => e.stopPropagation()}
                                  onChange={(e) =>
                                    setApproveAmounts((prev) => ({
                                      ...prev,
                                      [claim.id]: e.target.value,
                                    }))
                                  }
                                  style={{
                                    padding: "8px 12px",
                                    border: "1px solid #dfe6e9",
                                    borderRadius: 6,
                                    fontSize: 13,
                                    width: 140,
                                  }}
                                />
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleApprove(claim.id);
                                  }}
                                  disabled={actionLoading === claim.id + "-approve"}
                                  style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "8px 16px",
                                    background: "#2ed573",
                                    color: "#fff",
                                    border: "none",
                                    borderRadius: 6,
                                    fontSize: 13,
                                    fontWeight: 600,
                                    cursor: "pointer",
                                  }}
                                >
                                  <FiCheckCircle size={14} />
                                  {actionLoading === claim.id + "-approve" ? "Approving..." : "Approve"}
                                </button>
                              </div>

                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <input
                                  type="text"
                                  placeholder="Rejection reason"
                                  value={rejectReasons[claim.id] || ""}
                                  onClick={(e) => e.stopPropagation()}
                                  onChange={(e) =>
                                    setRejectReasons((prev) => ({
                                      ...prev,
                                      [claim.id]: e.target.value,
                                    }))
                                  }
                                  style={{
                                    padding: "8px 12px",
                                    border: "1px solid #dfe6e9",
                                    borderRadius: 6,
                                    fontSize: 13,
                                    width: 200,
                                  }}
                                />
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleReject(claim.id);
                                  }}
                                  disabled={actionLoading === claim.id + "-reject"}
                                  style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "8px 16px",
                                    background: "#ff6b6b",
                                    color: "#fff",
                                    border: "none",
                                    borderRadius: 6,
                                    fontSize: 13,
                                    fontWeight: 600,
                                    cursor: "pointer",
                                  }}
                                >
                                  <FiXCircle size={14} />
                                  {actionLoading === claim.id + "-reject" ? "Rejecting..." : "Reject"}
                                </button>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const cellStyle = {
  padding: "14px 16px",
  fontSize: 14,
  color: "#2d3436",
  borderBottom: "1px solid #f1f2f6",
};
