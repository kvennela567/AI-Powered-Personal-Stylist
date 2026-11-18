import React, { useState } from 'react';
import { Check, X, Plus, AlertTriangle } from 'lucide-react';

export const ALL_COLORS = [
  { name: 'Black', hex: '#1A202C' },
  { name: 'White', hex: '#F8FAFC' },
  { name: 'Grey', hex: '#64748B' },
  { name: 'Navy', hex: '#1E3A8A' },
  { name: 'Blue', hex: '#3B82F6' },
  { name: 'Sky Blue', hex: '#60A5FA' },
  { name: 'Red', hex: '#EF4444' },
  { name: 'Maroon', hex: '#7F1D1D' },
  { name: 'Pink', hex: '#EC4899' },
  { name: 'Rose', hex: '#F43F5E' },
  { name: 'Purple', hex: '#8B5CF6' },
  { name: 'Lavender', hex: '#C084FC' },
  { name: 'Green', hex: '#10B981' },
  { name: 'Olive', hex: '#556B2F' },
  { name: 'Emerald', hex: '#059669' },
  { name: 'Yellow', hex: '#FBBF24' },
  { name: 'Mustard', hex: '#D97706' },
  { name: 'Orange', hex: '#F97316' },
  { name: 'Brown', hex: '#78350F' },
  { name: 'Beige', hex: '#E2D9C8' },
  { name: 'Cream', hex: '#FFFDD0' },
  { name: 'Tan', hex: '#D2B48C' },
  { name: 'Khaki', hex: '#C3B091' },
  { name: 'Burgundy', hex: '#800020' },
  { name: 'Teal', hex: '#0D9488' },
  { name: 'Turquoise', hex: '#14B8A6' },
];

export const POPULAR_CUSTOM_COLORS = [
  'Sage Green', 'Terracotta', 'Peach', 'Coral',
  'Wine', 'Dusty Pink', 'Champagne', 'Mint Green', 'Lilac'
];

export default function ColorSelector({
  favoriteColors = [],
  avoidColors = [],
  onChangeFavorites,
  onChangeAvoids
}) {
  const [activeMode, setActiveMode] = useState('favorite'); // 'favorite' or 'avoid'
  const [customColor, setCustomColor] = useState('');

  // Conflict validation: check if any color is accidentally in both
  const conflicts = favoriteColors.filter(c => avoidColors.map(x => x.toLowerCase()).includes(c.toLowerCase()));

  const toggleColor = (colorName) => {
    if (activeMode === 'favorite') {
      if (favoriteColors.includes(colorName)) {
        onChangeFavorites(favoriteColors.filter(c => c !== colorName));
      } else {
        onChangeFavorites([...favoriteColors, colorName]);
        // Avoid takes priority: remove from avoid if user explicitly switches to favorite
        onChangeAvoids(avoidColors.filter(c => c.toLowerCase() !== colorName.toLowerCase()));
      }
    } else {
      if (avoidColors.includes(colorName)) {
        onChangeAvoids(avoidColors.filter(c => c !== colorName));
      } else {
        onChangeAvoids([...avoidColors, colorName]);
        // Remove from favorites if added to avoid
        onChangeFavorites(favoriteColors.filter(c => c.toLowerCase() !== colorName.toLowerCase()));
      }
    }
  };

  const handleAddCustomColor = (colorToAdd) => {
    const raw = (colorToAdd || customColor).trim();
    if (!raw) return;
    const formatted = raw.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');

    if (activeMode === 'favorite') {
      if (!favoriteColors.includes(formatted)) {
        onChangeFavorites([...favoriteColors, formatted]);
        onChangeAvoids(avoidColors.filter(c => c.toLowerCase() !== formatted.toLowerCase()));
      }
    } else {
      if (!avoidColors.includes(formatted)) {
        onChangeAvoids([...avoidColors, formatted]);
        onChangeFavorites(favoriteColors.filter(c => c.toLowerCase() !== formatted.toLowerCase()));
      }
    }
    setCustomColor('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Mode Switcher Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255, 255, 255, 0.05)', padding: '0.25rem', borderRadius: 'var(--radius-full)', width: 'fit-content' }}>
        <button
          type="button"
          onClick={() => setActiveMode('favorite')}
          style={{
            padding: '0.45rem 1.2rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.85rem',
            fontWeight: 600,
            background: activeMode === 'favorite' ? 'rgba(52, 211, 153, 0.2)' : 'transparent',
            color: activeMode === 'favorite' ? 'var(--accent-emerald)' : 'var(--text-secondary)',
            border: activeMode === 'favorite' ? '1px solid rgba(52, 211, 153, 0.4)' : '1px solid transparent',
            cursor: 'pointer'
          }}
        >
          ❤️ Favourite Colours ({favoriteColors.length})
        </button>

        <button
          type="button"
          onClick={() => setActiveMode('avoid')}
          style={{
            padding: '0.45rem 1.2rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.85rem',
            fontWeight: 600,
            background: activeMode === 'avoid' ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
            color: activeMode === 'avoid' ? 'var(--accent-rose)' : 'var(--text-secondary)',
            border: activeMode === 'avoid' ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid transparent',
            cursor: 'pointer'
          }}
        >
          🚫 Colours to Avoid ({avoidColors.length})
        </button>
      </div>

      {conflicts.length > 0 && (
        <div style={{
          padding: '0.6rem 1rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          color: '#fca5a5',
          fontSize: '0.82rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <AlertTriangle size={16} />
          <span>Conflict detected: <strong>{conflicts.join(', ')}</strong> is in both lists. Colours in <em>Colours to Avoid</em> take strict priority and will not be recommended.</span>
        </div>
      )}

      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
        {activeMode === 'favorite' 
          ? 'Tap colors you love wearing. Main clothing items will strictly feature these colors or compatible shades.' 
          : 'Tap colors you dislike or want to avoid. The recommendation engine will strictly exclude them from all outfits.'}
      </div>

      {/* 26+ Color Swatches Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
        gap: '0.6rem'
      }}>
        {ALL_COLORS.map(c => {
          const isFav = favoriteColors.some(fc => fc.toLowerCase() === c.name.toLowerCase());
          const isAvoid = avoidColors.some(ac => ac.toLowerCase() === c.name.toLowerCase());
          const isLight = ['White', 'Cream', 'Yellow', 'Beige'].includes(c.name);

          let borderStyle = '1px solid var(--border-subtle)';
          let statusBadge = null;

          if (isFav) {
            borderStyle = '2px solid var(--accent-emerald)';
            statusBadge = <Check size={14} color="var(--accent-emerald)" />;
          } else if (isAvoid) {
            borderStyle = '2px solid var(--accent-rose)';
            statusBadge = <X size={14} color="var(--accent-rose)" />;
          }

          return (
            <button
              key={c.name}
              type="button"
              onClick={() => toggleColor(c.name)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                padding: '0.5rem 0.75rem',
                background: isFav ? 'rgba(52, 211, 153, 0.1)' : (isAvoid ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.04)'),
                border: borderStyle,
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.82rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{
                  width: '18px',
                  height: '18px',
                  borderRadius: '50%',
                  background: c.hex,
                  border: isLight ? '1px solid #718096' : '1px solid rgba(255, 255, 255, 0.2)',
                  display: 'inline-block'
                }} />
                <span>{c.name}</span>
              </div>
              {statusBadge}
            </button>
          );
        })}
      </div>

      {/* Popular Custom Shades Shortcuts */}
      <div style={{ marginTop: '0.5rem' }}>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: 600 }}>
          POPULAR DESIGNER SHADES:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
          {POPULAR_CUSTOM_COLORS.map(shade => {
            const isFav = favoriteColors.some(fc => fc.toLowerCase() === shade.toLowerCase());
            const isAvoid = avoidColors.some(ac => ac.toLowerCase() === shade.toLowerCase());
            return (
              <button
                key={shade}
                type="button"
                onClick={() => toggleColor(shade)}
                style={{
                  fontSize: '0.75rem',
                  padding: '0.25rem 0.65rem',
                  borderRadius: 'var(--radius-full)',
                  background: isFav ? 'rgba(52, 211, 153, 0.2)' : (isAvoid ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.05)'),
                  border: isFav ? '1px solid var(--accent-emerald)' : (isAvoid ? '1px solid var(--accent-rose)' : '1px solid var(--border-subtle)'),
                  color: isFav ? 'var(--accent-emerald)' : (isAvoid ? 'var(--accent-rose)' : 'var(--text-secondary)'),
                  cursor: 'pointer'
                }}
              >
                {shade} {isFav ? '✓' : (isAvoid ? '✕' : '+')}
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom Color Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleAddCustomColor(); }} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
        <input
          type="text"
          value={customColor}
          onChange={(e) => setCustomColor(e.target.value)}
          placeholder="Add custom colour (e.g. Sage Green, Terracotta)..."
          style={{
            flexGrow: 1,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-subtle)',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.85rem',
            color: 'var(--text-primary)'
          }}
        />
        <button type="submit" className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
          <Plus size={15} />
          <span>Add to {activeMode === 'favorite' ? 'Favorites' : 'Avoid'}</span>
        </button>
      </form>
    </div>
  );
}
