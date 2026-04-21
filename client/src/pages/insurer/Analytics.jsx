import { useState, useEffect } from "react";
import api from "../../utils/api";
import toast from "react-hot-toast";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts";
import { FiFileText, FiDollarSign, FiTrendingUp, FiPieChart } from "react-icons/fi";

const cardStyle = {
  background: "#fff",
  borderRadius: 12,
  padding: 24,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

const STATUS_COLORS = {
  pending: "#ffa502",
  approved: "#2ed573",
  rejected: "#ff4757",
  flagged: "#ff6348",
};

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await api.get("/insurer/analytics");
      setData(res.data);
    } catch (err) {
      toast.error("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
        <p style={{ fontSize: 18, color: "#888" }}>Loading analytics...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
        <p style={{ fontSize: 18, color: "#888" }}>No analytics data available.</p>
      </div>
    );
  }

  const pieData = [
    { name: "Pending", value: data.pending ?? 0 },
    { name: "Approved", value: data.approved ?? 0 },
    { name: "Rejected", value: data.rejected ?? 0 },
    { name: "Flagged", value: data.flagged ?? 0 },
  ].filter((d) => d.value > 0);

  const PIE_COLORS = [STATUS_COLORS.pending, STATUS_COLORS.approved, STATUS_COLORS.rejected, STATUS_COLORS.flagged];

  const diagnosisData = (data.top_diagnoses || []).map((d) => ({
    name: d.diagnosis,
    count: d.count,
  }));

  const trendData = (data.monthly_trend || []).map((m) => ({
    month: m.month,
    count: m.count || 0,
    amount: m.amount || 0,
  }));

  const summaryCards = [
    { label: "Total Claims", value: data.total_claims ?? 0, icon: <FiFileText size={24} />, color: "#4ecdc4" },
    {
      label: "Total Amount",
      value: "₹" + Number(data.total_amount ?? 0).toLocaleString("en-IN", { minimumFractionDigits: 2 }),
      icon: <FiDollarSign size={24} />,
      color: "#ffa502",
    },
    {
      label: "Approval Rate",
      value:
        data.total_claims > 0
          ? ((data.approved ?? 0) / data.total_claims * 100).toFixed(1) + "%"
          : "0%",
      icon: <FiTrendingUp size={24} />,
      color: "#2ed573",
    },
    {
      label: "Flagged Rate",
      value:
        data.total_claims > 0
          ? ((data.flagged ?? 0) / data.total_claims * 100).toFixed(1) + "%"
          : "0%",
      icon: <FiPieChart size={24} />,
      color: "#ff6348",
    },
  ];

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: "0 auto" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#2d3436" }}>Analytics</h1>
      <p style={{ color: "#636e72", marginBottom: 32, fontSize: 15 }}>
        Claims analytics and insights for your organization.
      </p>

      {/* Summary Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20, marginBottom: 32 }}>
        {summaryCards.map((card) => (
          <div key={card.label} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 10,
                background: card.color + "18",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: card.color,
              }}
            >
              {card.icon}
            </div>
            <div>
              <p style={{ fontSize: 13, color: "#636e72", margin: 0 }}>{card.label}</p>
              <p style={{ fontSize: 24, fontWeight: 700, margin: 0, color: "#2d3436" }}>{card.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {/* Pie Chart: Claims by Status */}
        <div style={cardStyle}>
          <h3 style={{ fontSize: 16, fontWeight: 600, color: "#2d3436", marginBottom: 16 }}>
            Claims by Status
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={4}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, idx) => (
                    <Cell key={entry.name} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "#888", textAlign: "center", padding: 40 }}>No data</p>
          )}
        </div>

        {/* Bar Chart: Top Diagnoses */}
        <div style={cardStyle}>
          <h3 style={{ fontSize: 16, fontWeight: 600, color: "#2d3436", marginBottom: 16 }}>
            Top Diagnoses by Claim Count
          </h3>
          {diagnosisData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={diagnosisData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f2f6" />
                <XAxis type="number" tick={{ fontSize: 12, fill: "#636e72" }} />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fontSize: 12, fill: "#636e72" }}
                  width={120}
                />
                <Tooltip />
                <Bar dataKey="count" fill="#4ecdc4" radius={[0, 6, 6, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "#888", textAlign: "center", padding: 40 }}>No data</p>
          )}
        </div>
      </div>

      {/* Line Chart: Monthly Trend */}
      <div style={cardStyle}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: "#2d3436", marginBottom: 16 }}>
          Monthly Claims Trend
        </h3>
        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={trendData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f2f6" />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#636e72" }} />
              <YAxis yAxisId="left" tick={{ fontSize: 12, fill: "#636e72" }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12, fill: "#636e72" }} />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="count"
                stroke="#4ecdc4"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Claim Count"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="amount"
                stroke="#ffa502"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Total Amount (₹)"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: "#888", textAlign: "center", padding: 40 }}>No trend data available</p>
        )}
      </div>
    </div>
  );
}
