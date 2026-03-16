import React, { useState, useRef, useEffect } from 'react';
import api from '../utils/api';
import './ChatbotPage.css';

const SUGGESTED = [
  'What does my EEG analysis indicate?',
  'Explain the Alpha band results',
  'What are the stress indicators?',
  'How does my brain activity compare to normal?',
  'Suggest relaxation techniques based on my data',
  'What is the confidence level of the prediction?',
];

export default function ChatbotPage() {
  const [uploadId, setUploadId] = useState('');
  const [idSet, setIdSet] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: 'Hello! I\'m your NeuroShield AI assistant. Enter your **Upload ID** above and I\'ll answer questions about your EEG analysis — predictions, band power, stress indicators, and more.',
      time: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef();
  const inputRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const setId = () => {
    if (!uploadId.trim()) { setError('Enter a valid upload ID'); return; }
    setIdSet(true);
    setError('');
    setMessages(prev => [...prev, {
      role: 'bot',
      text: `Context set for Upload ID **${uploadId}**. You can now ask me anything about this EEG session!`,
      time: new Date(),
    }]);
  };

  const sendMessage = async (text) => {
    const question = text || input.trim();
    if (!question) return;
    if (!idSet && !uploadId) { setError('Please set an upload ID first.'); return; }
    setError('');
    setInput('');

    const userMsg = { role: 'user', text: question, time: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setSending(true);

    try {
      const data = await api.chat(uploadId || '0', question);
      const answer = data.answer || data.response || data.message || JSON.stringify(data);
      setMessages(prev => [...prev, { role: 'bot', text: answer, time: new Date() }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: '⚠️ Could not reach the backend. Make sure the Django server is running on port 8000.',
        time: new Date(),
        isError: true,
      }]);
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  const formatTime = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const renderText = (text) =>
    text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>');

  return (
    <div className="chat-page">
      {/* Top bar */}
      <div className="chat-topbar">
        <div className="chat-agent-info">
          <div className="chat-avatar">
            <span>AI</span>
            <div className="chat-online" />
          </div>
          <div>
            <div className="chat-agent-name">NeuroShield AI</div>
            <div className="chat-agent-status">
              <div className="pulse-dot" style={{ width: 6, height: 6 }} />
              <span>Online · EEG Context Ready</span>
            </div>
          </div>
        </div>

        <div className="chat-id-row">
          <input
            className="input"
            placeholder="Upload ID"
            value={uploadId}
            onChange={e => { setUploadId(e.target.value); setIdSet(false); }}
            onKeyDown={e => e.key === 'Enter' && setId()}
            style={{ width: 140 }}
          />
          <button className={`btn ${idSet ? 'btn-accent' : 'btn-primary'}`} onClick={setId} style={{ padding: '10px 18px', fontSize: 13 }}>
            {idSet ? '✓ Set' : 'Set ID'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ margin: '0 16px' }}>{error}</div>}

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg-wrap ${msg.role}`}>
            {msg.role === 'bot' && (
              <div className="msg-avatar bot-avatar">AI</div>
            )}
            <div className={`chat-bubble ${msg.role} ${msg.isError ? 'bubble-error' : ''}`}>
              <div
                className="bubble-text"
                dangerouslySetInnerHTML={{ __html: renderText(msg.text) }}
              />
              <div className="bubble-time">{formatTime(msg.time)}</div>
            </div>
            {msg.role === 'user' && (
              <div className="msg-avatar user-avatar">U</div>
            )}
          </div>
        ))}

        {sending && (
          <div className="chat-msg-wrap bot">
            <div className="msg-avatar bot-avatar">AI</div>
            <div className="chat-bubble bot typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 2 && (
        <div className="chat-suggestions">
          {SUGGESTED.map(s => (
            <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="chat-input-bar">
        <input
          ref={inputRef}
          className="input chat-input"
          placeholder="Ask about your EEG data…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          disabled={sending}
        />
        <button
          className="btn btn-primary chat-send"
          onClick={() => sendMessage()}
          disabled={sending || !input.trim()}
        >
          {sending ? <div className="spinner" /> : '→'}
        </button>
      </div>
    </div>
  );
}
