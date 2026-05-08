import React, { useState } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

const COMMANDS = [
  {
    id: 'queue',
    label: 'Queue starten',
    icon: 'play_arrow',
    description: 'Admin-Task anlegen',
    action: async (setMessages) => {
      setMessages(prev => [...prev, { role: 'user', content: '🚀 /queue-start — Admin-Task wird angelegt...', timestamp: new Date().toISOString() }]);
      try {
        const task = await api.createTask({
          title: 'Admin-Cockpit Queue-Task',
          description: 'Manuell ausgelöster Task aus dem Admin-Cockpit',
          priority: 'high',
          source: 'admin-cockpit',
        });
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `✅ **Task angelegt**\n\nID: \`${task.id || task.task_id || '?'}\`\nStatus: waiting\nDer CLI-Autopilot wird den Task in Kürze aufnehmen.`,
          timestamp: new Date().toISOString(),
        }]);
      } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ Fehler: ${err.message}`, timestamp: new Date().toISOString() }]);
      }
    },
  },
  {
    id: 'health',
    label: 'Health prüfen',
    icon: 'monitor_heart',
    description: 'Live-Health-Score abrufen',
    action: async (setMessages) => {
      setMessages(prev => [...prev, { role: 'user', content: '🩺 /health-check — Health-Score wird abgerufen...', timestamp: new Date().toISOString() }]);
      try {
        const h = await api.getHealth();
        const items = [];
        if (h) {
          for (const [k, v] of Object.entries(h)) {
            if (typeof v !== 'object') items.push(`- **${k}:** ${v}`);
          }
          if (h.health_score !== undefined) items.unshift(`**Gesamt-Score: ${Math.round(h.health_score)}%**`);
        }
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `🩺 **System Health**\n\n${items.join('\n') || 'Keine Daten'}`,
          timestamp: new Date().toISOString(),
        }]);
      } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ Fehler: ${err.message}`, timestamp: new Date().toISOString() }]);
      }
    },
  },
  {
    id: 'commit',
    label: 'Letzter Commit',
    icon: 'commit',
    description: 'GitHub-Commit-Status',
    action: async (setMessages) => {
      setMessages(prev => [...prev, { role: 'user', content: '📝 /commit-status — Letzter Commit wird abgefragt...', timestamp: new Date().toISOString() }]);
      try {
        const c = await api.getLastCommit();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `📝 **Letzter Commit**\n\n- **SHA:** \`${c?.sha?.slice(0, 8) || '?'}\`\n- **Message:** ${c?.message || c?.commit?.message || '?'}\n- **Autor:** ${c?.author || c?.commit?.author?.name || '?'}\n- **Datum:** ${c?.date || c?.commit?.author?.date || '?'}`,
          timestamp: new Date().toISOString(),
        }]);
      } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ Fehler: ${err.message}`, timestamp: new Date().toISOString() }]);
      }
    },
  },
  {
    id: 'build',
    label: 'Build-Bericht',
    icon: 'build',
    description: 'Build- und Deploy-Status',
    action: async (setMessages) => {
      setMessages(prev => [...prev, { role: 'user', content: '🔨 /build-report — Build-Status wird abgefragt...', timestamp: new Date().toISOString() }]);
      try {
        const b = await api.getBuildReport();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `🔨 **Build-Bericht**\n\n- **Status:** ${b?.status || b?.build_status || '?'}\n- **Letztes Deployment:** ${b?.last_deploy || b?.deployed_at || '?'}\n- **Branch:** ${b?.branch || '?'}\n- **Commit:** \`${b?.commit?.slice(0, 8) || '?'}\``,
          timestamp: new Date().toISOString(),
        }]);
      } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ Fehler: ${err.message}`, timestamp: new Date().toISOString() }]);
      }
    },
  },
  {
    id: 'brain',
    label: 'Brain durchsuchen',
    icon: 'psychology',
    description: 'Semantische Brain-Suche',
    action: async (setMessages) => {
      const query = window.prompt('Brain-Suchbegriff:');
      if (!query) return;
      setMessages(prev => [...prev, { role: 'user', content: `🧠 /brain-search "${query}"`, timestamp: new Date().toISOString() }]);
      try {
        const results = await api.searchBrain(query);
        const items = Array.isArray(results) ? results.slice(0, 10) : (results?.results || []).slice(0, 10);
        if (items.length === 0) {
          setMessages(prev => [...prev, { role: 'assistant', content: `🧠 **Brain-Suche: "${query}"**\n\nKeine Ergebnisse gefunden.`, timestamp: new Date().toISOString() }]);
        } else {
          const lines = items.map((r, i) => `${i + 1}. **${r.title || r.key || `Eintrag ${i + 1}`}** — ${(r.content || r.text || '').slice(0, 120)}...`);
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: `🧠 **Brain-Suche: "${query}"**\n\n${lines.join('\n')}`,
            timestamp: new Date().toISOString(),
          }]);
        }
      } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ Fehler: ${err.message}`, timestamp: new Date().toISOString() }]);
      }
    },
  },
];

export default function CommandButtons({ setMessages }) {
  const [busy, setBusy] = useState(null);

  const handleCommand = async (cmd) => {
    setBusy(cmd.id);
    await cmd.action(setMessages);
    setBusy(null);
  };

  return (
    <div className="ac-commands">
      {COMMANDS.map(cmd => (
        <button
          key={cmd.id}
          className="ac-cmd-btn"
          onClick={() => handleCommand(cmd)}
          disabled={busy !== null}
          title={cmd.description}
        >
          <I n={cmd.icon} s={16} />
          <span>{cmd.label}</span>
        </button>
      ))}
    </div>
  );
}
