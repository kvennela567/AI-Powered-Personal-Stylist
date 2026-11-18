import React, { useState } from 'react';

export const ALL_OCCASIONS = [
  'College', 'University', 'Office', 'Business Meeting', 'Interview',
  'Casual Outing', 'Shopping', 'Travel', 'Vacation', 'Party',
  'Birthday', 'Date', 'Dinner', 'Wedding', 'Engagement',
  'Festival', 'Religious Event', 'Family Gathering', 'Brunch', 'Beach',
  'Sports', 'Gym', 'Concert', 'Formal Event', 'Semi-Formal Event',
  'Photoshoot'
];

export default function OccasionSelector({ selectedOccasion, onSelectOccasion }) {
  const [isCustom, setIsCustom] = useState(false);
  const [customText, setCustomText] = useState('');

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (customText.trim()) {
      onSelectOccasion(customText.trim());
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.5rem',
        maxHeight: '220px',
        overflowY: 'auto',
        padding: '0.25rem'
      }}>
        {ALL_OCCASIONS.map((occ) => {
          const isSelected = selectedOccasion?.toLowerCase() === occ.toLowerCase() && !isCustom;
          return (
            <button
              key={occ}
              type="button"
              onClick={() => {
                setIsCustom(false);
                onSelectOccasion(occ);
              }}
              style={{
                padding: '0.45rem 0.9rem',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.82rem',
                fontWeight: isSelected ? 600 : 400,
                background: isSelected ? 'rgba(212, 175, 55, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                border: isSelected ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                color: isSelected ? 'var(--gold-light)' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {occ}
            </button>
          );
        })}

        <button
          type="button"
          onClick={() => setIsCustom(true)}
          style={{
            padding: '0.45rem 0.9rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.82rem',
            fontWeight: 600,
            background: isCustom ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
            border: isCustom ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid var(--border-subtle)',
            color: isCustom ? 'var(--accent-cyan)' : 'var(--text-secondary)',
            cursor: 'pointer'
          }}
        >
          ✨ Other / Custom Occasion
        </button>
      </div>

      {/* Custom Occasion Input */}
      {isCustom && (
        <form onSubmit={handleCustomSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            placeholder="Type custom occasion (e.g. Graduation Ceremony, Rooftop Sundowner)..."
            style={{
              flexGrow: 1,
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-medium)',
              padding: '0.6rem 1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.88rem',
              color: 'var(--text-primary)'
            }}
          />
          <button type="submit" className="btn-secondary" style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem' }}>
            Set Occasion
          </button>
        </form>
      )}
    </div>
  );
}
