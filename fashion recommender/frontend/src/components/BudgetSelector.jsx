import React from 'react';

const QUICK_BUDGETS = [
  { label: 'Under ₹1,000', min: 400, max: 1000 },
  { label: '₹1,000 – ₹2,500', min: 1000, max: 2500 },
  { label: '₹2,500 – ₹5,000', min: 2500, max: 5000 },
  { label: '₹5,000 – ₹10,000', min: 5000, max: 10000 },
  { label: '₹10,000+', min: 10000, max: 25000 },
];

export default function BudgetSelector({
  budgetMin = 1500,
  budgetMax = 6000,
  onChangeMin,
  onChangeMax
}) {
  const isSelectedQuick = (qb) => budgetMin === qb.min && budgetMax === qb.max;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Quick Option Pills */}
      <div>
        <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'block' }}>
          QUICK BUDGET PRESETS (INR ₹)
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {QUICK_BUDGETS.map((qb, idx) => {
            const active = isSelectedQuick(qb);
            return (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  onChangeMin(qb.min);
                  onChangeMax(qb.max);
                }}
                style={{
                  padding: '0.45rem 0.9rem',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  background: active ? 'rgba(212, 175, 55, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: active ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                  color: active ? 'var(--gold-light)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {qb.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom Budget Inputs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1rem',
        background: 'rgba(255, 255, 255, 0.03)',
        padding: '1.25rem',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)'
      }}>
        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
            MINIMUM BUDGET (₹)
          </label>
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--gold-light)', fontWeight: 600 }}>₹</span>
            <input
              type="number"
              min="200"
              max="100000"
              step="100"
              value={budgetMin}
              onChange={(e) => onChangeMin(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem 0.6rem 2rem',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                fontWeight: 600
              }}
            />
          </div>
        </div>

        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
            MAXIMUM BUDGET (₹)
          </label>
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--gold-light)', fontWeight: 600 }}>₹</span>
            <input
              type="number"
              min="500"
              max="200000"
              step="100"
              value={budgetMax}
              onChange={(e) => onChangeMax(Number(e.target.value))}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem 0.6rem 2rem',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                fontWeight: 600
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Active Outfit Target: <strong style={{ color: 'var(--gold-light)' }}>₹{budgetMin.toLocaleString('en-IN')} – ₹{budgetMax.toLocaleString('en-IN')}</strong>. Recommendations will automatically optimize item combinations to respect this limit.
      </div>
    </div>
  );
}
