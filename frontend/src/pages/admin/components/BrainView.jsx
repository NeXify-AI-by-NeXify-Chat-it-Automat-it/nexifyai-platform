import React, { useState } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

export default function BrainView() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(false);

  const search = async (e) => {
    e.preventDefault();
    if (!query.trim() || searching) return;
    setSearching(true);
    try {
      const d = await api.searchBrain(query);
      setResults(Array.isArray(d) ? d : (d?.results || d?.matches || []));
      setSearched(true);
    } catch (err) {
      setResults([{ title: 'Fehler', content: err.message }]);
      setSearched(true);
    }
    setSearching(false);
  };

  return (
    <div className="ac-view" style={{ padding: '24px', overflow: 'auto', flexDirection: 'column' }}>
      <h3>Brain durchsuchen</h3>
      <form onSubmit={search} className="ac-search-form">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Semantische Suche über alle Brain-Einträge..."
          className="ac-input ac-search-input"
          autoFocus
        />
        <button type="submit" className="ac-btn-primary" disabled={searching || !query.trim()}>
          <I n="search" s={16} /> {searching ? 'Suche...' : 'Suchen'}
        </button>
      </form>
      {searched && (
        <div className="ac-results">
          {results.length === 0 ? (
            <p className="ac-empty">Keine Ergebnisse für "{query}"</p>
          ) : (
            results.map((r, i) => (
              <div key={i} className="ac-result-card">
                <div className="ac-result-title">{r.title || r.key || r.id || `Ergebnis ${i + 1}`}</div>
                <div className="ac-result-content">{(r.content || r.text || r.description || '').slice(0, 300)}</div>
                {r.score !== undefined && <div className="ac-result-score">Score: {(r.score * 100).toFixed(1)}%</div>}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
