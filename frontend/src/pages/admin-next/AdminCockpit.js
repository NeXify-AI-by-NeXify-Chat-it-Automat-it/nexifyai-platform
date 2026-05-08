/**
 * AdminCockpit v2 — Neues Admin-Panel
 * Features: Supabase Auth, LiveDashboard, ChatWindow, CommandButtons
 * Lazy-loadable, fällt auf alte Admin.js zurück bei Fehlern
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

const API = process.env.REACT_APP_BACKEND_URL || '';

let supabase = null;
const getSupabase = () => {
  if (!supabase) {
    const url = process.env.REACT_APP_SUPABASE_URL || 'https://www.nexify-automate.com/api';
    const key = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiJ9.demo';
    supabase = createClient(url, key);
  }
  return supabase;
};

const I = ({ n, c }) => (
  <span className={`material-symbols-outlined ${c || ''}`} style={{ fontSize: 'inherit' }}>{n}</span>
);

// ── Auth ──────────────────────────────────────────────────────────────
const getAdminSession = async () => {
  // 1) Backend JWT from localStorage (primary — works with all backend endpoints)
  try {
    const storedAuth = JSON.parse(localStorage.getItem('nx_auth') || '{}');
    if (storedAuth.token && storedAuth.role === 'admin') {
      const res = await fetch(`${API}/api/admin/stats`, {
        headers: { 'Authorization': `Bearer ${storedAuth.token}` },
      });
      if (res.ok) {
        return { token: storedAuth.token, email: storedAuth.email, role: 'admin' };
      }
    }
  } catch (e) { /* fallback */ }

  // 2) Supabase session fallback
  try {
    const sb = getSupabase();
    const { data: { session }, error } = await sb.auth.getSession();
    if (!error && session?.user?.email) {
      const res = await fetch(`${API}/api/auth/check-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.access_token}` },
        body: JSON.stringify({ email: session.user.email }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.role === 'admin' || data.role === 'dual') {
          return { token: session.access_token, email: session.user.email, role: 'admin' };
        }
      }
    }
  } catch (e) { /* fallback */ }

  return null;
};

// ── Dashboard Card ────────────────────────────────────────────────────
const DashboardCard = ({ icon, label, value, color }) => (
  <div style={{
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: '12px', padding: '16px',
    display: 'flex', flexDirection: 'column', gap: '4px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <I n={icon} />
      <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', fontWeight: 500 }}>{label}</span>
    </div>
    <span style={{ fontSize: '1.5rem', fontWeight: 700, color, fontFamily: 'var(--f-mono)' }}>
      {value}
    </span>
  </div>
);

// ── Live Dashboard ─────────────────────────────────────────────────────
const LiveDashboard = ({ stats, health }) => (
  <div style={{
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '12px', padding: '16px 20px',
  }}>
    <DashboardCard icon="people" label="Leads" value={stats?.leads_total || 0} color="#3b82f6" />
    <DashboardCard icon="trending_up" label="Neu (7d)" value={stats?.leads_new || 0} color="#10b981" />
    <DashboardCard icon="description" label="Angebote" value={stats?.quotes_total || 0} color="#f59e0b" />
    <DashboardCard icon="gavel" label="Verträge" value={stats?.contracts_total || 0} color="#8b5cf6" />
    <DashboardCard icon="receipt_long" label="Rechnungen" value={stats?.invoices_total || 0} color="#ef4444" />
    <DashboardCard icon="forum" label="Chats" value={stats?.chat_sessions || 0} color="#06b6d4" />
    {health && (
      <DashboardCard
        icon="monitor_heart" label="Health"
        value={health.status || 'OK'}
        color={health.status === 'OK' ? '#10b981' : '#ef4444'}
      />
    )}
  </div>
);

// ── Command Buttons ────────────────────────────────────────────────────
const COMMANDS = [
  { label: 'System Status', prompt: 'Zeige den aktuellen System-Status: Health-Score, alle Services, CPU/RAM/Disk.', icon: 'monitor_heart', color: '#10b981' },
  { label: 'Offene Tasks', prompt: 'Liste alle offenen Tasks und deren Status.', icon: 'checklist', color: '#3b82f6' },
  { label: 'Letzte Leads', prompt: 'Zeige die 5 neuesten Leads mit Status.', icon: 'person_add', color: '#f59e0b' },
  { label: 'Deployments', prompt: 'Zeige die letzten Vercel-Deployments und deren Status.', icon: 'rocket_launch', color: '#8b5cf6' },
  { label: 'Fehler-Analyse', prompt: 'Analysiere die letzten Backend-Fehler aus den Logs.', icon: 'bug_report', color: '#ef4444' },
  { label: 'Health Check', prompt: 'Führe einen kompletten System-Health-Check durch.', icon: 'health_and_safety', color: '#06b6d4' },
];

const CommandButtons = ({ onCommand, disabled }) => (
  <div style={{
    display: 'flex', gap: '8px', padding: '12px 20px', overflowX: 'auto',
    borderBottom: '1px solid rgba(255,255,255,0.06)', flexWrap: 'wrap',
  }}>
    {COMMANDS.map(cmd => (
      <button key={cmd.label} onClick={() => onCommand(cmd.prompt)} disabled={disabled}
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          padding: '8px 16px', borderRadius: '20px',
          border: `1px solid ${cmd.color}22`, background: `${cmd.color}0a`,
          color: cmd.color, fontSize: '0.8rem', fontWeight: 500,
          cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.5 : 1,
          transition: 'all 200ms', whiteSpace: 'nowrap',
        }}>
        <I n={cmd.icon} /> {cmd.label}
      </button>
    ))}
  </div>
);

// ── Simple Chat Markdown ─────────────────────────────────────────────
const ChatMarkdown = ({ text }) => {
  if (!text) return null;
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    const lines = part.split('\n');
    return lines.map((line, j) => (
      <React.Fragment key={`${i}-${j}`}>
        {line}{j < lines.length - 1 && <br />}
      </React.Fragment>
    ));
  });
};

// ── Chat Window ────────────────────────────────────────────────────────
const ChatWindow = ({ session, inputVal, onInputChange, streaming, onStreamingChange, stats, health }) => {
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState('');
  const messagesEnd = useRef(null);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // Welcome message
  useEffect(() => {
    if (messages.length === 0 && session) {
      setMessages([{
        role: 'assistant',
        content: `Willkommen im **Admin Cockpit v2**, Pascal! 🚀\n\nDas System ist bereit. Command-Buttons für Schnellzugriffe oder direkter Chat.\n\n**System:** ${stats?.leads_total || 0} Leads | ${stats?.quotes_total || 0} Angebote | Health: ${health?.status || 'OK'}`,
        timestamp: new Date().toISOString(),
      }]);
    }
  }, [session]);

  const sendMessage = useCallback(async (text) => {
    const msg = (text || inputVal).trim();
    if (!msg || streaming || !session?.token) return;

    setError('');
    if (onInputChange) onInputChange('');
    onStreamingChange(true);

    const userMsg = { role: 'user', content: msg, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);

    try {
      // Nutze Public Chat Endpoint im Advisor-Mode (OpenRouter direkt, kein Gateway nötig)
      const res = await fetch(`${API}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`,
        },
        body: JSON.stringify({
          session_id: conversationId || `acp_${Date.now()}`,
          message: msg,
          language: 'de',
          mode: 'advisor',
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        throw new Error(err.detail || `Fehler ${res.status}`);
      }

      const data = await res.json();
      const reply = data.message || data.response || '';

      if (reply) {
        if (data.conversation_id && !conversationId) setConversationId(data.conversation_id);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: reply,
          timestamp: new Date().toISOString(),
          conversation_id: data.conversation_id,
        }]);
      }
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        role: 'assistant', content: `❌ **Fehler:** ${err.message}`,
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      onStreamingChange(false);
    }
  }, [inputVal, streaming, session, messages, conversationId, onInputChange, onStreamingChange]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: '400px' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            display: 'flex', gap: '10px', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%',
          }}>
            {m.role === 'assistant' && (
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg,#FE9B7B,#f59e0b)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, flexShrink: 0, marginTop: 4 }}>🤖</div>
            )}
            <div style={{
              background: m.role === 'user' ? 'linear-gradient(135deg,#FE9B7B,#f59e0b)' : 'rgba(255,255,255,0.05)',
              border: m.role === 'user' ? 'none' : '1px solid rgba(255,255,255,0.08)',
              borderRadius: 12, padding: '12px 16px',
              color: m.role === 'user' ? '#080c12' : 'rgba(255,255,255,0.9)',
              fontSize: '0.875rem', lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word',
            }}>
              <ChatMarkdown text={m.content} />
            </div>
            {m.role === 'user' && (
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, flexShrink: 0, marginTop: 4 }}>
                <I n="person" />
              </div>
            )}
          </div>
        ))}
        {streaming && <div style={{ alignSelf: 'flex-start', color: '#FE9B7B', fontSize: '0.75rem' }}>Schreibt...</div>}
        {error && (
          <div style={{ alignSelf: 'center', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, padding: '8px 16px', color: '#ef4444', fontSize: '0.8rem' }}>
            {error}
            <button onClick={() => setError('')} style={{ marginLeft: 8, background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>✕</button>
          </div>
        )}
        <div ref={messagesEnd} />
      </div>
      <div style={{ padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
        <textarea
          value={inputVal}
          onChange={e => onInputChange && onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Nachricht an Admin AI..."
          rows={1}
          disabled={streaming}
          style={{ flex: 1, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, padding: '12px 16px', color: '#fff', fontSize: '0.875rem', resize: 'none', outline: 'none', fontFamily: 'inherit' }}
        />
        <button onClick={() => sendMessage()} disabled={!inputVal?.trim() || streaming}
          style={{ width: 44, height: 44, borderRadius: 10, background: inputVal?.trim() && !streaming ? 'linear-gradient(135deg,#FE9B7B,#f59e0b)' : 'rgba(255,255,255,0.06)', border: 'none', color: inputVal?.trim() && !streaming ? '#080c12' : 'rgba(255,255,255,0.3)', cursor: inputVal?.trim() && !streaming ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <I n="send" />
        </button>
      </div>
    </div>
  );
};

// ── Toolbar: Fabrik-Button + Admin-Chat ────────────────────────────────
const AppToolbar = ({ token }) => {
  const switchTo = (url) => {
    // Pass auth token as hash parameter (never in query string)
    const encodedToken = btoa(token || '');
    window.open(`${url}#nx_token=${encodedToken}`, '_blank', 'noopener');
  };

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '8px',
      padding: '8px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)',
      background: 'rgba(255,255,255,0.015)',
    }}>
      <button onClick={() => switchTo('https://ai-farbrik.nexifyai.cloud')}
        title="KI-Fabrik (Paperclip) — Task-Verwaltung und autonome Worker"
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          padding: '6px 14px', borderRadius: '8px',
          background: 'rgba(254,155,123,0.1)', border: '1px solid rgba(254,155,123,0.25)',
          color: '#FE9B7B', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
          transition: 'all 0.2s',
        }}
      >
        <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>precision_manufacturing</span>
        KI-Fabrik
      </button>
      <button onClick={() => switchTo('https://admin.nexifyai.cloud')}
        title="Admin-Chat — Direkter Zugriff auf NeXifyAI"
        style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          padding: '6px 14px', borderRadius: '8px',
          background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
          color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer',
          transition: 'all 0.2s',
        }}
      >
        <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>chat</span>
        Admin-Chat
      </button>
    </div>
  );
};

// ── MAIN: AdminCockpit ──────────────────────────────────────────────────
const AdminCockpit = ({ onFallback }) => {
  const [session, setSession] = useState(null);
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState('');
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);

  useEffect(() => {
    document.body.classList.add('hide-wa');
    return () => document.body.classList.remove('hide-wa');
  }, []);

  useEffect(() => {
    getAdminSession().then(s => {
      if (s) {
        setSession(s);
        loadStats(s.token);
        loadHealth(s.token);
      } else {
        setAuthError('Nicht authentifiziert. Leite zum Login weiter...');
        setTimeout(() => { window.location.href = '/login'; }, 1500);
      }
      setLoading(false);
    }).catch(() => {
      setLoading(false);
      if (onFallback) onFallback();
    });
  }, []);

  const loadStats = async (token) => {
    try {
      const res = await fetch(`${API}/api/admin/stats`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setStats(await res.json());
    } catch (e) { /* silent */ }
  };

  const loadHealth = async (token) => {
    try {
      const res = await fetch(`${API}/api/admin/audit/health`, { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setHealth(await res.json());
    } catch (e) { /* silent */ }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: '#080c12', color: 'rgba(255,255,255,0.5)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: 16 }}>🚀</div>
          <div>Admin Cockpit v2 wird geladen...</div>
        </div>
      </div>
    );
  }

  if (authError) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: '#080c12', color: 'rgba(255,255,255,0.5)', flexDirection: 'column', gap: 12 }}>
        <span>{authError}</span>
        <button onClick={() => window.location.href = '/login'} style={{ padding: '10px 24px', borderRadius: 8, background: 'linear-gradient(135deg,#FE9B7B,#f59e0b)', border: 'none', color: '#080c12', fontWeight: 600, cursor: 'pointer' }}>
          Zum Login
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#080c12', color: '#fff', fontFamily: 'var(--f-sans), -apple-system, BlinkMacSystemFont, sans-serif' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,255,255,0.02)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <img src="/nexifyai-logo-light.png" alt="NeXifyAI" height="22" />
          <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', fontWeight: 500 }}>Admin Cockpit v2</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.8rem' }}>
          <span style={{ color: 'rgba(255,255,255,0.4)' }}>{session?.email}</span>
          <button onClick={() => { localStorage.clear(); window.location.href = '/login'; }}
            style={{ padding: '6px 12px', borderRadius: 6, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', cursor: 'pointer' }}>
            <I n="logout" /> Logout
          </button>
        </div>
      </header>
      <AppToolbar token={session?.token} />
      <LiveDashboard stats={stats} health={health} />
      <CommandButtons onCommand={(prompt) => setInput(prompt)} disabled={streaming} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <ChatWindow
          session={session} stats={stats} health={health}
          inputVal={input} onInputChange={setInput}
          streaming={streaming} onStreamingChange={setStreaming}
        />
      </div>
    </div>
  );
};

export { AdminCockpit, getAdminSession };
export default AdminCockpit;
