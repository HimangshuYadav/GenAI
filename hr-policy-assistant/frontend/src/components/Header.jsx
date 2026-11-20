import React from 'react';
import { Briefcase, Moon, Sun, Settings, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Header({ status, darkMode, onToggleDarkMode, onOpenSettings }) {
  const isIndexed = status?.indexed;
  const chunkCount = status?.chunk_count || 0;

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 28px',
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 10
    }}>
      {/* Brand & Tagline */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, var(--accent) 0%, #1e40af 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <Briefcase size={22} />
        </div>
        <div>
          <h1 style={{
            fontSize: '18px',
            fontWeight: 700,
            color: 'var(--text-main)',
            letterSpacing: '-0.3px',
            lineHeight: 1.2
          }}>
            NovaPay HR Policy Assistant
          </h1>
          <p style={{
            fontSize: '12.5px',
            color: 'var(--text-muted)',
            marginTop: '2px'
          }}>
            Official Employee Handbook AI with Grounded Citations
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Status Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: 600,
          background: isIndexed ? 'var(--success-bg)' : 'var(--warning-bg)',
          color: isIndexed ? 'var(--success)' : 'var(--warning)',
          border: `1px solid ${isIndexed ? 'rgba(34, 197, 94, 0.25)' : 'rgba(245, 158, 11, 0.25)'}`
        }}>
          <span className="status-pulse" style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isIndexed ? 'var(--success)' : 'var(--warning)'
          }} />
          {isIndexed ? `Handbook Indexed (${chunkCount} chunks)` : 'Not Indexed'}
        </div>

        {/* Dark Mode Toggle */}
        <button
          onClick={onToggleDarkMode}
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-card)',
            color: 'var(--text-main)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          title="Assistant Settings"
          style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-card)',
            color: 'var(--text-main)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Settings size={18} />
        </button>
      </div>
    </header>
  );
}

