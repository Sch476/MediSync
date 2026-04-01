/**
 * MediSync App — Root component with role-based routing.
 */
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

// Auth pages
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

// Doctor pages
import DoctorDashboard from "./pages/doctor/DoctorDashboard";
import Consultation from "./pages/doctor/Consultation";
import ClinicalNotes from "./pages/doctor/ClinicalNotes";
import UploadPolicy from "./pages/doctor/UploadPolicy";

// Insurer pages
import InsurerDashboard from "./pages/insurer/InsurerDashboard";
import Claims from "./pages/insurer/Claims";
import Analytics from "./pages/insurer/Analytics";

// Patient pages
import PatientDashboard from "./pages/patient/PatientDashboard";
import BillDecoder from "./pages/patient/BillDecoder";
import DischargeSummary from "./pages/patient/DischargeSummary";
import HealthCheck from "./pages/patient/HealthCheck";
import MyClaims from "./pages/patient/MyClaims";

function RootRedirect() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={`/${user.role}`} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Doctor routes */}
          <Route path="/doctor" element={
            <ProtectedRoute allowedRoles={["doctor"]}><Layout /></ProtectedRoute>
          }>
            <Route index element={<DoctorDashboard />} />
            <Route path="consultation" element={<Consultation />} />
            <Route path="notes" element={<ClinicalNotes />} />
            <Route path="upload-policy" element={<UploadPolicy />} />
            <Route path="alerts" element={<DoctorDashboard />} />
          </Route>

          {/* Insurer routes */}
          <Route path="/insurer" element={
            <ProtectedRoute allowedRoles={["insurer"]}><Layout /></ProtectedRoute>
          }>
            <Route index element={<InsurerDashboard />} />
            <Route path="claims" element={<Claims />} />
            <Route path="analytics" element={<Analytics />} />
          </Route>

          {/* Patient routes */}
          <Route path="/patient" element={
            <ProtectedRoute allowedRoles={["patient"]}><Layout /></ProtectedRoute>
          }>
            <Route index element={<PatientDashboard />} />
            <Route path="bill-decoder" element={<BillDecoder />} />
            <Route path="discharge" element={<DischargeSummary />} />
            <Route path="health-check" element={<HealthCheck />} />
            <Route path="claims" element={<MyClaims />} />
          </Route>

          {/* Root redirect */}
          <Route path="/" element={<RootRedirect />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
