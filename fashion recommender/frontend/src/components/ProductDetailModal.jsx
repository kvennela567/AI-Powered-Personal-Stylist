import React from 'react';
import { X, Star, CheckCircle, Tag, Layers, Palette, Scissors, ShieldCheck } from 'lucide-react';

export default function ProductDetailModal({ product, isOpen, onClose, onTryOnProduct }) {
  if (!isOpen || !product) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1100,
      background: 'rgba(5, 8, 14, 0.88)',
      backdropFilter: 'blur(16px)',
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
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-medium)',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        padding: 0,
        overflow: 'hidden'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          className="btn-icon"
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            zIndex: 10,
            background: 'rgba(9, 13, 22, 0.8)'
          }}
        >
          <X size={18} />
        </button>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 0
        }}>
          {/* Image Column */}
          <div style={{
            position: 'relative',
            height: '380px',
            background: '#0B1120',
            overflow: 'hidden'
          }}>
            <img
              src={product.image_url}
              alt={product.name}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
            <div style={{
              position: 'absolute',
              bottom: '12px',
              left: '12px',
              background: 'rgba(9, 13, 22, 0.85)',
              backdropFilter: 'blur(8px)',
              padding: '0.35rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: '0.75rem',
              color: 'var(--text-secondary)'
            }}>
              <span>Product ID:</span>
              <strong style={{ color: 'var(--gold-light)' }}>#{product.id}</strong>
            </div>

            {product.availability ? (
              <div style={{
                position: 'absolute',
                top: '16px',
                left: '16px',
                background: 'rgba(16, 185, 129, 0.9)',
                color: '#FFF',
                padding: '0.25rem 0.65rem',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.72rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}>
                <CheckCircle size={12} />
                <span>In Stock & Available</span>
              </div>
            ) : (
              <div style={{
                position: 'absolute',
                top: '16px',
                left: '16px',
                background: 'rgba(239, 68, 68, 0.9)',
                color: '#FFF',
                padding: '0.25rem 0.65rem',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.72rem',
                fontWeight: 600
              }}>
                Out of Stock
              </div>
            )}
          </div>

          {/* Details Column */}
          <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                <span className="badge badge-gold">{product.category}</span>
                <span className="badge badge-cyan">{product.subcategory}</span>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  fontSize: '0.78rem',
                  color: '#F6AD55',
                  marginLeft: 'auto'
                }}>
                  <Star size={14} fill="#F6AD55" stroke="none" />
                  <span style={{ fontWeight: 600 }}>{product.rating?.toFixed(1) || '4.8'}</span>
                </div>
              </div>

              <h3 style={{ fontSize: '1.35rem', fontWeight: 700, lineHeight: 1.3, marginBottom: '0.5rem' }}>
                {product.name}
              </h3>

              <div style={{
                fontSize: '1.6rem',
                fontWeight: 800,
                fontFamily: 'var(--font-heading)',
                color: 'var(--gold-light)'
              }}>
                ₹{product.price?.toLocaleString('en-IN')}
              </div>
            </div>

            {/* Spec Matrix */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '0.75rem',
              padding: '0.85rem',
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.8rem'
            }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Colour:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{product.color}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Size:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{product.size || 'M'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Material:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{product.material}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Fit:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{product.fit || 'Regular'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Style:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{product.style}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Occasion:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{product.occasion}</strong>
              </div>
            </div>

            {/* Description */}
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.25rem' }}>
                PRODUCT DESCRIPTION
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {product.description || "Premium garment tailored with fine detailing and breathable fabric composition for versatile daily and occasion wear."}
              </p>
            </div>

            {/* Actions */}
            <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', gap: '0.75rem' }}>
              <button
                onClick={onClose}
                className="btn-secondary"
                style={{ flex: 1, padding: '0.6rem', fontSize: '0.85rem' }}
              >
                Close
              </button>
              {onTryOnProduct && (
                <button
                  onClick={() => {
                    onClose();
                    onTryOnProduct(product);
                  }}
                  className="btn-primary"
                  style={{ flex: 1, padding: '0.6rem', fontSize: '0.85rem' }}
                >
                  Style Analysis
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
