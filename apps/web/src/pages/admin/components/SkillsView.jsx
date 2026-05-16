import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

export default function SkillsView() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null);

  useEffect(() => {
    api.getSkills().then(d => {
      setSkills(d?.skills || d || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const toggle = async (skill) => {
    const name = skill.name || skill.id || skill;
    setToggling(name);
    try {
      await api.toggleSkill(name, !skill.active);
      setSkills(prev => prev.map(s => {
        const sn = s.name || s.id || s;
        if (sn === name) return { ...s, active: !s.active };
        return s;
      }));
    } catch (err) {
      alert('Fehler: ' + err.message);
    }
    setToggling(null);
  };

  if (loading) return <div className="ac-loading"><div className="ac-loading-spinner" /><p>Lade Skills...</p></div>;

  return (
    <div className="ac-view" style={{ padding: '24px', overflow: 'auto' }}>
      <h3>Skills ({skills.length})</h3>
      <div className="ac-skill-grid">
        {skills.map((s, i) => {
          const name = s.name || s.id || s;
          const desc = s.description || s.desc || '';
          const active = s.active !== false;
          return (
            <div key={i} className={`ac-skill-card ${active ? '' : 'ac-skill-inactive'}`}>
              <div className="ac-skill-header">
                <span className="ac-skill-name">{name}</span>
                <button
                  onClick={() => toggle({ name, active })}
                  disabled={toggling === name}
                  className={`ac-toggle ${active ? 'ac-toggle-on' : ''}`}
                >
                  {toggling === name ? '...' : (active ? 'ON' : 'OFF')}
                </button>
              </div>
              {desc && <p className="ac-skill-desc">{desc.slice(0, 120)}</p>}
            </div>
          );
        })}
        {skills.length === 0 && <p className="ac-empty">Keine Skills geladen</p>}
      </div>
    </div>
  );
}
