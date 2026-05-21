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
  FiLock,
} from "react-icons/fi";

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const STATUS_COLORS = {
  pending: { bg: "#ffa50220", text: "#ffa502", label: "Pending" },
  adjudicated: { bg: "#3742fa20", text: "#3742fa", label: "Adjudicated" },
  approved: { bg: "#2ed57320", text: "#2ed573", label: "Approved" },
  rejected: { bg: "#ff4757", text: "#fff", label: "Rejected" },
  flagged: { bg: "#ff634820", text: "#ff6348", label: "Flagged" },
};

const TABS = ["all", "pending", "adjudicated", "approved", "rejected", "flagged"];

export default function Claims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const [expandedId, setExpandedId] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [approveAmounts, setApproveAmounts] = useState({});
  const [rejectReasons, setRejectReasons] = useState({});

  const [selectedIds, setSelectedIds] = useState(new Set());
  const [batchRejectReason, setBatchRejectReason] = useState("");
  const [batchLoading, setBatchLoading] = useState(false);

  useEffect(() => {
    fetchClaims();
    setSelectedIds(new Set());
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


  const toggleSelect = (claimId) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(claimId)) next.delete(claimId);
      else next.add(claimId);
      return next;
    });
  };

  const selectAllAdjudicated = () => {
    const adjudicatedIds = claims
      .filter((c) => c.status === "adjudicated")
      .map((c) => c.id);
    if (adjudicatedIds.length === 0) {
      toast("No adjudicated claims on this page");
      return;
    }
    if (selectedIds.size === adjudicatedIds.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(adjudicatedIds));
    }
  };

  const handleBatchApprove = async () => {
    if (selectedIds.size === 0) return toast.error("Select at least one claim");
    setBatchLoading(true);
    try {
      const res = await api.post("/insurer/claims/batch-approve", {
        claim_ids: Array.from(selectedIds),
      });
      toast.success(`Approved ${res.data.approved_count} claim(s)`);
      if (res.data.skipped?.length) {
        toast(`Skipped ${res.data.skipped.length} (not in adjudicated status)`);
      }
      setSelectedIds(new Set());
      fetchClaims();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Batch approve failed");
    } finally {
      setBatchLoading(false);
    }
  };

  const handleBatchReject = async () => {
    if (selectedIds.size === 0) return toast.error("Select at least one claim");
    if (!batchRejectReason.trim()) return toast.error("Provide a rejection reason");
    setBatchLoading(true);
    try {
      const res = await api.post("/insurer/claims/batch-reject", {
        claim_ids: Array.from(selectedIds),
        reason: batchRejectReason,
      });
      toast.success(`Rejected ${res.data.rejected_count} claim(s)`);
      if (res.data.skipped?.length) {
        toast(`Skipped ${res.data.skipped.length} (not in adjudicated status)`);
      }
      setSelectedIds(new Set());
      setBatchRejectReason("");
      fetchClaims();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Batch reject failed");
    } finally {
      setBatchLoading(false);
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
    return "₹" + Number(amount).toLocaleString("en-IN", { minimumFractionDigits: 2 });
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


      {selectedIds.size > 0 && (
        <div style={{
          display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap",
          padding: "12px 16px", marginBottom: 16,
          background: "#1a1a2e", color: "#fff", borderRadius: 10,
        }}>
          <span style={{ fontWeight: 600, fontSize: 14 }}>
            {selectedIds.size} adjudicated claim{selectedIds.size > 1 ? "s" : ""} selected
          </span>
          <button
            onClick={handleBatchApprove}
            disabled={batchLoading}
            style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              padding: "8px 16px", background: "#2ed573", color: "#fff",
              border: "none", borderRadius: 6, fontSize: 13, fontWeight: 600,
              cursor: batchLoading ? "not-allowed" : "pointer",
            }}
          >
            <FiCheckCircle size={14} />
            {batchLoading ? "Processing..." : "Batch Approve"}
          </button>
          <input
            type="text"
            placeholder="Rejection reason (required for batch reject)"
            value={batchRejectReason}
            onChange={(e) => setBatchRejectReason(e.target.value)}
            style={{
              padding: "8px 12px", border: "none", borderRadius: 6,
              fontSize: 13, width: 240, color: "#2d3436",
            }}
          />
          <button
            onClick={handleBatchReject}
            disabled={batchLoading}
            style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              padding: "8px 16px", background: "#ff6b6b", color: "#fff",
              border: "none", borderRadius: 6, fontSize: 13, fontWeight: 600,
              cursor: batchLoading ? "not-allowed" : "pointer",
            }}
          >
            <FiXCircle size={14} />
            Batch Reject
          </button>
          <button
            onClick={() => setSelectedIds(new Set())}
            style={{
              marginLeft: "auto", padding: "8px 14px",
              background: "transparent", color: "#aaa",
              border: "1px solid #444", borderRadius: 6, fontSize: 13,
              cursor: "pointer",
            }}
          >
            Clear selection
          </button>
        </div>
      )}


      <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
        {loading ? (
          <div style={{ padding: 48, textAlign: "center", color: "#888" }}>Loading claims...</div>
        ) : claims.length === 0 ? (
          <div style={{ padding: 48, textAlign: "center", color: "#888" }}>No claims found.</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8f9fa" }}>
                <th style={{ padding: "14px 10px", width: 36, borderBottom: "1px solid #eee" }}>
                  <input
                    type="checkbox"
                    title="Select all adjudicated claims"
                    checked={
                      claims.filter((c) => c.status === "adjudicated").length > 0 &&
                      selectedIds.size === claims.filter((c) => c.status === "adjudicated").length
                    }
                    onChange={selectAllAdjudicated}
                    style={{ cursor: "pointer" }}
                  />
                </th>
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
                const isSelectable = claim.status === "adjudicated";
                const isChecked = selectedIds.has(claim.id);
                return (
                  <Fragment key={claim.id}>
                    <tr
                      onClick={() => setExpandedId(isExpanded ? null : claim.id)}
                      style={{
                        cursor: "pointer",
                        background: isChecked ? "#3742fa10" : isExpanded ? "#f8f9fa" : "#fff",
                        transition: "background 0.15s",
                      }}
                      onMouseEnter={(e) => {
                        if (!isExpanded && !isChecked) e.currentTarget.style.background = "#fafafa";
                      }}
                      onMouseLeave={(e) => {
                        if (!isExpanded && !isChecked) e.currentTarget.style.background = "#fff";
                      }}
                    >
                      <td style={{ ...cellStyle, width: 36, padding: "14px 10px" }}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          disabled={!isSelectable}
                          onClick={(e) => e.stopPropagation()}
                          onChange={() => toggleSelect(claim.id)}
                          title={isSelectable ? "Select for batch action" : "Only adjudicated claims can be batch-processed"}
                          style={{ cursor: isSelectable ? "pointer" : "not-allowed", opacity: isSelectable ? 1 : 0.3 }}
                        />
                      </td>
                      <td style={cellStyle}>{formatDate(claim.submitted_at || claim.date || claim.created_at)}</td>
                      <td style={cellStyle}>{claim.patient_name || "N/A"}</td>
                      <td style={cellStyle}>{claim.doctor_name || "N/A"}</td>
                      <td style={cellStyle}>{claim.diagnosis || "N/A"}</td>
                      <td style={cellStyle}>
                        {formatAmount(claim.amount || claim.total_amount)}
                        {claim.status === "adjudicated" && claim.recommended_amount != null && claim.recommended_amount !== (claim.amount || claim.total_amount) && (
                          <div style={{ fontSize: 11, color: "#3742fa", marginTop: 2 }}>
                            Recommended: {formatAmount(claim.recommended_amount)}
                          </div>
                        )}
                      </td>
                      <td style={cellStyle}>
                        {getBadge(claim.status)}
                        {claim.status === "adjudicated" && claim.recommendation && (
                          <span style={{
                            display: "inline-block", marginLeft: 6, padding: "2px 8px",
                            fontSize: 10, fontWeight: 600, borderRadius: 10,
                            background: claim.recommendation === "approve" ? "#2ed57320" : "#ff6b6b20",
                            color: claim.recommendation === "approve" ? "#2ed573" : "#ff6b6b",
                          }}>
                            {claim.recommendation === "approve" ? "↑ approve" : "↓ reject"}
                          </span>
                        )}
                      </td>
                      <td style={cellStyle}>
                        {isExpanded ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
                      </td>
                    </tr>


                    {isExpanded && (
                      <tr>
                        <td colSpan={8} style={{ padding: 0 }}>
                          <div style={{ padding: 24, background: "#f8f9fa", borderTop: "1px solid #eee" }}>

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


                            {claim.status === "approved" || claim.status === "rejected" ? (
                              <div style={{ marginTop: 16, padding: "12px 16px", background: "#fff", border: "1px solid #eee", borderRadius: 8, display: "flex", alignItems: "center", gap: 10, fontSize: 13, color: "#636e72" }}>
                                <FiLock size={14} />
                                <span>
                                  Claim <strong style={{ color: claim.status === "approved" ? "#2ed573" : "#ff6b6b" }}>{claim.status}</strong>
                                  {claim.adjudicated_at && <> on <strong>{formatDate(claim.adjudicated_at)}</strong></>}
                                  {claim.status === "approved" && claim.approved_amount != null && <> · final amount <strong>{formatAmount(claim.approved_amount)}</strong></>}
                                  {claim.status === "rejected" && claim.rejection_reason && <> · reason: <em>{claim.rejection_reason}</em></>}
                                  . This decision is final.
                                </span>
                              </div>
                            ) : (
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
                            )}
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
