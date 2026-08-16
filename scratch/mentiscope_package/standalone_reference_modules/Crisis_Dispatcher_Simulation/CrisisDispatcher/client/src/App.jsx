import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Spin } from 'antd';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './layouts/AppLayout';
import theme from './styles/theme';

// Lazy-loaded pages
const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'));
const StudentDashboard = lazy(() => import('./pages/student/StudentDashboard'));
const AssessmentPage = lazy(() => import('./pages/student/AssessmentPage'));
const ResultsPage = lazy(() => import('./pages/student/ResultsPage'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const StudentsPage = lazy(() => import('./pages/admin/StudentsPage'));
const EventLogsPage = lazy(() => import('./pages/admin/EventLogsPage'));
const AnalyticsPage = lazy(() => import('./pages/admin/AnalyticsPage'));

const PageLoader = () => (
  <div style={{
    height: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#F0F2F5',
  }}>
    <Spin size="large" tip="Loading..." />
  </div>
);

export default function App() {
  return (
    <ConfigProvider theme={theme}>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Student routes */}
              <Route
                element={
                  <ProtectedRoute roles={['student']}>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="/dashboard" element={<StudentDashboard />} />
                <Route path="/assessment" element={<AssessmentPage />} />
                <Route path="/results" element={<ResultsPage />} />
              </Route>

              {/* Admin routes */}
              <Route
                element={
                  <ProtectedRoute roles={['admin']}>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/students" element={<StudentsPage />} />
                <Route path="/admin/events" element={<EventLogsPage />} />
                <Route path="/admin/analytics" element={<AnalyticsPage />} />
              </Route>

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ConfigProvider>
  );
}
