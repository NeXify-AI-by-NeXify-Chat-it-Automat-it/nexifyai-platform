import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'http://localhost:8002';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

let _supabase = null;

export function getSupabase() {
  if (!_supabase) {
    _supabase = createClient(supabaseUrl, supabaseAnonKey);
  }
  return _supabase;
}

export async function signIn(email, password) {
  const sb = getSupabase();
  const { data, error } = await sb.auth.signInWithPassword({ email, password });
  if (error) return { error };
  if (!data?.session) return { error: { message: 'Login fehlgeschlagen' } };

  const role = data.session.user?.user_metadata?.role || data.session.user?.app_metadata?.role;
  if (role !== 'admin') {
    await sb.auth.signOut();
    return { error: { message: 'Kein Admin-Zugang. Nur Administratoren haben Zugriff auf das Cockpit.' } };
  }

  return { data, error: null };
}

export async function signOutUser() {
  const sb = getSupabase();
  await sb.auth.signOut();
  localStorage.removeItem('nx_admin_token');
  localStorage.removeItem('nx_auth');
}

export async function getAdminSession() {
  const sb = getSupabase();
  const { data: { session } } = await sb.auth.getSession();
  return session;
}
