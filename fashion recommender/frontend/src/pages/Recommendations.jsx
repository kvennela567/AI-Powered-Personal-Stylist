import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { getRecommendations } from '../services/api';
import OutfitCard from '../components/OutfitCard';
import MixMatchModal from '../components/MixMatchModal';
import OutfitVisualizerModal from '../components/OutfitVisualizerModal';
import OccasionSelector, { ALL_OCCASIONS } from '../components/OccasionSelector';
import { Sparkles, Loader2, Sliders, RefreshCw, Layers, AlertCircle, ShieldCheck, ArrowRight } from 'lucide-react';

export default function Recommendations() {
  const { userProfile, profileVersion, weatherMode, weatherData, showToast, setActiveTab, activeOccasion, setActiveOccasion } = useApp();
  const [occasion, setOccasion] = useState(activeOccasion || 'College');
  const [looks, setLooks] = useState([]);
  const [emptyMessage, setEmptyMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeLookIndex, setActiveLookIndex] = useState(0);

  // Modals state
  const [mixMatchRole, setMixMatchRole] = useState(null);
  const [selectedOutfit, setSelectedOutfit] = useState(null);
  const [visualizeOpen, setVisualizeOpen] = useState(false);

  const activeGender = userProfile?.gender || 'Female';

  const fetchLooks = async (targetOccasion = occasion) => {
    try {
      setLoading(true);
      setEmptyMessage(null);
      const res = await getRecommendations({
        occasion: targetOccasion,
        gender: activeGender,
        budget_min: userProfile?.budget_min,
        budget_max: userProfile?.budget_max,
        weather: weatherData?.condition || 'Mild (24°C)',
        include_unisex: userProfile?.include_unisex
      });
      setLooks(res.looks || []);
      if (res.message) {
        setEmptyMessage(res.message);
      } else if (!res.looks || res.looks.length === 0) {
        setEmptyMessage(`No ${activeGender} outfits matched all mandatory criteria for '${targetOccasion}'. Try adjusting your budget or colour restrictions.`);
      }
      setActiveLookIndex(0);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      showToast('Error generating outfit looks', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLooks(occasion);
  }, [occasion, activeGender, profileVersion, weatherMode]);

  const handleOpenMixMatch = (outfit, role, currentProductId) => {
    setSelectedOutfit(outfit);
    setMixMatchRole(role);
  };

  const handleApplyReplacement = (role, newProduct) => {
    if (!selectedOutfit) return;
    const updatedLooks = looks.map(look => {
      if (look.id === selectedOutfit.id) {
        const updatedItems = look.items.map(it => {
          if (it.role === role) {
            return { ...it, product: newProduct };
          }
          return it;
        });
        const newTotal = updatedItems.reduce((acc, it) => acc + (it.product ? it.product.price : 0), 0);
        return { ...look, items: updatedItems, total_price: newTotal };
      }
      return look;
    });
    setLooks(updatedLooks);
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
          CENTRALIZED RECOMMENDATION ENGINE
        </div>
        <h2>Curated Outfits ({activeGender})</h2>
        <p>
          Intelligent, occasion-based, colour-aware outfits synchronized with your {activeGender} DNA, budget (₹{userProfile?.budget_min?.toLocaleString('en-IN')} – ₹{userProfile?.budget_max?.toLocaleString('en-IN')}),
          and real-time {weatherData?.condition} weather.
        </p>
      </div>

      {/* Synchronized DNA Info Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        padding: '0.85rem 1.25rem',
        background: 'rgba(212, 175, 55, 0.08)',
        border: '1px solid rgba(212, 175, 55, 0.25)',
        borderRadius: 'var(--radius-md)',
        marginBottom: '1.5rem',
        fontSize: '0.84rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <ShieldCheck size={18} color="var(--gold-light)" />
          <span><strong>Active Filters:</strong> {activeGender} only • Occasion: <strong>{occasion}</strong></span>
          {userProfile?.favorite_colors?.length > 0 && (
            <span>• Fav Colours: <strong style={{ color: 'var(--accent-emerald)' }}>{userProfile.favorite_colors.join(', ')}</strong></span>
          )}
          {userProfile?.avoid_colors?.length > 0 && (
            <span>• Avoid: <strong style={{ color: 'var(--accent-rose)' }}>{userProfile.avoid_colors.join(', ')}</strong></span>
          )}
          <span>• Max: <strong>₹{userProfile?.budget_max?.toLocaleString('en-IN')}</strong></span>
        </div>

        <button
          onClick={() => setActiveTab('profile')}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--gold-light)',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '0.82rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}
        >
          <span>Modify Preferences</span>
          <ArrowRight size={14} />
        </button>
      </div>

      {/* Interactive Controls Bar: Occasion & Generation */}
      <div className="glass-card" style={{
        padding: '1.5rem',
        borderRadius: 'var(--radius-lg)',
        marginBottom: '2.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
              STEP 1: SELECT OCCASION (27 SUPPORTED)
            </span>
            <div style={{ fontSize: '1rem', fontWeight: 600 }}>Where are you heading? ({occasion})</div>
          </div>

          <button
            onClick={() => fetchLooks(occasion)}
            disabled={loading}
            className="btn-primary"
            style={{ padding: '0.65rem 1.4rem', cursor: 'pointer' }}
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            <span>Regenerate Outfits</span>
          </button>
        </div>

        <OccasionSelector
          selectedOccasion={occasion}
          onSelectOccasion={(newOcc) => {
            setOccasion(newOcc);
            setActiveOccasion(newOcc);
          }}
        />
      </div>

      {/* Loading State */}
      {loading ? (
        <div style={{ padding: '4rem 1rem', textAlign: 'center' }}>
          <Loader2 size={42} className="animate-spin" style={{ margin: '0 auto 1.25rem', color: 'var(--gold-light)' }} />
          <h3 style={{ fontSize: '1.35rem', marginBottom: '0.5rem' }}>Curating {activeGender} Looks for {occasion}...</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '480px', margin: '0 auto' }}>
            Enforcing strict gender isolation, hard color rules, silhouette balancing, and optimizing total price within your INR budget.
          </p>
        </div>
      ) : looks.length === 0 ? (
        /* Empty State with Explanatory Reason */
        <div className="glass-card" style={{
          padding: '3.5rem 2rem',
          textAlign: 'center',
          borderRadius: 'var(--radius-lg)',
          maxWidth: '680px',
          margin: '0 auto'
        }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem',
            color: 'var(--accent-rose)'
          }}>
            <AlertCircle size={32} />
          </div>
          <h3 style={{ fontSize: '1.35rem', marginBottom: '0.75rem' }}>No Matching Products Found</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
            {emptyMessage || `No ${activeGender} outfits in our catalogue satisfy all your mandatory filters for '${occasion}'. Rather than showing unrelated casual clothes, we preserve strict occasion and gender integrity.`}
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setActiveTab('profile')}
              className="btn-primary"
              style={{ fontSize: '0.9rem', padding: '0.65rem 1.5rem' }}
            >
              Adjust Budget / Colour Filters
            </button>
            <button
              onClick={() => { setOccasion('Casual Outing'); setActiveOccasion('Casual Outing'); }}
              className="btn-secondary"
              style={{ fontSize: '0.9rem', padding: '0.65rem 1.5rem' }}
            >
              Try Casual Outing
            </button>
          </div>
        </div>
      ) : (
        /* Looks Showcase */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Look Selector Tabs */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '0.75rem',
            overflowX: 'auto'
          }}>
            {looks.map((look, idx) => {
              const isActive = activeLookIndex === idx;
              return (
                <button
                  key={idx}
                  onClick={() => setActiveLookIndex(idx)}
                  style={{
                    padding: '0.6rem 1.4rem',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.92rem',
                    fontWeight: isActive ? 700 : 500,
                    background: isActive ? 'linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(212, 175, 55, 0.1) 100%)' : 'rgba(255, 255, 255, 0.04)',
                    border: isActive ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                    color: isActive ? 'var(--gold-light)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <span>{look.title}</span>
                  <span className="badge badge-gold" style={{ fontSize: '0.65rem' }}>
                    ₹{Math.round(look.total_price).toLocaleString('en-IN')}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Active Look Display Card */}
          {looks.length > 0 && looks[activeLookIndex] && (
            <OutfitCard
              outfit={looks[activeLookIndex]}
              onMixMatch={handleOpenMixMatch}
              onVisualize={handleOpenVisualize}
              onTryAnother={() => fetchLooks(occasion)}
            />
          )}

          {/* 3 Looks Quick Comparison Strip */}
          {looks.length > 1 && (
            <div style={{ marginTop: '2rem' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '1rem', letterSpacing: '0.04em' }}>
                ALL 3 GENERATED LOOK VARIATIONS ({activeGender} • {occasion})
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.25rem'
              }}>
                {looks.map((l, idx) => (
                  <div
                    key={idx}
                    onClick={() => setActiveLookIndex(idx)}
                    className="glass-card"
                    style={{
                      padding: '1.25rem',
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                      border: activeLookIndex === idx ? '1px solid var(--gold-light)' : '1px solid var(--border-subtle)',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span className="badge badge-gold">{l.budget_tier}</span>
                      <span style={{ fontSize: '0.78rem', color: 'var(--accent-emerald)', fontWeight: 700 }}>
                        {Math.round(l.match_score)}% Match
                      </span>
                    </div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.35rem' }}>{l.title}</h4>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--gold-light)', fontFamily: 'var(--font-heading)' }}>
                      ₹{Math.round(l.total_price).toLocaleString('en-IN')}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                      {l.items.length} coordinated pieces • {l.style_tag}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Mix & Match Modal */}
      {mixMatchRole && (
        <MixMatchModal
          isOpen={Boolean(mixMatchRole)}
          onClose={() => setMixMatchRole(null)}
          outfit={selectedOutfit}
          roleToReplace={mixMatchRole}
          onApplyReplacement={handleApplyReplacement}
        />
      )}

      {/* AI Outfit Visualizer Lookbook Modal */}
      <OutfitVisualizerModal
        isOpen={visualizeOpen}
        onClose={() => setVisualizeOpen(false)}
        outfit={selectedOutfit}
        onGenerateNewLook={() => fetchLooks(occasion)}
      />
    </div>
  );
}
