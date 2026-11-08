import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { I18nProvider } from './i18n';
import { Spinner } from './components/ui';
import { Login, Register } from './pages/Auth';
import Dashboard from './pages/Dashboard';

const Loading = () => <div className="loading-screen"><Spinner /></div>;

/** Signed-in users only; everyone else is sent to /login. */
function Private({ children }) {
  const { user, ready } = useAuth();
  if (!ready) return <Loading />;
  return user ? children : <Navigate to="/login" replace />;
}

/** Login / register pages; a signed-in user is sent on to the app. */
function GuestOnly({ children }) {
  const { user, ready } = useAuth();
  if (!ready) return <Loading />;
  return user ? <Navigate to="/app" replace /> : children;
}

export default function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/app" replace />} />
            <Route path="/login" element={<GuestOnly><Login /></GuestOnly>} />
            <Route path="/register" element={<GuestOnly><Register /></GuestOnly>} />
            <Route path="/app" element={<Private><Dashboard /></Private>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </I18nProvider>
  );
}