import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header.jsx';
import Sidebar from './components/Sidebar.jsx';
import WelcomeCards from './components/WelcomeCards.jsx';
import ChatMessage from './components/ChatMessage.jsx';
import SettingsModal from './components/SettingsModal.jsx';
import { Send, Sparkles, AlertTriangle, Key } from 'lucide-react';

export default function App() {
  // Theme state
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('hr_dark_mode');
    if (saved !== null) return saved === 'true';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Backend state
  const [status, setStatus] = useState(null);
  const [categories, setCategories] = useState(['All']);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [reindexing, setReindexing] = useState(false);

  // Settings
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settings, setSettings] = useState(() => {
    return {
      apiKey: localStorage.getItem('hr_api_key') || '',
      model: 'llama-3.3-70b-versatile',
      top_k: 5,
      sim_threshold: 0.35
    };
  });

  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Apply dark mode to <html>
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('hr_dark_mode', darkMode);
  }, [darkMode]);

  // Fetch initial system status
  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
        if (data.categories) setCategories(data.categories);
        if (data.default_model) {
          setSettings((prev) => ({ ...prev, model: prev.model || data.default_model }));
        }
      }
    } catch (e) {
      console.warn('Backend not responding yet:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  // Re-index handler
  const handleReindex = async () => {
    setReindexing(true);
    try {
      const res = await fetch('/api/reindex', { method: 'POST' });
      if (res.ok) {
        await fetchStatus();
      } else {
        const err = await res.json();
        alert(`Re-indexing failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (e) {
      alert(`Error contacting server: ${e.message}`);
    } finally {
      setReindexing(false);
    }
  };

  // Feedback handler
  const handleFeedback = async (msgId, query, answer, rating, sources) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, feedback: rating } : m))
    );
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: json.stringify({ query, answer, rating, sources })
      });
    } catch (e) {
      console.error('Failed to log feedback:', e);
    }
  };

  // Send message
  const handleSend = async (queryToSend) => {
    const query = (queryToSend || inputQuery).trim();
    if (!query || isGenerating) return;

    setInputQuery('');
    const userMsgId = 'user_' + Date.now();
    const assistantMsgId = 'asst_' + (Date.now() + 1);

    // Append user message and empty assistant message
    const newMessages = [
      ...messages,
      { id: userMsgId, role: 'user', content: query },
      { id: assistantMsgId, role: 'assistant', content: '', sources: [], query }
    ];
    setMessages(newMessages);
    setIsGenerating(true);

    try {
      // Build chat history for query rewriter (last 4 turns)
      const chatHistory = messages.slice(-4).map((m) => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          category: selectedCategory,
          top_k: settings.top_k,
          sim_threshold: settings.sim_threshold,
          model: settings.model,
          chat_history: chatHistory,
          api_key: settings.apiKey || undefined
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let currentSources = [];
      let fullContent = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          if (!block.trim()) continue;
          const [eventLine, ...dataLines] = block.split('\n');
          const event = eventLine.replace(/^event:\s*/, '').trim();
          const rawData = dataLines.join('\n').replace(/^data:\s*/, '').trim();

          if (event === 'sources') {
            try {
              currentSources = JSON.parse(rawData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, sources: currentSources } : m
                )
              );
            } catch (e) {
              console.error('Error parsing sources:', e);
            }
          } else if (event === 'token') {
            try {
              const token = JSON.parse(rawData);
              fullContent += token;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, content: fullContent } : m
                )
              );
            } catch (e) {
              fullContent += rawData;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, content: fullContent } : m
                )
              );
            }
          } else if (event === 'done') {
            break;
          }
        }
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsgId
            ? {
                ...m,
                content:
                  `⚠️ **Network or Execution Error**: ${err.message}. Please verify the backend service is running.`
              }
            : m
        )
      );
    } finally {
      setIsGenerating(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const hasApiKey = Boolean(settings.apiKey || status?.has_api_key);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-app)' }}>
      {/* Header */}
      <Header
        status={status}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Layout Container */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <Sidebar
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={(cat) => setSelectedCategory(cat)}
          onClearChat={() => setMessages([])}
          onReindex={handleReindex}
          reindexing={reindexing}
          status={status}
        />

        {/* Chat / Content Area */}
        <main style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Missing API Key Alert */}
          {!hasApiKey && (
            <div style={{
              background: 'var(--warning-bg)',
              color: 'var(--warning)',
              borderBottom: '1px solid rgba(245, 158, 11, 0.3)',
              padding: '10px 24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '13px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={16} />
                <span>
                  <strong>Groq API Key not detected:</strong> Please set <code>GROQ_API_KEY</code> in <code>.env</code> or configure it in Settings.
                </span>
              </div>
              <button
                onClick={() => setIsSettingsOpen(true)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '6px',
                  background: 'var(--warning)',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '12px'
                }}
              >
                Enter Key
              </button>
            </div>
          )}

          {/* Active Category Banner */}
          {selectedCategory !== 'All' && (
            <div style={{
              background: 'var(--accent-soft)',
              color: 'var(--accent)',
              borderBottom: '1px solid var(--accent-border)',
              padding: '6px 24px',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <span>Filtering search context strictly to: <strong>{selectedCategory}</strong></span>
              <button
                onClick={() => setSelectedCategory('All')}
                style={{ color: 'var(--accent)', fontWeight: 600, textDecoration: 'underline' }}
              >
                Reset to All
              </button>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '24px 32px'
          }}>
            {messages.length === 0 ? (
              <WelcomeCards onSelectExample={(q) => handleSend(q)} />
            ) : (
              <div>
                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    onFeedback={handleFeedback}
                  />
                ))}
                {isGenerating && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    maxWidth: '860px',
                    margin: '0 auto 20px auto',
                    color: 'var(--text-muted)',
                    fontSize: '13px'
                  }}>
                    <Sparkles size={16} color="var(--accent)" className="status-pulse" />
                    <span>Searching handbook and formulating cited answer...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Bar */}
          <div style={{
            background: 'var(--bg-surface)',
            borderTop: '1px solid var(--border-color)',
            padding: '16px 28px 20px 28px'
          }}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              style={{
                maxWidth: '860px',
                margin: '0 auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                background: 'var(--bg-app)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-lg)',
                padding: '4px 6px 4px 16px',
                boxShadow: 'var(--shadow-sm)'
              }}>
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Ask about compensation, ESOPs, travel caps, leave entitlements, or employee benefits..."
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  disabled={isGenerating}
                  style={{
                    flex: 1,
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    color: 'var(--text-main)',
                    fontSize: '14px',
                    padding: '8px 0'
                  }}
                />
                <button
                  type="submit"
                  disabled={!inputQuery.trim() || isGenerating}
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: 'var(--radius-md)',
                    background: inputQuery.trim() && !isGenerating ? 'var(--accent)' : 'var(--border-color)',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: inputQuery.trim() && !isGenerating ? 'pointer' : 'not-allowed'
                  }}
                >
                  <Send size={16} />
                </button>
              </div>

              <div style={{
                textAlign: 'center',
                fontSize: '11.5px',
                color: 'var(--text-subtle)'
              }}>
                Answers generated strictly from the employee handbook. Human Resources is the final authority on policy interpretation.
              </div>
            </form>
          </div>
        </main>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveSettings={(newSettings) => {
          setSettings(newSettings);
          if (newSettings.apiKey) {
            localStorage.setItem('hr_api_key', newSettings.apiKey);
          }
        }}
        availableModels={status?.available_models}
      />
    </div>
  );
}

