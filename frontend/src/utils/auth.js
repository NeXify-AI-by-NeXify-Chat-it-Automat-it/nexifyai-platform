/**
 * Zentraler Auth-Helper für NeXifyAI Frontend
 * Single Source of Truth für Token, Session, Logout, Redirects.
 *
 * Best Practice:
 * - Nur EINE localStorage-Ebene pro Rolle (admin / customer)
 * - Niemals localStorage-Side-Effects im React-Render
 * - Logout cleart immer ALLE rollenrelevanten Keys
 */

const KEYS = {
  AUTH: 'nx_auth',                    // Hauptobjekt {token, role, email, name}
  ADMIN_TOKEN: 'nx_admin_token',      // Legacy — admin token (kompatibel)
  PORTAL_TOKEN: 'nx_portal_token',    // Legacy — portal token (kompatibel)
  PORTAL_EMAIL: 'nx_portal_email',
  PORTAL_NAME: 'nx_portal_name',
  ACTIVE_CONVO: 'nx_active_convo',
  ADMIN_VIEW: 'nx_admin_view',
  SIDEBAR_OPEN: 'nx_admin_sidebar_open',
};

const ALL_KEYS = Object.values(KEYS);

/** Liest die aktuelle Session aus, oder null. */
export const getAuth = () => {
  try {
    const raw = localStorage.getItem(KEYS.AUTH);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed?.token) return null;
    return parsed;
  } catch {
    return null;
  }
};

/** Speichert eine Session konsistent. */
export const setAuth = ({ token, role, email, name }) => {
  if (!token || !role) throw new Error('setAuth: token+role required');
  const auth = { token, role, email: email || '', name: name || '' };
  localStorage.setItem(KEYS.AUTH, JSON.stringify(auth));
  // Legacy-Kompatibilität für bestehende Komponenten
  if (role === 'admin') {
    localStorage.setItem(KEYS.ADMIN_TOKEN, token);
  } else if (role === 'customer') {
    localStorage.setItem(KEYS.PORTAL_TOKEN, token);
    localStorage.setItem(KEYS.PORTAL_EMAIL, email || '');
    localStorage.setItem(KEYS.PORTAL_NAME, name || '');
  }
};

/** Entfernt ALLE Session-Keys & redirected — saubere Logout-Operation. */
export const logout = (redirectTo = '/login') => {
  ALL_KEYS.forEach((k) => localStorage.removeItem(k));
  // Hard-redirect: erzwingt React-Reset, kein Stale-State
  window.location.href = redirectTo;
};

/** Prüft ob ein Token aktuell vorhanden ist. */
export const isAuthed = () => !!getAuth();

/** Reiner Token-Getter für Authorization-Header. */
export const getToken = () => getAuth()?.token || '';

/** Standard Authorization-Header. */
export const authHeaders = () => {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
};

export const AUTH_KEYS = KEYS;
