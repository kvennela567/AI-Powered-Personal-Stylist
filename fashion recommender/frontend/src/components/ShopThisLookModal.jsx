import React, { useState } from 'react';
import { X, Sparkles, ShoppingBag, Shirt, ArrowRight, ExternalLink, CheckCircle } from 'lucide-react';

export default function ShopThisLookModal({
  isOpen,
  onClose,
  outfit,
  onProductClick,
  onTryOutfit
}) {
  if (!isOpen || !outfit || !outfit.items) return null;

  const roleLabels = {
    top: 'TOP',
    bottom: 'BOTTOM',
    footwear: 'SHOES',
    accessory: 'ACCESSORIES'
  };

  const totalPrice = outfit.items.reduce((acc, it) => acc + (it.product ? it.product.price : 0), 0);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1050,
      background: 'rgba(5, 8, 14, 0.88)',
      backdropFilter: 'blur(16px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem'
    }}>
      <div className="glass-card" style={{
        maxWidth: '960px',
        width: '100%',
        maxHeight: '92vh',
        overflowY: 'auto',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-medium)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        padding: '2rem'
      }}>
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="badge badge-gold" style={{ marginBottom: '0.4rem' }}>
              <ShoppingBag size={12} />
              SHOP THIS LOOK
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              {outfit.title}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Coordinated pieces matched to your recommended look. Click any item to view complete catalogue specs.
            </p>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X size={18} />
          </button>
        </div>

        {/* 4 Category Breakdown Grid (TOP, BOTTOM, SHOES, ACCESSORIES) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          {['top', 'bottom', 'footwear', 'accessory'].map((roleKey) => {
            const item = outfit.items.find(it => it.role === roleKey) || outfit.items.find(it => (roleKey === 'footwear' && it.role === 'shoes'));
            const product = item?.product;

            if (!product) return null;

            return (
              <div
                key={roleKey}
                onClick={() => onProductClick && onProductClick(product)}
                style={{
                  background: 'rgba(15, 22, 38, 0.75)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  transition: 'transform 0.2s ease, border-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--gold-light)';
                  e.currentTarget.style.transform = 'translateY(-3px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                {/* Role Header Badge */}
                <div style={{
                  padding: '0.5rem 0.75rem',
                  background: 'rgba(9, 13, 22, 0.9)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderBottom: '1px solid var(--border-subtle)'
                }}>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    color: 'var(--gold-light)'
                  }}>
                    {roleLabels[roleKey]}
                  </span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                    #{product.id}
                  </span>
                </div>

                {/* Product Image */}
                <div style={{ height: '180px', position: 'relative', background: '#0B1120' }}>
                  <img
                    src={product.image_url}
                    alt={product.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  {product.availability && (
                    <span style={{
                      position: 'absolute',
                      bottom: '8px',
                      left: '8px',
                      background: 'rgba(16, 185, 129, 0.85)',
                      backdropFilter: 'blur(4px)',
                      color: '#FFF',
                      fontSize: '0.65rem',
                      fontWeight: 600,
                      padding: '0.15rem 0.45rem',
                      borderRadius: '4px'
                    }}>
                      In Stock
                    </span>
                  )}
                </div>

                {/* Product Information */}
                <div style={{ padding: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.35rem', flexGrow: 1 }}>
                  <h4 style={{
                    fontSize: '0.88rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {product.name}
                  </h4>

                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    <span>{product.color}</span> • <span>Size {product.size || 'M'}</span> • <span>{product.material}</span>
                  </div>

                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                    Style: <strong style={{ color: 'var(--text-primary)' }}>{product.style}</strong>
                  </div>

                  <div style={{
                    marginTop: 'auto',
                    paddingTop: '0.5rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderTop: '1px solid rgba(255, 255, 255, 0.05)'
                  }}>
                    <span style={{
                      fontSize: '1rem',
                      fontWeight: 700,
                      color: 'var(--gold-light)',
                      fontFamily: 'var(--font-heading)'
                    }}>
                      ₹{product.price?.toLocaleString('en-IN')}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)' }}>
                      View Details →
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Outfit Price Breakdown Summary */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.03)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
          padding: '1rem 1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
            LOOK PRICE BREAKDOWN
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.84rem' }}>
            {outfit.items.map((it, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>{it.product.name} ({it.role})</span>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>₹{it.product.price?.toLocaleString('en-IN')}</span>
              </div>
            ))}
          </div>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingTop: '0.6rem',
            borderTop: '1px solid var(--border-subtle)',
            marginTop: '0.25rem'
          }}>
            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Total Outfit Investment:</span>
            <span style={{
              fontSize: '1.4rem',
              fontWeight: 800,
              color: 'var(--gold-light)',
              fontFamily: 'var(--font-heading)'
            }}>
              ₹{totalPrice.toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        {/* Disclaimer per requirement */}
        <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
          * Notice: Matching products displayed from existing catalogue. Real retailer integration can be linked via modular service.
        </div>

        {/* Footer Actions */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          paddingTop: '0.75rem',
          borderTop: '1px solid var(--border-subtle)'
        }}>
          <button onClick={onClose} className="btn-secondary" style={{ fontSize: '0.85rem' }}>
            Back to Recommendations
          </button>

          <button
            onClick={() => {
              onClose();
              if (onTryOutfit) onTryOutfit(outfit);
            }}
            className="btn-primary"
            style={{
              padding: '0.65rem 1.4rem',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Sparkles size={16} />
            <span>AI Style Analysis</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
