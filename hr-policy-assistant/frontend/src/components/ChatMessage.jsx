import React, { useState } from 'react';
import { User, Bot, BookOpen, ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Check } from 'lucide-react';

export default function ChatMessage({ message, onFeedback }) {
  const isUser = message.role === 'user';
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(message.feedback || null);

  const handleRate = (rating) => {
    setFeedbackGiven(rating);
    if (onFeedback) {
      onFeedback(message.id, message.query || '', message.content, rating, message.sources || []);
    }
  };

  // Helper to render basic markdown lines
  const renderFormattedContent = (text) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Bullets
      if (line.startsWith('• ') || line.startsWith('- ')) {
        const item = line.substring(2);
        return (
          <li key={idx} style={{ marginBottom: '4px', marginLeft: '16px' }}>
            <span dangerouslySetInnerHTML={{ __html: formatInline(item) }} />
          </li>
        );
      }
      // Note/Disclaimer blockquote
      if (line.includes('ℹ️') || line.includes('Note:')) {
        return (
          <div key={idx} style={{
            fontSize: '12px',
            color: 'var(--text-muted)',
            fontStyle: 'italic',
            borderLeft: '2px solid var(--accent)',
            paddingLeft: '8px',
            marginTop: '10px'
          }}>
            <span dangerouslySetInnerHTML={{ __html: formatInline(line) }} />
          </div>
        );
      }
      if (!line.trim()) {
        return <div key={idx} style={{ height: '8px' }} />;
      }
      return (
        <p key={idx} style={{ marginBottom: '6px' }}>
          <span dangerouslySetInnerHTML={{ __html: formatInline(line) }} />
        </p>
      );
    });
  };

  const formatInline = (str) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\(([^)]+p\.\s*\d+[^)]*)\)/g, '<span style="color:var(--accent); font-weight:500;">($1)</span>');
  };

  return (
    <div className="animate-fade-in" style={{
      display: 'flex',
      gap: '14px',
      marginBottom: '24px',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      maxWidth: '860px',
      margin: '0 auto 24px auto'
    }}>
      {/* Bot Avatar */}
      {!isUser && (
        <div style={{
          width: '34px',
          height: '34px',
          borderRadius: '50%',
          background: 'var(--accent)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          boxShadow: 'var(--shadow-sm)'
        }}>
          <Bot size={18} />
        </div>
      )}

      {/* Bubble Container */}
      <div style={{
        maxWidth: isUser ? '75%' : '88%',
        background: isUser ? 'var(--user-bubble)' : 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        padding: '16px 20px',
        boxShadow: 'var(--shadow-sm)',
        color: isUser ? 'var(--user-bubble-text)' : 'var(--text-main)'
      }}>
        <div className="prose-content">
          {renderFormattedContent(message.content)}
        </div>

        {/* Expandable Sources section */}
        {!isUser && message.sources && message.sources.length > 0 && !message.content.includes("couldn't find this") && (
          <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid var(--border-color)' }}>
            <button
              onClick={() => setSourcesOpen(!sourcesOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--accent)',
                padding: '4px 0'
              }}
            >
              <BookOpen size={14} />
              <span>{sourcesOpen ? 'Hide Sources' : `View ${message.sources.length} Cited Sources`}</span>
              {sourcesOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {sourcesOpen && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '10px' }}>
                {message.sources.map((src, sIdx) => {
                  const matchPct = Math.round((src.similarity || 0) * 100);
                  return (
                    <div
                      key={sIdx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderLeft: '3px solid var(--accent)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '10px 12px',
                        fontSize: '12px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600, color: 'var(--accent)' }}>
                          {src.section_title || 'Handbook Excerpt'}
                        </span>
                        <span style={{
                          fontSize: '11px',
                          padding: '1px 6px',
                          borderRadius: '10px',
                          background: 'var(--accent-soft)',
                          color: 'var(--accent)',
                          fontWeight: 600
                        }}>
                          Page {src.page_number} • {matchPct}% match
                        </span>
                      </div>
                      <p style={{
                        color: 'var(--text-muted)',
                        fontSize: '11.5px',
                        fontFamily: 'var(--font-mono)',
                        lineHeight: 1.4
                      }}>
                        {src.text}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Feedback buttons */}
        {!isUser && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginTop: '12px',
            paddingTop: '8px'
          }}>
            <button
              onClick={() => handleRate('up')}
              title="Helpful"
              style={{
                padding: '4px 8px',
                borderRadius: '6px',
                border: '1px solid var(--border-color)',
                color: feedbackGiven === 'up' ? 'var(--success)' : 'var(--text-muted)',
                background: feedbackGiven === 'up' ? 'var(--success-bg)' : 'transparent',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px'
              }}
            >
              <ThumbsUp size={12} />
              {feedbackGiven === 'up' && <span>Helpful</span>}
            </button>

            <button
              onClick={() => handleRate('down')}
              title="Not helpful"
              style={{
                padding: '4px 8px',
                borderRadius: '6px',
                border: '1px solid var(--border-color)',
                color: feedbackGiven === 'down' ? '#ef4444' : 'var(--text-muted)',
                background: feedbackGiven === 'down' ? '#fee2e2' : 'transparent',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px'
              }}
            >
              <ThumbsDown size={12} />
              {feedbackGiven === 'down' && <span>Not helpful</span>}
            </button>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div style={{
          width: '34px',
          height: '34px',
          borderRadius: '50%',
          background: 'var(--border-color)',
          color: 'var(--text-main)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <User size={18} />
        </div>
      )}
    </div>
  );
}

