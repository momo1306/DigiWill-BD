import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import en from './en';
import bn from './bn';

const DICTS = { en, bn };
const STORE = 'dw.lang';
const BN_DIGITS = '০১২৩৪৫৬৭৮৯';

const I18nContext = createContext(null);

function lookup(dict, key) {
  return key.split('.').reduce((node, part) => (node == null ? node : node[part]), dict);
}

export const toBnDigits = (s) => String(s).replace(/\d/g, (d) => BN_DIGITS[d]);

function initialLang() {
  try {
    const saved = localStorage.getItem(STORE);
    if (saved === 'en' || saved === 'bn') return saved;
  } catch { /* storage blocked */ }
  return navigator.language?.startsWith('bn') ? 'bn' : 'en';
}

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(initialLang);

  const setLang = useCallback((l) => {
    if (l !== 'en' && l !== 'bn') return;
    setLangState(l);
    try { localStorage.setItem(STORE, l); } catch { /* storage blocked */ }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo(() => {
    const num = (n) => (lang === 'bn' ? toBnDigits(n) : String(n));
    const t = (key, vars) => {
      let s = lookup(DICTS[lang], key) ?? lookup(en, key) ?? key;
      if (s && typeof s === 'object' && 'other' in s) s = vars?.n === 1 ? s.one : s.other;
      if (typeof s !== 'string') return s;
      if (vars) {
        s = s.replace(/\{(\w+)\}/g, (_, k) => {
          const v = vars[k];
          return typeof v === 'number' ? num(v) : v ?? '';
        });
      }
      return s;
    };
    const err = (e) => {
      if (!e) return '';
      if (e.status === 0) return t('errors.network');
      if (e.status === 429) return t('errors.throttled');
      if (e.status >= 500) return t('errors.server');
      return e.message || t('errors.generic');
    };
    return { lang, setLang, t, num, err };
  }, [lang, setLang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export const useI18n = () => useContext(I18nContext);