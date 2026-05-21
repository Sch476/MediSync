import { useState, useEffect } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import { FiXCircle, FiCheckCircle } from "react-icons/fi";

export default function Payable() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(null);

  const fetchPayable = () => {
    api.get("/patient/payable")
      .then((r) => setData(r.data))
      .catch(() => toast.error("Failed to load payable items"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchPayable(); }, []);

  const markAsPaid = async (billId) => {
    setPaying(billId);
    try {
      await api.post(`/patient/payable/${billId}/paid`);
      toast.success("Marked as paid — cleared from your payable");
      fetchPayable();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to mark as paid");
    } finally {
      setPaying(null);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
        <p style={{ color: "#888", fontSize: 16 }}>Loading your payable items...</p>
      </div>
    );
  }

  if (!data) return null;

  const allClear = data.total_payable === 0;

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: "0 auto" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 4, color: "#2d3436" }}>My Payable</h1>
      <p style={{ color: "#636e72", fontSize: 15, marginBottom: 28 }}>
        Items not covered by your insurance policy — to be paid at the hospital counter.
      </p>


      <div
        style={{
          background: allClear
            ? "linear-gradient(135deg, #2ed573, #1abc9c)"
            : "linear-gradient(135deg, #ff6b6b, #ff4757)",
          borderRadius: 16,
          padding: "28px 32px",
          color: "#fff",
          marginBottom: 28,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <p style={{ margin: "0 0 4px", fontSize: 13, opacity: 0.85, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>
            Total Amount Payable at Counter
          </p>
          <p style={{ margin: 0, fontSize: 42, fontWeight: 800, lineHeight: 1 }}>
            ₹{data.total_payable?.toLocaleString()}
          </p>
          {allClear && (
            <p style={{ margin: "8px 0 0", fontSize: 14, opacity: 0.9 }}>
              Nothing outstanding — you're all clear!
            </p>
          )}
        </div>
        {allClear ? (
          <FiCheckCircle size={52} style={{ opacity: 0.8 }} />
        ) : (
          <FiXCircle size={52} style={{ opacity: 0.8 }} />
        )}
      </div>


      {data.bills?.length === 0 ? (
        <div style={{ background: "#fff", borderRadius: 12, padding: 48, textAlign: "center", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}>
          <FiCheckCircle size={40} color="#2ed573" style={{ marginBottom: 12 }} />
          <p style={{ color: "#636e72", fontSize: 16 }}>No outstanding payable items from the hospital.</p>
        </div>
      ) : (
        data.bills.map((bill) => (
          <div
            key={bill.id}
            style={{
              background: "#fff",
              borderRadius: 12,
              padding: 24,
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              marginBottom: 16,
            }}
          >

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <p style={{ fontSize: 16, fontWeight: 700, color: "#2d3436", margin: "0 0 3px" }}>
                  {bill.hospital_name || "Hospital"}
                </p>
                <p style={{ fontSize: 13, color: "#636e72", margin: 0 }}>Bill date: {bill.bill_date}</p>
              </div>
              <div style={{ textAlign: "right" }}>
                <span
                  style={{
                    background: "#fff5f5",
                    color: "#ff4757",
                    padding: "6px 16px",
                    borderRadius: 20,
                    fontSize: 15,
                    fontWeight: 700,
                  }}
                >
                  ₹{bill.patient_total?.toLocaleString()}
                </span>
                <p style={{ fontSize: 11, color: "#aaa", margin: "4px 0 0", textAlign: "right" }}>
                  {bill.status === "submitted" ? "Claim sent to insurer" : "Draft"}
                </p>
              </div>
            </div>


            <div style={{ marginBottom: 12 }}>
              <button
                onClick={() => markAsPaid(bill.id)}
                disabled={paying === bill.id}
                style={{
                  padding: "8px 20px", background: paying === bill.id ? "#aaa" : "#2ed573",
                  color: "#fff", border: "none", borderRadius: 8, fontSize: 13,
                  fontWeight: 600, cursor: paying === bill.id ? "not-allowed" : "pointer",
                  display: "inline-flex", alignItems: "center", gap: 6,
                }}
              >
                <FiCheckCircle size={14} />
                {paying === bill.id ? "Processing..." : "Mark as Paid"}
              </button>
            </div>


            <div style={{ borderTop: "1px solid #f5f5f5", paddingTop: 12 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr auto", gap: 8, marginBottom: 6 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: "#aaa", textTransform: "uppercase", letterSpacing: 0.5 }}>Item</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: "#aaa", textTransform: "uppercase", letterSpacing: 0.5 }}>Reason not covered</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: "#aaa", textTransform: "uppercase", letterSpacing: 0.5, textAlign: "right" }}>Amount</span>
              </div>
              {bill.patient_items?.map((item, i) => (
                <div
                  key={i}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 2fr auto",
                    gap: 8,
                    padding: "8px 0",
                    borderBottom: i < bill.patient_items.length - 1 ? "1px solid #fafafa" : "none",
                    alignItems: "start",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <FiXCircle size={13} color="#ff4757" style={{ flexShrink: 0, marginTop: 2 }} />
                    <span style={{ fontSize: 14, color: "#2d3436", fontWeight: 500 }}>{item.description}</span>
                  </div>
                  <span style={{ fontSize: 12, color: "#888" }}>
                    {item.coverage_reason || "Not covered by your insurance policy"}
                  </span>
                  <span style={{ fontSize: 14, fontWeight: 700, color: "#ff4757", textAlign: "right" }}>
                    ₹{Number(item.amount).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
