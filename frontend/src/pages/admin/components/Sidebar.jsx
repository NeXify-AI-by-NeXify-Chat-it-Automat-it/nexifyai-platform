import React from 'react';

const I = ({ n, s = 20 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

const NAV_ITEMS = [
  { id: 'chat', label: 'Admin Chat', icon: 'chat' },
  { id: 'conversations', label: 'Konversationen', icon: 'forum' },
  { id: 'leads', label: 'Leads', icon: 'person_search' },
  { id: 'tasks', label: 'Tasks', icon: 'assignment' },
  { id: 'skills', label: 'Skills', icon: 'extension' },
  { id: 'brain', label: 'Brain', icon: 'psychology' },
  { id: 'legal', label: 'Legal', icon: 'gavel' },
];

export default function Sidebar({ open, onToggle, view, onViewChange, onLogout, userEmail }) {
  return (
    <aside className={`ac-sidebar ${open ? '' : 'ac-sidebar-closed'}`}>
      <button className="ac-sidebar-toggle" onClick={onToggle} title={open ? 'Einklappen' : 'Ausklappen'}>
        <I n={open ? 'chevron_left' : 'chevron_right'} s={16} />
      </button>

      {!open && (
        <div className="ac-sidebar-mini-brand">
          <I n="bolt" s={24} />
        </div>
      )}

      <nav className="ac-nav">
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            className={`ac-nav-item ${view === item.id ? 'ac-nav-active' : ''}`}
            onClick={() => onViewChange(item.id)}
            title={item.label}
          >
            <I n={item.icon} />
            {open && <span className="ac-nav-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      {open && userEmail && (
        <div className="ac-sidebar-user">{userEmail}</div>
      )}

      <button className="ac-logout-btn" onClick={onLogout} title="Abmelden">
        <I n="logout" />
        {open && <span>Abmelden</span>}
      </button>
    </aside>
  );
}
