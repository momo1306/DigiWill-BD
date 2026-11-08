import { useAuth } from '../context/AuthContext';
import { useI18n } from '../i18n';
import { Button, LangToggle, ThemeToggle } from '../components/ui';

/** A minimal protected page: proves the session works and gives a way to sign out. */
export default function Dashboard() {
  const { t } = useI18n();
  const { user, logout } = useAuth();

  return (
    <main className="auth-main" style={{ minHeight: '100vh' }}>
      <div className="auth-card">
        <div className="auth-top"><LangToggle /><ThemeToggle /></div>
        <div>
          <h1>{t('dashboard.hello', { name: user.full_name })}</h1>
          <p className="muted" style={{ marginTop: 8 }}>{t('dashboard.body')}</p>
        </div>
        <dl className="profile">
          <div><dt>{t('dashboard.email')}</dt><dd>{user.email}</dd></div>
          <div><dt>{t('dashboard.phone')}</dt><dd>{user.phone || '—'}</dd></div>
          <div><dt>{t('dashboard.language')}</dt><dd>{user.language === 'bn' ? t('dashboard.bangla') : t('dashboard.english')}</dd></div>
        </dl>
        <Button className="secondary" onClick={logout}>{t('dashboard.signOut')}</Button>
      </div>
    </main>
  );
}