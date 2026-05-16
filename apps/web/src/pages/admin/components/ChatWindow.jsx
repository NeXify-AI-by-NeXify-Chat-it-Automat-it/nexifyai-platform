import React, { useState, useRef, useEffect } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

const SYSTEM_INTRO = {
  role: 'assistant',
  content: '🟢 **Admin Cockpit bereit.**\n\nIch bin dein KI-Steuer-Cockpit. Du kannst:\n- Aufträge erteilen → werden als Tasks angelegt und vom Autopilot ausgeführt\n- Nach Brain-Infos fragen → semantische Suche über alle Wissensquellen\n- Skills verwalten → aktivieren/deaktivieren/registrieren\n- Subagenten delegieren → Code-Review, Security-Audit, Dependency-Scan\n- Status abfragen → Health, Build, Commits, Incidents\n\n**Was soll ich tun?**',
  timestamp: new Date().toISOString(),
};

export default function ChatWindow({ activeConvo, setActiveConvo, messages, setMessages }) {
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [currentStream, setCurrentStream] = useState('');
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize with system intro
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([SYSTEM_INTRO]);
    }
  }, []);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStream]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || streaming) return;

    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setStreaming(true);
    setCurrentStream('');

    try {
      const token = localStorage.getItem('nx_admin_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || ''}/api/admin/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: text,
          conversation_id: activeConvo,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat API error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let newConvoId = activeConvo;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (!data) continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.conversation_id) newConvoId = parsed.conversation_id;
              if (parsed.content) {
                fullContent += parsed.content;
                setCurrentStream(fullContent);
              }
              if (parsed.done || parsed.content === '') {
                // Stream complete
              }
            } catch (e) {
              // Non-JSON line, skip
            }
          }
        }
      }

      if (fullContent) {
        const assistantMsg = { role: 'assistant', content: fullContent, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, assistantMsg]);
      }
      if (newConvoId && !activeConvo) setActiveConvo(newConvoId);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ **Fehler:** ${err.message}`,
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setStreaming(false);
      setCurrentStream('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="ac-chat">
      <div className="ac-chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`ac-chat-msg ${msg.role}`}>
            <div className="ac-chat-role">
              {msg.role === 'user' ? <I n="person" s={16} /> : <I n="bolt" s={16} />}
            </div>
            <div className="ac-chat-content">
              <Markdown text={msg.content} />
            </div>
          </div>
        ))}
        {streaming && currentStream && (
          <div className="ac-chat-msg assistant streaming">
            <div className="ac-chat-role"><I n="bolt" s={16} /></div>
            <div className="ac-chat-content">
              <Markdown text={currentStream} />
              <span className="ac-cursor">▌</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="ac-chat-input-area">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Auftrag an Hermes senden..."
          className="ac-chat-input"
          rows={2}
          disabled={streaming}
        />
        <button
          className="ac-chat-send"
          onClick={handleSend}
          disabled={!input.trim() || streaming}
        >
          <I n="send" s={20} />
        </button>
      </div>
    </div>
  );
}

// Simple markdown-like rendering
function Markdown({ text }) {
  if (!text) return null;
  const html = text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>')
    .replace(/^- (.+)$/gm, '• $1');
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
