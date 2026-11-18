import React from 'react';
import { Star, CheckCircle, Info } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function ProductCard({ product, onSelect, actionLabel = 'Select' }) {
  const { setSelectedProductDetail } = useApp();

  if (!product) return null;

  return (
    <div
      className="glass-card"
      style={{
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: 'relative',
        transition: 'transform 0.25s ease, border-color 0.25s ease'
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
      {/* Product Image Box */}
      <div
        onClick={() => setSelectedProductDetail && setSelectedProductDetail(product)}
        style={{
          position: 'relative',
          width: '100%',
          height: '240px',
          overflow: 'hidden',
          background: '#121826',
          cursor: 'pointer'
        }}
        title="Click to view detailed specs"
      >
        <img
          src={product.image_url}
          alt={product.name}
          loading="lazy"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transition: 'transform 0.4s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.06)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1.0)'}
        />

        {/* Subcategory & Fit Tag */}
        <div style={{
          position: 'absolute',
          top: '12px',
          left: '12px',
          display: 'flex',
          gap: '0.4rem',
          flexWrap: 'wrap'
        }}>
          <span style={{
            background: 'rgba(9, 13, 22, 0.8)',
            backdropFilter: 'blur(8px)',
            color: 'var(--text-primary)',
            padding: '0.2rem 0.6rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.72rem',
            fontWeight: 600,
            border: '1px solid var(--border-subtle)'
          }}>
            {product.category} • {product.subcategory}
          </span>
          {product.fit && (
            <span style={{
              background: 'rgba(212, 175, 55, 0.2)',
              backdropFilter: 'blur(8px)',
              color: 'var(--gold-light)',
              padding: '0.2rem 0.5rem',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.72rem',
              fontWeight: 600,
              border: '1px solid var(--border-gold)'
            }}>
              {product.fit}
            </span>
          )}
        </div>

        {/* Product ID Pill */}
        <div style={{
          position: 'absolute',
          bottom: '10px',
          left: '12px',
          background: 'rgba(9, 13, 22, 0.8)',
          backdropFilter: 'blur(8px)',
          padding: '0.2rem 0.5rem',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.7rem',
          color: 'var(--text-muted)'
        }}>
          ID: <strong style={{ color: 'var(--gold-light)' }}>#{product.id}</strong>
        </div>

        {/* Rating Badge */}
        <div style={{
          position: 'absolute',
          bottom: '10px',
          right: '12px',
          background: 'rgba(9, 13, 22, 0.8)',
          backdropFilter: 'blur(8px)',
          padding: '0.2rem 0.5rem',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.25rem',
          fontSize: '0.75rem',
          color: '#F6AD55'
        }}>
          <Star size={12} fill="#F6AD55" stroke="none" />
          <span>{product.rating?.toFixed(1) || '4.8'}</span>
        </div>
      </div>

      {/* Product Content Details */}
      <div style={{
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1,
        justifyContent: 'space-between',
        gap: '0.75rem'
      }}>
        <div
          onClick={() => setSelectedProductDetail && setSelectedProductDetail(product)}
          style={{ cursor: 'pointer' }}
          title="Click to view detailed specs"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
            <h4 style={{
              fontSize: '1rem',
              fontWeight: 600,
              lineHeight: 1.3,
              color: 'var(--text-primary)'
            }}>
              {product.name}
            </h4>
          </div>

          {/* Color, Size, Material, Style */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.78rem',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            <span>Color: <strong style={{ color: 'var(--text-primary)' }}>{product.color}</strong></span>
            <span>•</span>
            <span>Size: <strong style={{ color: 'var(--text-primary)' }}>{product.size || 'M'}</strong></span>
            <span>•</span>
            <span>{product.material}</span>
          </div>

          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Style: <strong style={{ color: 'var(--gold-light)' }}>{product.style}</strong>
            {product.occasion ? ` • ${product.occasion}` : ''}
          </div>

          {/* In-Stock / Availability */}
          <div style={{ fontSize: '0.74rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            {product.availability ? (
              <span style={{ color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <CheckCircle size={12} />
                <span>Available</span>
              </span>
            ) : (
              <span style={{ color: 'var(--accent-rose)' }}>Out of Stock</span>
            )}
          </div>
        </div>

        {/* Price & Action */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: '0.75rem',
          borderTop: '1px solid var(--border-subtle)'
        }}>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>PRICE</div>
            <div style={{
              fontSize: '1.2rem',
              fontWeight: 700,
              fontFamily: 'var(--font-heading)',
              color: 'var(--gold-light)'
            }}>
              ₹{product.price?.toLocaleString('en-IN')}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.4rem' }}>
            <button
              onClick={() => setSelectedProductDetail && setSelectedProductDetail(product)}
              className="btn-secondary"
              style={{
                padding: '0.38rem 0.75rem',
                fontSize: '0.78rem',
                borderRadius: 'var(--radius-full)'
              }}
              title="View full specs"
            >
              Details
            </button>

            {onSelect && (
              <button
                onClick={() => onSelect(product)}
                className="btn-primary"
                style={{
                  padding: '0.38rem 0.85rem',
                  fontSize: '0.78rem',
                  borderRadius: 'var(--radius-full)'
                }}
              >
                {actionLabel}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
