import React, { useState, useEffect, useCallback } from 'react';
import { signIn, signOutUser, getAdminSession } from '../../lib/supabase';
import { api } from '../../lib/adminApi';
import Sidebar from './components/Sidebar';
import LiveDashboard from './components/LiveDashboard';
import ChatWindow from './components/ChatWindow';
import CommandButtons from './components/CommandButtons';
import ConversationsView from './components/ConversationsView';
import TasksView from './components/TasksView';
import SkillsView from './components/SkillsView';
import BrainView from './components/BrainView';
import WorkerPoolView from './components/WorkerPoolView';
import LegalView from './components/LegalView';
import LeadsView from './components/LeadsView';
import MCPToolsView from './components/MCPToolsView';
import './admin.css';

const I = ({ n, s = 20 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

export default function AdminCockpit() {
  // Auth
  const [session, setSession] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginErr, setLoginErr] = useState('');
  const [loginBusy, setLoginBusy] = useState(false);

  // Navigation
  const [view, setView] = useState(() => localStorage.getItem('nx_admin_view') || 'chat');
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const s = localStorage.getItem('nx_admin_sidebar_open');
    return s !== null ? s === 'true' : true;
  });

  // Chat
  const [activeConvo, setActiveConvo] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);

  // Dashboard data
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [agents, setAgents] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [workflows, setWorkflows] = useState({});

  // Auth Check
  useEffect(() => {
    (async () => {
      // Try Supabase session first
      const sess = await getAdminSession();
      if (sess?.user) {
        const role = sess.user.user_metadata?.role || sess.user.app_metadata?.role;
        if (role === 'admin') {
          localStorage.setItem('nx_admin_token', sess.access_token);
          localStorage.setItem('nx_auth', JSON.stringify({ role: 'admin', token: sess.access_token, email: sess.user.email, method: 'supabase' }));
          setSession(sess);
          setAuthChecked(true);
          return;
        }
      }
      // Check for existing backend token
      const legacyToken = localStorage.getItem('nx_admin_token');
      if (legacyToken) {
        try {
          const auth = JSON.parse(localStorage.getItem('nx_auth') || '{}');
          if (auth.role === 'admin') {
            setSession({ user: { email: auth.email }, access_token: legacyToken });
            setAuthChecked(true);
            return;
          }
        } catch {}
      }
      setAuthChecked(true);
    })();
  }, []);

  // Login Handler - tries Supabase first, falls back to backend
  const handleLogin = async (e) => {
    e.preventDefault();
    if (loginBusy) return;
    setLoginBusy(true);
    setLoginErr('');

    // Try Supabase first
    const { data: sbData, error: sbError } = await signIn(loginEmail, loginPassword);
    if (!sbError && sbData?.session) {
      localStorage.setItem('nx_admin_token', sbData.session.access_token);
      localStorage.setItem('nx_auth', JSON.stringify({ role: 'admin', token: sbData.session.access_token, email: sbData.session.user.email, method: 'supabase' }));
      setSession(sbData.session);
      setLoginBusy(false);
      return;
    }

    // Fallback: Backend login
    try {
      const backendResult = await api.login(loginEmail, loginPassword);
      if (backendResult?.access_token || backendResult?.token) {
        const token = backendResult.access_token || backendResult.token;
        localStorage.setItem('nx_admin_token', token);
        localStorage.setItem('nx_auth', JSON.stringify({ role: 'admin', token, email: loginEmail, method: 'backend' }));
        setSession({ user: { email: loginEmail }, access_token: token });
        setLoginBusy(false);
        return;
      }
      setLoginErr(backendResult?.detail || 'Login fehlgeschlagen');
    } catch (err) {
      setLoginErr(sbError?.message || 'Login fehlgeschlagen. Bitte E-Mail und Passwort prüfen.');
    }
    setLoginBusy(false);
  };

  // Logout
  const handleLogout = async () => {
    await signOutUser();
    setSession(null);
    setHealth(null);
    setStats(null);
    setChatMessages([]);
  };

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => {
      const next = !prev;
      localStorage.setItem('nx_admin_sidebar_open', String(next));
      return next;
    });
  }, []);

  const changeView = useCallback((v) => {
    setView(v);
    localStorage.setItem('nx_admin_view', v);
  }, []);

  // Dashboard Polling (30s)
  useEffect(() => {
    if (!session) return;
    const poll = async () => {
      try {
        const [h, s, a, i, w] = await Promise.allSettled([
          api.getHealth().catch(() => null),
          api.getStats().catch(() => null),
          api.getAgents().catch(() => []),
          api.getIncidents().catch(() => []),
          api.getWorkflowStatus().catch(() => ({})),
        ]);
        if (h.status === 'fulfilled' && h.value) setHealth(h.value);
        if (s.status === 'fulfilled' && s.value) setStats(s.value);
        if (a.status === 'fulfilled') setAgents(a.value?.agents || a.value || []);
        if (i.status === 'fulfilled') setIncidents(i.value?.incidents || i.value || []);
        if (w.status === 'fulfilled') setWorkflows(w.value?.workflows || w.value || {});
      } catch {}
    };
    poll();
    const interval = setInterval(poll, 30000);
    return () => clearInterval(interval);
  }, [session]);

  // Login Screen
  if (!authChecked) {
    return (
      <div className="ac-loading">
        <div className="ac-loading-spinner" />
        <p>Prüfe Authentifizierung...</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="ac-login-page">
        <div className="ac-login-card">
          <div className="ac-login-brand">
            <I n="bolt" s={36} />
            <h1><span>NeXify</span><em>AI</em></h1>
          </div>
          <p className="ac-login-sub">Admin Cockpit — Nur für Administratoren</p>
          <form onSubmit={handleLogin} className="ac-login-form">
            <input
              type="email"
              value={loginEmail}
              onChange={e => setLoginEmail(e.target.value)}
              placeholder="admin@nexifyai.de"
              className="ac-input"
              required
              autoFocus
            />
            <input
              type="password"
              value={loginPassword}
              onChange={e => setLoginPassword(e.target.value)}
              placeholder="Passwort"
              className="ac-input"
              required
            />
            {loginErr && <div className="ac-error">{loginErr}</div>}
            <button type="submit" className="ac-btn-primary" disabled={loginBusy}>
              {loginBusy ? 'Anmelden...' : 'Anmelden'}
            </button>
          </form>
          <p className="ac-login-footer">NeXifyAI by NeXify — Chat it. Automate it.</p>
        </div>
      </div>
    );
  }

  // Main Cockpit
  return (
    <div className={`ac-layout ${sidebarOpen ? '' : 'ac-collapsed'}`}>
      <Sidebar
        open={sidebarOpen}
        onToggle={toggleSidebar}
        view={view}
        onViewChange={changeView}
        onLogout={handleLogout}
        userEmail={session.user?.email}
      />

      <div className="ac-main">
        <div className="ac-topbar">
          <div className="ac-topbar-brand">
            <I n="bolt" s={20} />
            <span>NeXify<em>AI</em></span>
          </div>
          <div className="ac-topbar-title">
            {view === 'chat' && 'Admin Chat'}
            {view === 'conversations' && 'Konversationen'}
            {view === 'tasks' && 'Tasks'}
            {view === 'skills' && 'Skills'}
            {view === 'mcp' && 'MCP Tools'}
            {view === 'workers' && 'Worker Pool'}
            {view === 'brain' && 'Brain'}
            {view === 'leads' && 'Leads'}
            {view === 'legal' && 'Legal'}
          </div>
          <div className="ac-topbar-user">{session.user?.email}</div>
        </div>

        <div className="ac-content">
          {view === 'chat' && (
            <LiveDashboard
              health={health}
              stats={stats}
              agents={agents}
              incidents={incidents}
              workflows={workflows}
            />
          )}

          {view === 'chat' && (
            <ChatWindow
              activeConvo={activeConvo}
              setActiveConvo={setActiveConvo}
              messages={chatMessages}
              setMessages={setChatMessages}
            />
          )}

          {view === 'chat' && <CommandButtons setMessages={setChatMessages} />}

          {view === 'conversations' && <ConversationsView />}
          {view === 'tasks' && <TasksView />}
          {view === 'skills' && <SkillsView />}
          {view === 'brain' && <BrainView />}
          {view === 'mcp' && <MCPToolsView />}
          {view === 'leads' && <LeadsView />}
          {view === 'legal' && <LegalView />}
        </div>
      </div>
    </div>
  );
}
