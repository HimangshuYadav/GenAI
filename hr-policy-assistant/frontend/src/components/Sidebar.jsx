import React from 'react';
import {
  Layers,
  RotateCw,
  Trash2,
  FileText,
  DollarSign,
  TrendingUp,
  Coffee,
  Plane,
  Calendar,
  HeartHandshake,
  ShieldCheck,
  Cpu
} from 'lucide-react';

const TOPIC_ICONS = {
  All: Layers,
  Compensation: DollarSign,
  ESOP: TrendingUp,
  Cafeteria: Coffee,
  Travel: Plane,
  Leave: Calendar,
  Benefits: HeartHandshake,
  General: ShieldCheck
};

export default function Sidebar({
  categories,
  selectedCategory,
  onSelectCategory,
  onClearChat,
  onReindex,
  reindexing,
  status
}) {
  return (
    <aside style={{
      width: '280px',
      height: 'calc(100vh - 75px)',
      background: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      padding: '20px 16px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      overflowY: 'auto'
    }}>
      <div>
        {/* Quick Filter Title */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '14px',
          paddingLeft: '4px'
        }}>
          <Layers size={16} color="var(--accent)" />
          <span style={{
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.6px',
            color: 'var(--text-muted)'
          }}>
            Topic Filters
          </span>
        </div>

        {/* Category Pills */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {categories.map((cat) => {
            const Icon = TOPIC_ICONS[cat] || Layers;
            const isSelected = selectedCategory === cat;

            return (
              <button
                key={cat}
                onClick={() => onSelectCategory(cat)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '9px 12px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '13px',
                  fontWeight: isSelected ? 600 : 500,
                  background: isSelected ? 'var(--accent-soft)' : 'transparent',
                  color: isSelected ? 'var(--accent)' : 'var(--text-main)',
                  border: isSelected ? '1px solid var(--accent-border)' : '1px solid transparent',
                  textAlign: 'left',
                  width: '100%'
                }}
              >
                <Icon size={16} />
                <span>{cat}</span>
              </button>
            );
          })}
        </div>

        <div style={{ height: '1px', background: 'var(--border-color)', margin: '18px 0' }} />

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button
            onClick={onReindex}
            disabled={reindexing}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              fontSize: '13px',
              fontWeight: 600,
              background: 'var(--accent)',
              color: 'white',
              opacity: reindexing ? 0.7 : 1,
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            <RotateCw size={15} style={{ animation: reindexing ? 'spin 1s linear infinite' : 'none' }} />
            <span>{reindexing ? 'Re-indexing...' : 'Re-index Handbook'}</span>
          </button>

          <button
            onClick={onClearChat}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '9px 14px',
              borderRadius: 'var(--radius-md)',
              fontSize: '13px',
              fontWeight: 500,
              background: 'transparent',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)'
            }}
          >
            <Trash2 size={15} />
            <span>Clear Conversation</span>
          </button>
        </div>
      </div>

      {/* Document Metadata Card */}
      <div style={{
        background: 'var(--bg-app)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '14px',
        marginTop: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
          <FileText size={15} color="var(--accent)" />
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-main)' }}>
            Active Reference Document
          </span>
        </div>
        <p style={{
          fontSize: '11.5px',
          color: 'var(--text-muted)',
          wordBreak: 'break-all',
          marginBottom: '6px'
        }}>
          {status?.pdf_name || 'handbook.pdf'}
        </p>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-subtle)' }}>
          <span>Chunks: {status?.chunk_count || 0}</span>
          <span>BAAI/bge-small</span>
        </div>
      </div>
    </aside>
  );
}

