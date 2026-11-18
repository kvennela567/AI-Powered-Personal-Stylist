import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { getSavedOutfits, deleteSavedOutfit } from '../services/api';
import OutfitCard from '../components/OutfitCard';
import OutfitVisualizerModal from '../components/OutfitVisualizerModal';
import { Heart, Trash2, Sparkles, Loader2, Calendar } from 'lucide-react';

export default function SavedOutfits() {
  const { savedOutfits, refreshSavedOutfits, showToast, setActiveTab } = useApp();
  const [loading, setLoading] = useState(false);
  const [selectedOutfit, setSelectedOutfit] = useState(null);
  const [visualizeOpen, setVisualizeOpen] = useState(false);

  useEffect(() => {
    refreshSavedOutfits();
  }, []);

  const handleDelete = async (outfitId) => {
    try {
      await deleteSavedOutfit(outfitId);
      showToast('Outfit removed from My Outfits');
      refreshSavedOutfits();
    } catch (err) {
      showToast(err.message || 'Failed to remove saved outfit', 'error');
    }
  };

  const handleOpenVisualize = (outfit) => {
    setSelectedOutfit(outfit);
    setVisualizeOpen(true);
  };

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 5rem' }}>
      {/* Header */}
      <div className="section-header" style={{ textAlign: 'left', marginBottom: '2rem' }}>
        <div className="badge badge-gold" style={{ marginBottom: '0.5rem' }}>
          WARDROBE ARCHIVE
        </div>
        <h2>My Saved Outfits</h2>
        <p>
          Your curated wardrobe lookbook ({savedOutfits.length} saved).
          Inspect item compositions, total ensemble prices, or generate similar outfits.
        </p>
      </div>

      {savedOutfits.length === 0 ? (
        <div className="glass-card" style={{
          padding: '4rem 2rem',
          textAlign: 'center',
          borderRadius: 'var(--radius-lg)',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'rgba(212, 175, 55, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem',
            color: 'var(--gold-light)'
          }}>
            <Heart size={28} />
          </div>
          <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>No Saved Outfits Yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            When the AI Stylist or Recommendation Engine curates an outfit you love, tap "Save" to archive it here.
          </p>
          <button onClick={() => setActiveTab('recommendations')} className="btn-primary">
            <Sparkles size={16} />
            <span>Discover Outfits</span>
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {savedOutfits.map((outfit) => (
            <div key={outfit.id} style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                top: '1.5rem',
                right: '1.5rem',
                zIndex: 10
              }}>
                <button
                  onClick={() => handleDelete(outfit.id)}
                  className="btn-icon"
                  title="Remove from My Outfits"
                  style={{ color: 'var(--accent-rose)' }}
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <OutfitCard
                outfit={outfit}
                onVisualize={handleOpenVisualize}
                onTryAnother={() => setActiveTab('recommendations')}
              />
            </div>
          ))}
        </div>
      )}

      {/* Lookbook Visualizer */}
      <OutfitVisualizerModal
        isOpen={visualizeOpen}
        onClose={() => setVisualizeOpen(false)}
        outfit={selectedOutfit}
        onGenerateNewLook={() => setActiveTab('recommendations')}
      />
    </div>
  );
}
