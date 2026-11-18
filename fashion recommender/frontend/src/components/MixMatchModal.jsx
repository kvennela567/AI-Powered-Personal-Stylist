import React, { useState, useEffect } from 'react';
import { X, Shuffle, Check, Sparkles, Loader2 } from 'lucide-react';
import { getMixMatchAlternatives } from '../services/api';
import { useApp } from '../context/AppContext';

export default function MixMatchModal({
  isOpen,
  onClose,
  outfit,
  roleToReplace,
  onApplyReplacement
}) {
  const { userProfile, weatherData, showToast } = useApp();
  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAlt, setSelectedAlt] = useState(null);

  useEffect(() => {
    if (!isOpen || !outfit || !roleToReplace) return;

    async function loadAlternatives() {
      try {
        setLoading(true);
        // Extract IDs of accepted products (the other 3 items)
        const acceptedIds = outfit.items
          .filter(it => it.role !== roleToReplace && it.product)
          .map(it => it.product.id);

        const res = await getMixMatchAlternatives({
          outfit_id: outfit.id,
          accepted_product_ids: acceptedIds,
          role_to_replace: roleToReplace,
          occasion: outfit.occasion,
          budget_max: userProfile?.budget_max || 6000,
          weather: weatherData?.condition || 'Mild'
        });

        setAlternatives(res.alternatives || []);
      } catch (err) {
        console.error('Failed to load mix and match alternatives:', err);
        showToast('Could not load alternatives for this piece', 'error');
      } finally {
        setLoading(false);
      }
    }

    loadAlternatives();
  }, [isOpen, outfit, roleToReplace]);

  if (!isOpen) return null;

  const currentItem = outfit.items.find(it => it.role === roleToReplace)?.product;

  const handleApply = () => {
    if (!selectedAlt) {
      showToast('Please pick an alternative to swap', 'info');
      return;
    }
    onApplyReplacement(roleToReplace, selectedAlt.replacement_product);
    showToast(`Replaced ${roleToReplace} with ${selectedAlt.replacement_product.name}!`, 'success');
    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      background: 'rgba(5, 8, 14, 0.85)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem'
    }}>
      <div className="glass-card" style={{
        maxWidth: '750px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '2rem',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-medium)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="badge badge-gold" style={{ marginBottom: '0.4rem' }}>
              <Shuffle size={12} />
              MIX & MATCH CUSTOMIZER
            </div>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Change {roleToReplace.toUpperCase()}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Select a compatible replacement that preserves color harmony, {outfit.occasion} dress code, and budget.
            </p>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X size={18} />
          </button>
        </div>

        {/* Current Piece Being Replaced */}
        {currentItem && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <img
                src={currentItem.image_url}
                alt={currentItem.name}
                style={{ width: '48px', height: '48px', objectFit: 'cover', borderRadius: '8px' }}
              />
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>CURRENT ITEM</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{currentItem.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {currentItem.color} • {currentItem.material}
                </div>
              </div>
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gold-light)' }}>
              ₹{currentItem.price.toLocaleString('en-IN')}
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Loader2 size={32} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--gold-light)' }} />
            <div>AI analyzing palette harmony and occasion compatibility...</div>
          </div>
        ) : (
          /* Compatible Alternatives List */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
              RECOMMENDED COMPATIBLE ALTERNATIVES ({alternatives.length})
            </div>

            {alternatives.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                No direct alternative found within current filters.
              </div>
            ) : (
              alternatives.map((alt, idx) => {
                const p = alt.replacement_product;
                const isSelected = selectedAlt?.replacement_product.id === p.id;

                return (
                  <div
                    key={p.id || idx}
                    onClick={() => setSelectedAlt(alt)}
                    style={{
                      background: isSelected ? 'rgba(212, 175, 55, 0.1)' : 'rgba(15, 23, 42, 0.5)',
                      border: isSelected ? '1px solid var(--gold-light)' : '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      padding: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '1rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <img
                        src={p.image_url}
                        alt={p.name}
                        style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '8px' }}
                      />
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                          <span style={{ fontSize: '0.92rem', fontWeight: 600 }}>{p.name}</span>
                          <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>
                            {alt.compatibility_score}% Harmony
                          </span>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                          {p.color} • {p.material} {p.fit ? `• ${p.fit}` : ''}
                        </div>
                        <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                          {alt.explanation}
                        </div>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right', minWidth: '110px' }}>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gold-light)' }}>
                        ₹{p.price.toLocaleString('en-IN')}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        New Total: ₹{alt.new_total_price.toLocaleString('en-IN')}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* Footer Actions */}
        <div style={{
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '0.75rem',
          paddingTop: '1rem',
          borderTop: '1px solid var(--border-subtle)'
        }}>
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleApply}
            disabled={!selectedAlt}
            className="btn-primary"
            style={{ opacity: selectedAlt ? 1 : 0.5 }}
          >
            <Check size={16} />
            <span>Apply Selected Swap</span>
          </button>
        </div>
      </div>
    </div>
  );
}
