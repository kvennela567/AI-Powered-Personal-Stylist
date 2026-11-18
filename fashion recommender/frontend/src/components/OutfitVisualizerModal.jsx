import React, { useState, useEffect } from 'react';
import { X, Sparkles, RefreshCw, AlertCircle, Loader2 } from 'lucide-react';
import { generateVisualization } from '../services/api';

export default function OutfitVisualizerModal({
  isOpen,
  onClose,
  outfit,
  onGenerateNewLook
}) {
  const [loading, setLoading] = useState(false);
  const [svgCanvas, setSvgCanvas] = useState('');
  const [disclaimer, setDisclaimer] = useState('');

  const loadVisualizer = async () => {
    if (!outfit) return;
    try {
      setLoading(true);
      const itemsSummary = outfit.items.map(it => `${it.product.name} (${it.product.color})`);
      const palette = outfit.items.map(it => it.product.color);

      const res = await generateVisualization({
        outfit_title: outfit.title,
        style_tag: outfit.style_tag,
        occasion: outfit.occasion,
        items_summary: itemsSummary,
        palette: palette
      });

      setSvgCanvas(res.svg_canvas || '');
      setDisclaimer(res.disclaimer || 'AI visual representation for styling preview. Not an exact brand photograph.');
    } catch (err) {
      console.error('Visualization error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && outfit) {
      loadVisualizer();
    }
  }, [isOpen, outfit]);

  if (!isOpen || !outfit) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      background: 'rgba(5, 8, 14, 0.88)',
      backdropFilter: 'blur(16px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem'
    }}>
      <div className="glass-card" style={{
        maxWidth: '860px',
        width: '100%',
        maxHeight: '92vh',
        overflowY: 'auto',
        padding: '2rem',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-medium)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="badge badge-gold" style={{ marginBottom: '0.4rem' }}>
              <Sparkles size={12} />
              AI LOOKBOOK VISUALIZER
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              AI Visual Representation: {outfit.title}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Stylistic ensemble canvas representing silhouette, color harmonies, and piece coordination.
            </p>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X size={18} />
          </button>
        </div>

        {/* Canvas Area */}
        <div style={{
          minHeight: '380px',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          background: '#0B1120',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
              <Loader2 size={36} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--gold-light)' }} />
              <div>Synthesizing AI outfit moodboard and color harmony canvas...</div>
            </div>
          ) : svgCanvas ? (
            <div 
              style={{ width: '100%', height: '100%' }}
              dangerouslySetInnerHTML={{ __html: svgCanvas }}
            />
          ) : (
            <div style={{ color: 'var(--text-muted)' }}>No visual representation generated.</div>
          )}
        </div>

        {/* Mandatory Transparency Disclaimer per Section 14 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-subtle)',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.8rem',
          color: 'var(--text-muted)'
        }}>
          <AlertCircle size={16} color="var(--gold-light)" style={{ flexShrink: 0 }} />
          <span>
            {disclaimer}
          </span>
        </div>

        {/* Actions per Section 14: Regenerate Image, Generate New Look */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          paddingTop: '0.75rem',
          borderTop: '1px solid var(--border-subtle)'
        }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Total Look Price: <strong style={{ color: 'var(--gold-light)' }}>₹{outfit.total_price?.toLocaleString('en-IN')}</strong>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={loadVisualizer}
              disabled={loading}
              className="btn-secondary"
              style={{ fontSize: '0.85rem' }}
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
              <span>Regenerate Visualization</span>
            </button>

            {onGenerateNewLook && (
              <button
                onClick={() => {
                  onClose();
                  onGenerateNewLook();
                }}
                className="btn-primary"
                style={{ fontSize: '0.85rem' }}
              >
                <Sparkles size={14} />
                <span>Generate New Look</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
