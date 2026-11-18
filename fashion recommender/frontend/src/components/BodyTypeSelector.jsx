import React, { useState } from 'react';

export const BODY_TYPES = [
  { id: 'Rectangle', label: 'Rectangle', desc: 'Balanced shoulders and hips with subtle waist definition.' },
  { id: 'Hourglass', label: 'Hourglass', desc: 'Evenly proportioned bust and hips with defined waist.' },
  { id: 'Pear', label: 'Pear', desc: 'Hips are broader than shoulders, often styled with highlighted tops.' },
  { id: 'Apple', label: 'Apple', desc: 'Fuller torso and bust with shapely legs, great for empire cuts.' },
  { id: 'Inverted Triangle', label: 'Inverted Triangle', desc: 'Broader shoulders tapering down, pairs well with A-line styles.' },
  { id: 'Athletic', label: 'Athletic', desc: 'Muscular tone with structured shoulders and defined posture.' },
  { id: 'Plus-size', label: 'Plus-size', desc: 'Full-figured silhouette celebrated with fluid and structured tailoring.' },
  { id: 'Not sure', label: 'Not sure', desc: 'Stylist will balance proportions evenly across standard silhouettes.' },
  { id: 'Prefer not to specify', label: 'Prefer not to specify', desc: 'Styling focuses purely on fit and aesthetic preferences.' },
];

export default function BodyTypeSelector({
  selectedBodyType,
  customBodyType = '',
  onSelectBodyType,
  onChangeCustom
}) {
  const [showCustom, setShowCustom] = useState(selectedBodyType === 'Other');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))',
        gap: '0.75rem'
      }}>
        {BODY_TYPES.map((bt) => {
          const isSelected = selectedBodyType === bt.id;
          return (
            <div
              key={bt.id}
              onClick={() => {
                setShowCustom(false);
                onSelectBodyType(bt.id);
              }}
              style={{
                padding: '0.85rem 1rem',
                borderRadius: 'var(--radius-md)',
                background: isSelected ? 'rgba(212, 175, 55, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                border: isSelected ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.25rem'
              }}
            >
              <div style={{
                fontSize: '0.92rem',
                fontWeight: 600,
                color: isSelected ? 'var(--gold-light)' : 'var(--text-primary)'
              }}>
                {bt.label}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.35 }}>
                {bt.desc}
              </div>
            </div>
          );
        })}

        {/* Other / Describe */}
        <div
          onClick={() => {
            setShowCustom(true);
            onSelectBodyType('Other');
          }}
          style={{
            padding: '0.85rem 1rem',
            borderRadius: 'var(--radius-md)',
            background: showCustom ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.04)',
            border: showCustom ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid var(--border-subtle)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.25rem'
          }}
        >
          <div style={{
            fontSize: '0.92rem',
            fontWeight: 600,
            color: showCustom ? 'var(--accent-cyan)' : 'var(--text-primary)'
          }}>
            Other / Describe
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.35 }}>
            Describe your unique proportions in your own words.
          </div>
        </div>
      </div>

      {showCustom && (
        <div style={{ marginTop: '0.5rem' }}>
          <input
            type="text"
            value={customBodyType}
            onChange={(e) => onChangeCustom(e.target.value)}
            placeholder="E.g. Petite with athletic shoulders, tall torso with longer legs..."
            style={{
              width: '100%',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-medium)',
              padding: '0.65rem 1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.88rem'
            }}
          />
        </div>
      )}

      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        Note: Body type is used strictly as one non-judgmental factor for drape, tailoring, and fit balancing.
      </div>
    </div>
  );
}
