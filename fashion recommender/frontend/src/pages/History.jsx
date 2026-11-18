import React, { useState, useEffect } from 'react';
import { getHistory } from '../services/api';
import OutfitCard from '../components/OutfitCard';
import OutfitVisualizerModal from '../components/OutfitVisualizerModal';
import { useApp } from '../context/AppContext';
import { History as HistoryIcon, Sparkles, Loader2, Clock } from 'lucide-react';

export default function History() {
  const { setActiveTab } = useApp();
  const [historyLooks, setHistoryLooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOutfit, setSelectedOutfit] = useState(null);
  const [visualizeOpen, setVisualizeOpen] = useState(false);

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await getHistory(25);
        setHistoryLooks(data);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  const handleOpenVisualize = (outfit) => {
    setSelectedOutfit(outfit);
    setVisualizeOpen(true);
  };

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 5rem' }}>
      {/* Header */}
      <div className="section-header" style={{ textAlign: 'left', marginBottom: '2rem' }}>
        <div className="badge badge-gold" style={{ marginBottom: '0.5rem' }}>
          RECOMMENDATION TIMELINE
        </div>
        <h2>Recommendation History</h2>
        <p>
          Chronological record of previously generated outfit recommendations.
          Review styling rationales, give feedback, or generate similar aesthetics.
        </p>
      </div>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Loader2 size={36} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--gold-light)' }} />
          <div>Retrieving past recommendation history...</div>
        </div>
      ) : historyLooks.length === 0 ? (
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
            <Clock size={28} />
          </div>
          <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>No History Logged Yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            As you generate looks via the AI Stylist or Recommendation Engine, your timeline will appear here.
          </p>
          <button onClick={() => setActiveTab('recommendations')} className="btn-primary">
            <Sparkles size={16} />
            <span>Curate First Outfit</span>
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {historyLooks.map((outfit, idx) => (
            <div key={outfit.id || idx}>
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
