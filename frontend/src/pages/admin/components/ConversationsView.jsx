import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

export default function ConversationsView() {
  const [conversations, setConversations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [reply, setReply] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getConversations().then(d => {
      setConversations(d?.conversations || d || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const loadConvo = async (id) => {
    setSelected(null);
    const d = await api.getConversation(id);
    setSelected(d);
  };

  const sendReply = async () => {
    if (!reply.trim() || busy) return;
    setBusy(true);
    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL || ''}/api/admin/conversations/${selected.conversation_id}/reply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('nx_admin_token')}`,
        },
        body: JSON.stringify({ message: reply }),
      });
      setReply('');
      loadConvo(selected.conversation_id);
    } catch (e) {
      alert('Fehler: ' + e.message);
    }
    setBusy(false);
  };

  if (loading) return <div className="ac-loading"><div className="ac-loading-spinner" /><p>Lade...</p></div>;

  return (
    <div className="ac-view">
      <div className="ac-view-list">
        <h3>Konversationen ({conversations.length})</h3>
        <div className="ac-list">
          {conversations.map(c => (
            <div
              key={c.conversation_id || c.id}
              className={`ac-list-item ${selected?.conversation_id === (c.conversation_id || c.id) ? 'ac-list-active' : ''}`}
              onClick={() => loadConvo(c.conversation_id || c.id)}
            >
              <div className="ac-list-item-title">{c.subject || c.title || 'Ohne Titel'}</div>
              <div className="ac-list-item-sub">{c.platform || c.channel || '?'} • {c.updated_at ? new Date(c.updated_at).toLocaleDateString('de-DE') : ''}</div>
            </div>
          ))}
          {conversations.length === 0 && <p className="ac-empty">Keine Konversationen</p>}
        </div>
      </div>
      {selected && (
        <div className="ac-view-detail">
          <h3>Konversation {selected.conversation_id?.slice(0, 12)}</h3>
          <div className="ac-messages">
            {(selected.messages || []).map((m, i) => (
              <div key={i} className={`ac-msg ${m.role}`}>
                <strong>{m.role === 'user' ? '👤' : '🤖'}</strong> {m.content}
              </div>
            ))}
          </div>
          <div className="ac-reply-area">
            <input
              value={reply}
              onChange={e => setReply(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') sendReply(); }}
              placeholder="Antwort..."
              className="ac-input"
            />
            <button onClick={sendReply} disabled={busy} className="ac-btn-primary ac-btn-sm">
              <I n="send" s={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
