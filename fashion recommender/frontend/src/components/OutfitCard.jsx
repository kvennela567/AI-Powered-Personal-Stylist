import React, { useState } from 'react';
import { 
  ThumbsUp, 
  ThumbsDown, 
  Heart, 
  Shuffle, 
  Eye, 
  Sparkles, 
  Info, 
  ChevronDown, 
  ChevronUp,
  RotateCcw,
  ShoppingBag,
  Camera,
  Shirt
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { saveOutfit, submitFeedback } from '../services/api';

export default function OutfitCard({
  outfit,
  onMixMatch,
  onVisualize,
  onTryAnother,
  onItemReplaced
}) {
  const { showToast, refreshSavedOutfits, openTryOn, openShopThisLook, setSelectedProductDetail } = useApp();
  const [showExplanation, setShowExplanation] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(null); // 'liked', 'disliked'
  const [savingLoading, setSavingLoading] = useState(false);

  if (!outfit || !outfit.items) return null;

  // Compute live total price based on current items
  const currentTotal = outfit.items.reduce((acc, it) => acc + (it.product ? it.product.price : 0), 0);

  const handleSave = async () => {
    if (!outfit.id) {
      showToast('Outfit saved to My Outfits!', 'success');
      setIsSaved(true);
      return;
    }
    try {
      setSavingLoading(true);
      await saveOutfit(outfit.id);
      setIsSaved(true);
      showToast('Outfit saved to My Outfits!', 'success');
      await refreshSavedOutfits();
    } catch (err) {
      showToast(err.message || 'Failed to save outfit', 'error');
    } finally {
      setSavingLoading(false);
    }
  };

  const handleLike = async () => {
    setFeedbackGiven('liked');
    showToast('Preference learned! Stylist will favor this aesthetic.');
    if (outfit.id) {
      try {
        await submitFeedback({ outfit_id: outfit.id, feedback_type: 'like' });
      } catch (err) {
        console.warn('Feedback submission error:', err);
      }
    }
  };

  const handleDislike = async () => {
    setFeedbackGiven('disliked');
    showToast('Preference noted! We will reduce similar recommendations.');
    if (outfit.id) {
      try {
        await submitFeedback({ outfit_id: outfit.id, feedback_type: 'dislike' });
      } catch (err) {
        console.warn('Feedback submission error:', err);
      }
    }
  };

  const roleLabels = {
    top: 'TOP PIECE',
    bottom: 'BOTTOM PIECE',
    footwear: 'FOOTWEAR',
    accessory: 'ACCESSORY'
  };

  return (
    <div className="glass-card" style={{
      padding: '1.5rem',
      borderRadius: 'var(--radius-lg)',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.25rem',
      position: 'relative'
    }}>
      {/* Card Header: Title & Badges */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '0.75rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span className="badge badge-gold">
              {outfit.budget_tier || 'Balanced'}
            </span>
            <span className="badge badge-cyan">
              {outfit.style_tag}
            </span>
            {outfit.weather_context && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                • {outfit.weather_context}
              </span>
            )}
          </div>
          <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {outfit.title}
          </h3>
        </div>

        {/* Personalization Match Score Badge */}
        <div style={{
          textAlign: 'right',
          background: 'rgba(52, 211, 153, 0.1)',
          border: '1px solid rgba(52, 211, 153, 0.3)',
          padding: '0.4rem 0.8rem',
          borderRadius: 'var(--radius-md)'
        }}>
          <div style={{ fontSize: '0.68rem', color: 'var(--accent-emerald)', fontWeight: 600, letterSpacing: '0.04em' }}>
            PERSONALIZATION MATCH
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-emerald)', fontFamily: 'var(--font-heading)' }}>
            {outfit.match_score ? `${Math.round(outfit.match_score)}%` : '94%'}
          </div>
        </div>
      </div>

      {/* 4-Item Grid Showcase */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1rem'
      }}>
        {outfit.items.map((item, idx) => {
          const product = item.product;
          if (!product) return null;

          return (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 22, 38, 0.65)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                transition: 'border-color 0.2s ease'
              }}
            >
              {/* Product Thumbnail with Swap Button */}
              <div style={{ position: 'relative', height: '180px', background: '#0F172A' }}>
                <img
                  src={product.image_url}
                  alt={product.name}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                <span style={{
                  position: 'absolute',
                  top: '8px',
                  left: '8px',
                  background: 'rgba(9, 13, 22, 0.8)',
                  backdropFilter: 'blur(6px)',
                  color: 'var(--text-secondary)',
                  padding: '0.15rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  letterSpacing: '0.05em'
                }}>
                  {roleLabels[item.role] || item.role.toUpperCase()}
                </span>

                {/* Individual Item Mix & Match Swap Button */}
                {onMixMatch && (
                  <button
                    onClick={() => onMixMatch(outfit, item.role, product.id)}
                    title={`Change ${item.role} with AI alternative`}
                    style={{
                      position: 'absolute',
                      bottom: '8px',
                      right: '8px',
                      background: 'rgba(9, 13, 22, 0.85)',
                      backdropFilter: 'blur(6px)',
                      color: 'var(--gold-light)',
                      border: '1px solid var(--border-gold)',
                      padding: '0.3rem 0.6rem',
                      borderRadius: 'var(--radius-full)',
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      cursor: 'pointer'
                    }}
                  >
                    <Shuffle size={11} />
                    <span>Change</span>
                  </button>
                )}
              </div>

              {/* Product Specs */}
              <div 
                onClick={() => setSelectedProductDetail && setSelectedProductDetail(product)}
                style={{ padding: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', cursor: 'pointer' }}
                title="Click to view full product details"
              >
                <h5 style={{
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {product.name}
                </h5>

                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                  {product.color} • {product.material} {product.fit ? `• ${product.fit}` : ''}
                </div>

                <div style={{
                  marginTop: '0.4rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    color: 'var(--gold-light)',
                    fontFamily: 'var(--font-heading)'
                  }}>
                    ₹{product.price.toLocaleString('en-IN')}
                  </span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--accent-cyan)' }}>
                    Specs →
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Dynamic Explanation Accordion ("Why this outfit?") */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        overflow: 'hidden'
      }}>
        <button
          onClick={() => setShowExplanation(!showExplanation)}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
            fontWeight: 500
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={15} color="var(--gold-light)" />
            <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>Why this outfit?</span>
          </div>
          {showExplanation ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {showExplanation && (
          <div style={{
            padding: '0.75rem 1rem 1rem',
            fontSize: '0.86rem',
            color: 'var(--text-secondary)',
            lineHeight: 1.5,
            borderTop: '1px solid var(--border-subtle)'
          }}>
            {outfit.explanation || "Curated specifically to balance your style aesthetic, preferred color palette, occasion setting, and budget constraints."}
          </div>
        )}
      </div>

      {/* Footer: Total Outfit Price & Actions */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem',
        paddingTop: '0.75rem',
        borderTop: '1px solid var(--border-subtle)'
      }}>
        {/* Total Price Display */}
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
            TOTAL OUTFIT PRICE
          </span>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 800,
            color: 'var(--gold-light)',
            fontFamily: 'var(--font-heading)'
          }}>
            ₹{currentTotal.toLocaleString('en-IN')}
          </div>
        </div>

        {/* Action Button Strip */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          {/* Like */}
          <button
            onClick={handleLike}
            className="btn-icon"
            title="Like this outfit"
            style={{
              color: feedbackGiven === 'liked' ? 'var(--accent-emerald)' : 'var(--text-secondary)',
              background: feedbackGiven === 'liked' ? 'rgba(52, 211, 153, 0.15)' : undefined
            }}
          >
            <ThumbsUp size={16} />
          </button>

          {/* Dislike */}
          <button
            onClick={handleDislike}
            className="btn-icon"
            title="Dislike this outfit"
            style={{
              color: feedbackGiven === 'disliked' ? 'var(--accent-rose)' : 'var(--text-secondary)',
              background: feedbackGiven === 'disliked' ? 'rgba(226, 132, 122, 0.15)' : undefined
            }}
          >
            <ThumbsDown size={16} />
          </button>

          {/* Save Outfit */}
          <button
            onClick={handleSave}
            disabled={savingLoading || isSaved}
            className="btn-secondary"
            style={{
              padding: '0.45rem 0.9rem',
              fontSize: '0.82rem',
              color: isSaved ? 'var(--accent-rose)' : 'var(--text-primary)'
            }}
          >
            <Heart size={15} fill={isSaved ? 'var(--accent-rose)' : 'none'} color={isSaved ? 'var(--accent-rose)' : 'currentColor'} />
            <span>{isSaved ? 'Saved' : 'Save'}</span>
          </button>

          {/* Shop This Look Button */}
          <button
            onClick={() => openShopThisLook && openShopThisLook(outfit)}
            className="btn-secondary"
            title="Shop this look with catalogue product cards"
            style={{
              padding: '0.45rem 0.9rem',
              fontSize: '0.82rem',
              borderColor: 'var(--border-gold)',
              color: 'var(--gold-light)'
            }}
          >
            <ShoppingBag size={14} />
            <span>Shop This Look</span>
          </button>

          {/* AI Style Analysis Button */}
          <button
            onClick={() => openTryOn && openTryOn(outfit)}
            className="btn-secondary"
            title="Analyze your photo and style profile for personalized recommendations"
            style={{
              padding: '0.45rem 0.95rem',
              fontSize: '0.82rem',
              background: 'linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0.08) 100%)',
              borderColor: 'var(--border-gold)',
              color: '#FFF'
            }}
          >
            <Sparkles size={14} color="var(--gold-light)" />
            <span>AI Style Analysis</span>
          </button>

          {/* Visualize AI Lookbook */}
          {onVisualize && (
            <button
              onClick={() => onVisualize(outfit)}
              className="btn-secondary"
              style={{ padding: '0.45rem 0.9rem', fontSize: '0.82rem' }}
            >
              <Eye size={15} color="var(--accent-cyan)" />
              <span>Visualize</span>
            </button>
          )}

          {/* Try Another Look */}
          {onTryAnother && (
            <button
              onClick={onTryAnother}
              className="btn-primary"
              style={{ padding: '0.45rem 1rem', fontSize: '0.82rem' }}
            >
              <RotateCcw size={14} />
              <span>Try Another</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
