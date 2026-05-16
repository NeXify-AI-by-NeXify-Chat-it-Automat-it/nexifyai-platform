// NeXifyAI Admin — MCP Tools View
// Displays configured MCP servers, their available tools, and execution UI

import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

function ToolCard({ tool, server, onExecute, executing }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="ac-mcp-tool" style={{
      background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.04)',
      borderRadius: 8,
      padding: '12px 16px',
      marginBottom: 6,
    }}>
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}
        onClick={() => setExpanded(!expanded)}
      >
        <I n={expanded ? 'expand_less' : 'expand_more'} s={16} />
        <span style={{ fontFamily: 'var(--f-mono, monospace)', fontSize: '0.85rem', fontWeight: 600, color: '#10b981' }}>
          {tool.name}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', flex: 1 }}>
          {tool.description?.slice(0, 80)}
        </span>
        <button
          className="ac-btn-primary ac-btn-xs"
          onClick={(e) => { e.stopPropagation(); onExecute(server, tool); }}
          disabled={executing}
          style={{ width: 'auto', padding: '4px 12px', fontSize: '0.7rem' }}
        >
          {executing ? '...' : 'Run'}
        </button>
      </div>
      {expanded && tool.schema?.properties && (
        <div style={{ marginTop: 8, paddingLeft: 24, fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)' }}>
          <div style={{ marginBottom: 4, fontWeight: 600, color: 'rgba(255,255,255,0.6)' }}>Parameters:</div>
          {Object.entries(tool.schema.properties).map(([key, val]) => (
            <div key={key} style={{ display: 'flex', gap: 8, marginBottom: 2 }}>
              <span style={{ fontFamily: 'var(--f-mono, monospace)', color: '#3b82f6' }}>{key}</span>
              <span style={{ color: 'rgba(255,255,255,0.3)' }}>{val.type || 'string'}</span>
              {tool.schema.required?.includes(key) && (
                <span style={{ color: '#ef4444' }}>*</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ServerCard({ server }) {
  const [tools, setTools] = useState([]);
  const [executing, setExecuting] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (server.tools) setTools(server.tools);
  }, [server.tools]);

  const handleExecute = async (srv, tool) => {
    setExecuting(tool.name);
    setResult(null);
    setError(null);

    try {
      const res = await api.callMCPTool(srv.name, tool.name, {});
      if (res?.success) {
        setResult(res);
      } else {
        setError(res?.error || 'Execution failed');
      }
    } catch (e) {
      setError(e.message || 'Request failed');
    } finally {
      setExecuting(null);
    }
  };

  return (
    <div className="ac-chart-card" style={{ marginBottom: 12 }}>
      <div className="ac-chart-header">
        <I n={server.connected ? 'cloud_done' : 'cloud_off'} s={16} />
        <span>{server.displayName}</span>
        <span className="ac-chart-sub" style={{ color: server.connected ? '#10b981' : '#ef4444' }}>
          {server.connected ? 'Connected' : 'Not configured'}
        </span>
      </div>
      {!server.connected && (
        <div style={{ padding: '16px', textAlign: 'center', color: 'rgba(255,255,255,0.3)', fontSize: '0.8rem' }}>
          <I n="settings" s={32} />
          <div style={{ marginTop: 8 }}>Set VERCEL_MCP_TOKEN env var to connect</div>
        </div>
      )}
      {server.connected && tools.length === 0 && (
        <div style={{ padding: '16px', textAlign: 'center', color: 'rgba(255,255,255,0.3)', fontSize: '0.8rem' }}>
          <I n="search" s={32} />
          <div style={{ marginTop: 8 }}>No tools loaded — connect to discover available tools</div>
        </div>
      )}
      {tools.length > 0 && (
        <div style={{ marginTop: 8 }}>
          {tools.map((tool) => (
            <ToolCard
              key={tool.name}
              tool={tool}
              server={server}
              onExecute={handleExecute}
              executing={executing === tool.name}
            />
          ))}
        </div>
      )}
      {result && (
        <div className="ac-mcp-result" style={{
          marginTop: 12, padding: 12,
          background: 'rgba(16,185,129,0.06)',
          border: '1px solid rgba(16,185,129,0.15)',
          borderRadius: 6, fontSize: '0.75rem',
          fontFamily: 'var(--f-mono, monospace)',
          whiteSpace: 'pre-wrap',
          maxHeight: 200, overflow: 'auto',
        }}>
          {JSON.stringify(result.content, null, 2)}
        </div>
      )}
      {error && (
        <div className="ac-mcp-error" style={{
          marginTop: 12, padding: 12,
          background: 'rgba(239,68,68,0.06)',
          border: '1px solid rgba(239,68,68,0.15)',
          borderRadius: 6, fontSize: '0.75rem',
          color: '#ef4444',
        }}>
          <I n="error" s={14} /> {error}
        </div>
      )}
    </div>
  );
}

export default function MCPToolsView() {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchServers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMCPServers();
      setServers(data?.servers || []);
    } catch (e) {
      setError(e.message || 'Failed to load MCP servers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  return (
    <div className="ac-view" style={{ flexDirection: 'column', padding: 20, overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <I n="power_settings_new" s={24} />
        <h2 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>MCP Tools</h2>
        <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.3)' }}>
          Model Context Protocol — AI Tool Integration
        </span>
        <button
          className="ac-btn-primary ac-btn-sm"
          onClick={fetchServers}
          disabled={loading}
          style={{ marginLeft: 'auto', width: 'auto' }}
        >
          <I n="refresh" s={14} /> Refresh
        </button>
      </div>

      {loading && (
        <div className="ac-chart-empty">
          <I n="sync" s={32} />
          <span>Loading MCP servers...</span>
        </div>
      )}

      {error && (
        <div className="ac-chart-empty" style={{ borderColor: 'rgba(239,68,68,0.2)' }}>
          <I n="error" s={32} />
          <span style={{ color: '#ef4444' }}>{error}</span>
          <button className="ac-btn-primary ac-btn-sm" onClick={fetchServers} style={{ width: 'auto' }}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && servers.length === 0 && (
        <div className="ac-chart-empty">
          <I n="power_off" s={32} />
          <span>No MCP servers configured</span>
        </div>
      )}

      {servers.map((server) => (
        <ServerCard key={server.name} server={server} />
      ))}
    </div>
  );
}
