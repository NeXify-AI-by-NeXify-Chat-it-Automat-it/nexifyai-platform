/**
 * Admin Cockpit API helper
 * All API calls go through Vercel proxy → VPS Backend
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function getToken() {
  return localStorage.getItem('nx_admin_token') ||
    (() => { try { return JSON.parse(localStorage.getItem('nx_auth') || '{}').token; } catch { return ''; } })();
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem('nx_admin_token');
    localStorage.removeItem('nx_auth');
    if (window.location.pathname !== '/admin/login') {
      window.location.href = '/admin/login';
    }
    throw new Error('Unauthorized');
  }

  return res;
}

export const api = {
  // Auth
  login: (email, password) =>
    apiFetch('/api/auth/admin-login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }).then(r => r.json()),

  // Dashboard
  getHealth: () => apiFetch('/api/autopilot/health').then(r => r.json()),
  getStats: () => apiFetch('/api/admin/stats').then(r => r.json()),
  getAgents: () => apiFetch('/api/admin/agents/status').then(r => r.json()),
  getIncidents: () => apiFetch('/api/admin/incidents?today=true').then(r => r.json()),

  // Workflow Badges
  getWorkflowStatus: () => apiFetch('/api/admin/workflow-status').then(r => r.json()),

  // Chat
  chatStream: function* () {}, // placeholder - handled via fetch directly for SSE

  // Conversations (existing)
  getConversations: () => apiFetch('/api/admin/nexify-ai/conversations').then(r => r.json()),
  getConversation: (id) => apiFetch(`/api/admin/nexify-ai/conversations/${id}`).then(r => r.json()),

  // Tasks
  getTasks: (limit = 50) => apiFetch(`/api/admin/tasks?limit=${limit}`).then(r => r.json()),
  createTask: (task) =>
    apiFetch('/api/admin/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    }).then(r => r.json()),
  updateTask: (id, updates) =>
    apiFetch(`/api/admin/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    }).then(r => r.json()),

  // Skills
  getSkills: () => apiFetch('/api/admin/skills').then(r => r.json()),
  toggleSkill: (name, active) =>
    apiFetch(`/api/admin/skills/${encodeURIComponent(name)}`, {
      method: 'PATCH',
      body: JSON.stringify({ active }),
    }).then(r => r.json()),

  // Brain
  searchBrain: (query) =>
    apiFetch(`/api/brain/search?q=${encodeURIComponent(query)}`).then(r => r.json()),

  // GitHub
  getLastCommit: () => apiFetch('/api/admin/github/last-commit').then(r => r.json()),

  // Build
  getBuildReport: () => apiFetch('/api/admin/build-report').then(r => r.json()),

  // Legacy admin endpoints (from existing Admin.js)
  getLeads: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/api/admin/leads?${qs}`).then(r => r.json());
  },
  getCustomers: (search = '') =>
    apiFetch(`/api/admin/customers?search=${encodeURIComponent(search)}`).then(r => r.json()),
  getQuotes: () => apiFetch('/api/admin/quotes').then(r => r.json()),
  getInvoices: () => apiFetch('/api/admin/invoices').then(r => r.json()),
  getCalendar: (month) => apiFetch(`/api/admin/calendar?month=${month}`).then(r => r.json()),
};
