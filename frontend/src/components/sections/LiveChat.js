import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { API, I, genSid, track, BrandName } from '../shared';

const formatTime = (ts) => {
  const d = new Date(ts);
  return d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
};

const LiveChat = ({ isOpen, onClose, initialQ, onBook, t, lang }) => {
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sid] = useState(() => genSid());
  const [qual, setQual] = useState({});
  const endRef = useRef(null);
  const inputRef = useRef(null);
  const lastInitialQ = useRef('');

  useEffect(() => {
    setMsgs([]);
    lastInitialQ.current = '';
  }, [lang]);

  useEffect(() => {
    if (isOpen && msgs.length === 0) {
      setMsgs([{ role: 'assistant', content: t.chat.welcome, ts: Date.now() }]);
      track('chat_started');
    }
  }, [isOpen, msgs.length, t.chat.welcome]);

  useEffect(() => {
    if (initialQ && isOpen && initialQ !== lastInitialQ.current) {
      lastInitialQ.current = initialQ;
      setTimeout(() => send(initialQ), 400);
    }
  }, [initialQ, isOpen]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);
  useEffect(() => {
    if (isOpen) { inputRef.current?.focus(); document.body.style.overflow = 'hidden'; }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const send = async (text = input) => {
    const txt = (typeof text === 'string' ? text : input).trim();
    if (!txt || loading) return;
    setMsgs(prev => [...prev, { role: 'user', content: txt, ts: Date.now() }]);
    setInput('');
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/chat/message`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid, message: txt, language: lang })
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Error');
      setMsgs(prev => [...prev, { role: 'assistant', content: d.message, ts: Date.now(), actions: d.actions }]);
      setQual(d.qualification || {});
      if (d.should_escalate) track('chat_escalation', { qual: d.qualification });
    } catch (_) {
      setMsgs(prev => [...prev, { role: 'assistant', content: t.contact.form.error, ts: Date.now() }]);
    } finally { setLoading(false); }
  };

  const onKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } };

  const aiLabel = { de: 'KI-Berater', nl: 'AI-Adviseur', en: 'AI Advisor' };
  const youLabel = { de: 'Sie', nl: 'U', en: 'You' };
  const newChatLabel = { de: 'Neue Unterhaltung', nl: 'Nieuw gesprek', en: 'New conversation' };
  const aiDisclaimer = {
    de: 'KI-gestützter Assistent. Keine rechtsverbindlichen Zusagen.',
    nl: 'AI-ondersteunde assistent. Geen juridisch bindende toezeggingen.',
    en: 'AI-powered assistant. No legally binding commitments.'
  };

  const handleNewChat = () => {
    setMsgs([{ role: 'assistant', content: t.chat.welcome, ts: Date.now() }]);
    setInput('');
    track('chat_new_conversation');
  };

  if (!isOpen) return null;

  return (
    <div className="chat-overlay" onClick={e => e.target === e.currentTarget && onClose()} role="dialog" aria-modal="true" aria-labelledby="chat-t" data-testid="chat-modal">
      <motion.div className="chat-modal" initial={{ opacity: 0, scale: 0.96, y: 16 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.35, ease: [0.25, 0.4, 0, 1] }}>

        {/* Mobile Header */}
        <div className="chat-mobile-header" data-testid="chat-mobile-header">
          <button className="chat-mobile-back" onClick={onClose} aria-label="Close" data-testid="chat-close-mobile">
            <I n="arrow_back" />
          </button>
          <div className="chat-mobile-brand">
            <img src="/icon-mark.svg" alt="" width="20" height="20" />
            <span className="chat-mobile-title">NeXify<span className="chat-accent">AI</span> {aiLabel[lang] || aiLabel.de}</span>
          </div>
          <div className="chat-mobile-status"><span className="status-dot on" /></div>
        </div>

        {/* Desktop Close */}
        <button className="chat-close-desktop" onClick={onClose} aria-label="Close" data-testid="chat-close">
          <I n="close" />
        </button>

        <div className="chat-layout">
          {/* Sidebar (Desktop only) */}
          <div className="chat-sidebar" data-testid="chat-sidebar">
            <div className="chat-sidebar-brand">
              <img src="/icon-mark.svg" alt="" width="24" height="24" />
              <div>
                <h2 id="chat-t" className="chat-sidebar-title">NeXify<span className="chat-accent">AI</span></h2>
                <span className="chat-sidebar-role">{t.chat.sidebarRole}</span>
              </div>
            </div>
            <div className="chat-sidebar-divider" />
            <p className="chat-sidebar-desc">{t.chat.sidebarDesc}</p>
            <div className="chat-presets" data-testid="chat-presets">
              {t.chat.presets.map((q, i) => (
                <button key={i} className="chat-preset" onClick={() => { track('preset_click', { q }); send(q); }} data-testid={`chat-preset-${i}`}>
                  <svg className="chat-preset-arrow" width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M1 7h10M8 3.5L11.5 7 8 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  <span>{q}</span>
                </button>
              ))}
            </div>
            <div className="chat-sidebar-divider" />
            <div className="chat-sidebar-cta">
              <button className="btn btn-primary btn-glow" onClick={() => { track('chat_offer_click'); send(lang === 'en' ? 'I would like to request a quote' : lang === 'nl' ? 'Ik wil graag een offerte aanvragen' : 'Ich möchte ein Angebot anfordern'); }} style={{ width: '100%' }} data-testid="chat-sidebar-offer-btn">
                <I n="description" /> {lang === 'en' ? 'Request Quote' : lang === 'nl' ? 'Offerte aanvragen' : 'Angebot anfordern'}
              </button>
              {onBook && <button className="btn btn-secondary" onClick={() => { track('chat_booking_fallback'); onBook(); }} style={{ width: '100%', marginTop: 8 }} data-testid="chat-sidebar-book-btn">
                <I n="calendar_month" /> {lang === 'en' ? 'Book Meeting' : lang === 'nl' ? 'Gesprek boeken' : 'Termin buchen'}
              </button>}
            </div>
            <button className="chat-new-btn" onClick={handleNewChat} data-testid="chat-new-conversation">
              <I n="refresh" /> {newChatLabel[lang] || newChatLabel.de}
            </button>
          </div>

          {/* Main Chat */}
          <div className="chat-main">
            <div className="chat-header" data-testid="chat-header">
              <div className="chat-header-left">
                <div className="chat-status"><span className="status-dot on" />{t.chat.status}</div>
              </div>
              <span className="chat-topic">{t.chat.topicLabel}</span>
            </div>

            <div className="chat-msgs" data-testid="chat-messages">
              {msgs.map((m, i) => (
                <motion.div key={i} className={`chat-msg ${m.role}`} data-testid={`chat-msg-${i}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
                  {m.role === 'assistant' && (
                    <div className="chat-msg-avatar" data-testid="chat-avatar">
                      <img src="/icon-mark.svg" alt="" width="18" height="18" />
                    </div>
                  )}
                  <div className="chat-msg-body">
                    <div className="chat-msg-meta">
                      <span className="chat-msg-sender">{m.role === 'assistant' ? (aiLabel[lang] || aiLabel.de) : (youLabel[lang] || youLabel.de)}</span>
                      <span className="chat-msg-time">{formatTime(m.ts)}</span>
                    </div>
                    {m.role === 'assistant' ? (
                      <div className="chat-md"><ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown></div>
                    ) : (
                      <div className="chat-msg-text">{m.content}</div>
                    )}
                    {m.actions && m.actions.length > 0 && (
                      <div className="chat-msg-actions">{m.actions.map((a, ai) => {
                        if (a.type === 'offer_generated') return <a key={ai} href={`${API}${a.pdf_url}`} target="_blank" rel="noreferrer" className="btn btn-sm btn-primary" data-testid="offer-pdf-download"><I n="picture_as_pdf" /> PDF-Angebot herunterladen</a>;
                        return <button key={ai} className="btn btn-sm btn-primary" onClick={() => send(t.booking.title)}><I n="event" /> {a.label}</button>;
                      })}</div>
                    )}
                  </div>
                </motion.div>
              ))}

              {loading && (
                <motion.div className="chat-msg assistant" initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}>
                  <div className="chat-msg-avatar"><img src="/icon-mark.svg" alt="" width="18" height="18" /></div>
                  <div className="chat-msg-body">
                    <div className="chat-msg-meta"><span className="chat-msg-sender">{aiLabel[lang] || aiLabel.de}</span></div>
                    <div className="chat-typing-wrap">
                      <div className="chat-typing"><span /><span /><span /></div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={endRef} />
            </div>

            {/* Input Area */}
            <div className="chat-input-area" data-testid="chat-input-area">
              <div className="chat-input-wrap">
                <input
                  ref={inputRef}
                  type="text"
                  className="chat-input"
                  placeholder={t.chat.placeholder}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={onKey}
                  disabled={loading}
                  aria-label="Message"
                  data-testid="chat-input"
                />
                <button className="chat-send" onClick={() => send()} disabled={!input.trim() || loading} aria-label="Send" data-testid="chat-send">
                  <I n="send" />
                </button>
              </div>
              <div className="chat-disclaimer" data-testid="chat-disclaimer">
                <I n="smart_toy" /> {aiDisclaimer[lang] || aiDisclaimer.de}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default LiveChat;
