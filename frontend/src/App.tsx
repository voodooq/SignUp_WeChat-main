import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './layouts/AdminLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import EventManage from './pages/EventManage';
import RegistrationManage from './pages/RegistrationManage';
import SettingsManage from './pages/SettingsManage';
import SchoolManage from './pages/SchoolManage';
import BannerManage from './pages/BannerManage';
import NoticeImageManage from './pages/NoticeImageManage';
import ScoreManage from './pages/ScoreManage';
import CompetitionManage from './pages/CompetitionManage';
import GymManage from './pages/GymManage';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('admin_token');
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AdminLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="events" element={<EventManage />} />
          <Route path="registrations" element={<RegistrationManage />} />
          <Route path="schools" element={<SchoolManage />} />
          <Route path="banners" element={<BannerManage />} />
          <Route path="notices" element={<NoticeImageManage />} />
          <Route path="scores" element={<ScoreManage />} />
          <Route path="competitions" element={<CompetitionManage />} />
          <Route path="gyms" element={<GymManage />} />
          <Route path="settings" element={<SettingsManage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
