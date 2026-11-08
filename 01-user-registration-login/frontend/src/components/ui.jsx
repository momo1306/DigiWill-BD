import { useId, useState } from 'react';
import { Link } from 'react-router-dom';
import { HugeiconsIcon } from '@hugeicons/react';
import {
  Alert02Icon,
  CheckmarkCircle02Icon,
  InformationCircleIcon,
  Moon02Icon,
  Sun03Icon,
  ViewIcon,
  ViewOffIcon,
} from '@hugeicons/core-free-icons';
import { useI18n } from '../i18n';

export function Icon({ icon, size = 20, strokeWidth = 1.7, ...rest }) {
  return <HugeiconsIcon icon={icon} size={size} strokeWidth={strokeWidth} aria-hidden="true" {...rest} />;
}

/** The mark: a stitched ring closed by a single knot. */
export function Logo({ size = 32 }) {
  const r = 13;
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <circle cx="16" cy="16" r={r} fill="none" stroke="currentColor" strokeWidth="2.4"
        strokeLinecap="round" strokeDasharray="4.2 3.2" transform="rotate(-90 16 16)" />
      <circle cx="16" cy="3" r="2.6" fill="currentColor" />
    </svg>
  );
}

export function Brand({ to = '/', sub = true }) {
  const { t } = useI18n();
  return (
    <Link className="brand" to={to}>
      <span className="brand-mark"><Logo /></span>
      <span className="brand-name">
        DigiWill BD
        {sub && <small>{t('brand.tagline')}</small>}
      </span>
    </Link>
  );
}

export function Spinner() {
  return <span className="spinner" role="status" aria-label="Loading" />;
}

export function Button({ loading, children, className = '', disabled, ...rest }) {
  return (
    <button className={`btn ${className}`} disabled={disabled || loading} {...rest}>
      {loading && <Spinner />}
      {children}
    </button>
  );
}

export function Field({ label, hint, error, children, id }) {
  return (
    <div className="field">
      {label && <label htmlFor={id}>{label}</label>}
      {children}
      {error ? <span className="error" role="alert">{error}</span> : hint ? <span className="hint">{hint}</span> : null}
    </div>
  );
}

export function TextField({ label, hint, error, textarea, ...rest }) {
  const id = useId();
  const Tag = textarea ? 'textarea' : 'input';
  return (
    <Field label={label} hint={hint} error={error} id={id}>
      <Tag id={id} className={textarea ? 'textarea' : 'input'} aria-invalid={error ? 'true' : undefined} {...rest} />
    </Field>
  );
}

export function PasswordField({ label, hint, error, ...rest }) {
  const id = useId();
  const [shown, setShown] = useState(false);
  const { t } = useI18n();
  return (
    <Field label={label} hint={hint} error={error} id={id}>
      <div className="input-wrap">
        <input id={id} className="input" type={shown ? 'text' : 'password'} aria-invalid={error ? 'true' : undefined} {...rest} />
        <button type="button" className="icon-btn" onClick={() => setShown((s) => !s)} aria-label={shown ? t('common.hide') : t('common.show')}>
          <Icon icon={shown ? ViewOffIcon : ViewIcon} size={18} />
        </button>
      </div>
    </Field>
  );
}

export function Alert({ tone = 'info', children }) {
  const icon = { error: Alert02Icon, warn: Alert02Icon, ok: CheckmarkCircle02Icon, info: InformationCircleIcon }[tone];
  return (
    <div className={`alert ${tone}`} role={tone === 'error' ? 'alert' : undefined}>
      <Icon icon={icon} size={18} />
      <div>{children}</div>
    </div>
  );
}

// ---- preferences ---------------------------------------------------------------

export function LangToggle() {
  const { lang, setLang } = useI18n();
  return (
    <div className="lang-toggle" role="group" aria-label="Language">
      <button aria-pressed={lang === 'bn'} onClick={() => setLang('bn')} lang="bn">বাংলা</button>
      <button aria-pressed={lang === 'en'} onClick={() => setLang('en')} lang="en">EN</button>
    </div>
  );
}

function currentTheme() {
  const set = document.documentElement.dataset.theme;
  if (set) return set;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeToggle() {
  const { t } = useI18n();
  const [theme, setTheme] = useState(currentTheme);
  const flip = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('dw.theme', next); } catch { /* storage blocked */ }
    setTheme(next);
  };
  return (
    <button className="icon-btn" onClick={flip} aria-label={theme === 'dark' ? t('common.lightMode') : t('common.darkMode')}>
      <Icon icon={theme === 'dark' ? Sun03Icon : Moon02Icon} size={19} />
    </button>
  );
}