import React from 'react';
import { DollarSign, TrendingUp, Coffee, Plane, Calendar, HeartHandshake } from 'lucide-react';

const EXAMPLES = [
  {
    topic: 'Compensation',
    icon: DollarSign,
    color: '#3b82f6',
    query: 'What are the rules and cycle for annual performance calibration and promotion?'
  },
  {
    topic: 'ESOP & Equity',
    icon: TrendingUp,
    color: '#8b5cf6',
    query: 'What is the vesting schedule and cliff for Band-3 engineers?'
  },
  {
    topic: 'Cafeteria',
    icon: Coffee,
    color: '#10b981',
    query: 'What are the cafeteria operating hours and meal facilities provided?'
  },
  {
    topic: 'Travel Reimbursement',
    icon: Plane,
    color: '#f59e0b',
    query: 'What is the maximum hotel lodging reimbursement cap for international travel in Tier-1 cities?'
  },
  {
    topic: 'Leave Policies',
    icon: Calendar,
    color: '#ec4899',
    query: 'What are the parental and paternity leave entitlements and time limits?'
  },
  {
    topic: 'Employee Benefits',
    icon: HeartHandshake,
    color: '#06b6d4',
    query: 'What are the attendance expectations and home-office ergonomic stipend policies?'
  }
];

export default function WelcomeCards({ onSelectExample }) {
  return (
    <div className="animate-fade-in" style={{ maxWidth: '860px', margin: '40px auto 0 auto', padding: '0 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
          How can I help you today?
        </h2>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
          Ask any question about company policies, benefits, travel caps, or select a suggested topic below:
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '14px'
      }}>
        {EXAMPLES.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectExample(item.query)}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-lg)',
                padding: '16px',
                textAlign: 'left',
                boxShadow: 'var(--shadow-sm)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                transition: 'all 0.18s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--accent)';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  background: `${item.color}18`,
                  color: item.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Icon size={16} />
                </div>
                <span style={{
                  fontSize: '11.5px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  color: item.color
                }}>
                  {item.topic}
                </span>
              </div>
              <p style={{
                fontSize: '13px',
                fontWeight: 500,
                color: 'var(--text-main)',
                lineHeight: 1.45
              }}>
                {item.query}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

