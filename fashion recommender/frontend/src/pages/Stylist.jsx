import React, { useState } from 'react';
import ChatBox from '../components/ChatBox';
import MixMatchModal from '../components/MixMatchModal';
import OutfitVisualizerModal from '../components/OutfitVisualizerModal';
import { useApp } from '../context/AppContext';
import { Sparkles, User, Sliders, CloudSun, Shield, Layers } from 'lucide-react';

export default function Stylist() {
  const { userProfile, weatherData, setActiveTab } = useApp();
  const [modalOutfit, setModalOutfit] = useState(null);
  const [mixMatchRole, setMixMatchRole] = useState(null);
  const [visualizeOpen, setVisualizeOpen] = useState(false);

  const handleOpenMixMatch = (outfit, role, currentProductId) => {
    setModalOutfit(outfit);
    setMixMatchRole(role);
  };

  const handleApplyReplacement = (role, newProduct) => {
    if (!modalOutfit) return;
    const updatedItems = modalOutfit.items.map(it => {
      if (it.role === role) {
        return { ...it, product: newProduct };
      }
      return it;
    });
    setModalOutfit({ ...modalOutfit, items: updatedItems });
  };

  const handleOpenVisualize = (outfit) => {
    setModalOutfit(outfit);
    setVisualizeOpen(true);
  };

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 5rem' }}>
      <div className="section-header" style={{ textAlign: 'left', marginBottom: '1.75rem' }}>
        <div className="badge badge-gold" style={{ marginBottom: '0.5rem' }}>
          CONVERSATIONAL FASHION INTELLIGENCE
        </div>
        <h2>AI Stylist Studio</h2>
        <p>
          Chat directly with Aura, your virtual luxury stylist. The AI continuously references your active style DNA, body type, budget, and real-time weather.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) 320px',
        gap: '2rem',
        alignItems: 'start'
      }} className="stylist-layout">
        {/* Main Column: Chat Studio */}
        <div>
          <ChatBox
            onMixMatch={handleOpenMixMatch}
            onVisualize={handleOpenOpen => handleOpenVisualize(handleOpenOpen)}
          />
        </div>

        {/* Sidebar: Active Style Profile Context */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="glass-card" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
                SYNCED PROFILE DNA
              </span>
              <button
                onClick={() => setActiveTab('profile')}
                style={{ fontSize: '0.75rem', color: 'var(--gold-light)', fontWeight: 600 }}
              >
                Edit
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Client:</span>
                <strong style={{ color: 'var(--text-primary)' }}>{userProfile?.name || 'Alex'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Gender:</span>
                <strong style={{ color: 'var(--gold-light)' }}>{userProfile?.gender || 'Female'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Silhouette:</span>
                <strong style={{ color: 'var(--text-primary)' }}>{userProfile?.body_type || 'Rectangle'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Budget:</span>
                <strong style={{ color: 'var(--gold-light)' }}>
                  ₹{userProfile?.budget_min?.toLocaleString('en-IN')} – ₹{userProfile?.budget_max?.toLocaleString('en-IN')}
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Preferred Fit:</span>
                <strong style={{ color: 'var(--text-primary)' }}>{userProfile?.preferred_fit || 'Relaxed'}</strong>
              </div>
              <div>
                <div style={{ color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Favorite Colors:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                  {(userProfile?.favorite_colors || ['Navy', 'White', 'Beige']).slice(0, 4).map(c => (
                    <span key={c} style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      padding: '0.2rem 0.5rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.74rem'
                    }}>
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Current Weather Styling Card */}
          <div className="glass-card" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <CloudSun size={18} color="var(--gold-light)" />
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Active Weather Forecast</span>
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
              {weatherData.condition} • {weatherData.temperature_c}°C
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
              {weatherData.styling_advice}
            </div>
          </div>

          {/* Prompt Inspirations */}
          <div className="glass-card" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Sparkles size={14} color="var(--gold-light)" />
              <span>Prompt Inspirations</span>
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.6rem', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              <li>• "Recommend an outfit for my college presentation under ₹3,000"</li>
              <li>• "Need a smart casual dinner look with Chelsea boots"</li>
              <li>• "What works best for hot sunny afternoon brunch?"</li>
              <li>• "Suggest a modern traditional look for a family festival"</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Mix and Match Modal */}
      {mixMatchRole && (
        <MixMatchModal
          isOpen={Boolean(mixMatchRole)}
          onClose={() => setMixMatchRole(null)}
          outfit={modalOutfit}
          roleToReplace={mixMatchRole}
          onApplyReplacement={handleApplyReplacement}
        />
      )}

      {/* AI Outfit Lookbook Visualizer */}
      <OutfitVisualizerModal
        isOpen={visualizeOpen}
        onClose={() => setVisualizeOpen(false)}
        outfit={modalOutfit}
        onGenerateNewLook={() => setActiveTab('recommendations')}
      />

      <style>{`
        @media (max-width: 860px) {
          .stylist-layout {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
