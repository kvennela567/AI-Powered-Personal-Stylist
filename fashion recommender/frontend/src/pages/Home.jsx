import React from 'react';
import { useApp } from '../context/AppContext';
import { 
  Sparkles, 
  ShoppingBag, 
  Sliders, 
  ThumbsUp, 
  CloudSun, 
  ArrowRight,
  CheckCircle2,
  Camera,
  Search
} from 'lucide-react';

export default function Home() {
  const { setActiveTab } = useApp();

  const features = [
    {
      icon: Search,
      title: 'Image & Product Search',
      desc: 'Connect AI recommendations directly with actual catalogue products. Search by keyword, colour, fit, material, style, and occasion with flexible multi-token matching.'
    },
    {
      icon: Sparkles,
      title: 'AI Style Analysis',
      desc: 'Upload your photo to analyze dominant clothing colors, complementary palettes, garment patterns, and styling features to receive personalized outfit recommendations from real catalogue items.'
    },
    {
      icon: Sliders,
      title: 'Personalized Styling',
      desc: 'Smart algorithms analyze your silhouette proportions, body type, preferred fits, and unique aesthetics for an individualized styling experience.'
    },
    {
      icon: ShoppingBag,
      title: 'Shop This Look & Budgets',
      desc: 'Discover complete 4-piece coordinated looks (Top, Bottom, Shoes, Accessories) with transparent itemized INR pricing within custom budget limits.'
    },
    {
      icon: ThumbsUp,
      title: 'Feedback-Based Learning',
      desc: 'Tell your stylist what you like, dislike, or swap single pieces with Mix & Match. The engine dynamically learns and refines future recommendations.'
    },
    {
      icon: CloudSun,
      title: 'Weather-Aware Outfits',
      desc: 'Adapts fabric breathability, layering, and footwear selections based on temperature, rain probability, and seasonal climates.'
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5rem', paddingBottom: '5rem' }}>
      {/* Hero Section */}
      <section style={{
        position: 'relative',
        padding: '5rem 0 3rem',
        overflow: 'hidden',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        {/* Glow Spheres */}
        <div style={{
          position: 'absolute',
          top: '-10%',
          right: '5%',
          width: '500px',
          height: '500px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(212, 175, 55, 0.12) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '0',
          left: '10%',
          width: '400px',
          height: '400px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none'
        }} />

        <div className="container" style={{ position: 'relative', textAlign: 'center', maxWidth: '880px' }}>
          <div className="badge badge-gold" style={{ marginBottom: '1.25rem' }}>
            <Sparkles size={13} />
            NEXT-GEN FASHION-TECH DISCOVERY
          </div>

          <h1 style={{
            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            fontWeight: 800,
            lineHeight: 1.15,
            marginBottom: '1.5rem',
            background: 'linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #D4AF37 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Your AI-Powered Personal Stylist
          </h1>

          <p style={{
            fontSize: '1.2rem',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            marginBottom: '2.5rem',
            maxWidth: '680px',
            margin: '0 auto 2.5rem'
          }}>
            Discover outfits personalized to your style, body type, occasion, colours and budget.
            Cohesive 4-piece looks backed by transparent styling explanations and AI visualization.
          </p>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => setActiveTab('recommendations')}
              className="btn-primary"
              style={{ padding: '0.9rem 2.2rem', fontSize: '1.05rem' }}
            >
              <Sparkles size={18} />
              <span>Get Styled</span>
            </button>

            <button
              onClick={() => setActiveTab('tryon')}
              className="btn-secondary"
              style={{ padding: '0.9rem 2rem', fontSize: '1.05rem', borderColor: 'var(--border-gold)', color: 'var(--gold-light)' }}
            >
              <Sparkles size={18} />
              <span>AI Style Analysis</span>
            </button>

            <button
              onClick={() => setActiveTab('shop')}
              className="btn-secondary"
              style={{ padding: '0.9rem 1.8rem', fontSize: '1.05rem' }}
            >
              <span>Image & Product Search</span>
              <ArrowRight size={18} />
            </button>
          </div>

          {/* Value Badges */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1.75rem',
            marginTop: '3.5rem',
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <CheckCircle2 size={16} color="var(--gold-light)" />
              <span>Zero Generic Chatbots</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <CheckCircle2 size={16} color="var(--gold-light)" />
              <span>Complete Outfits with INR ₹ Pricing</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <CheckCircle2 size={16} color="var(--gold-light)" />
              <span>Dynamic AI Visualizations</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Sections Grid per Section 3 */}
      <section className="container">
        <div className="section-header">
          <div className="badge badge-cyan" style={{ marginBottom: '0.75rem' }}>
            INTELLIGENT ARCHITECTURE
          </div>
          <h2>Engineered for Fashion Retailers</h2>
          <p>
            Bridging the gap between vast e-commerce product catalogs and confident personal wardrobe curation.
          </p>
        </div>

        <div className="grid-cards">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="glass-card"
                style={{
                  padding: '2rem 1.75rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  position: 'relative'
                }}
              >
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '12px',
                  background: 'rgba(212, 175, 55, 0.12)',
                  border: '1px solid var(--border-gold)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--gold-light)'
                }}>
                  <Icon size={24} />
                </div>

                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                  {feat.title}
                </h3>

                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                  {feat.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Interactive Quick-Start Teaser Banner */}
      <section className="container">
        <div className="glass-card" style={{
          padding: '3rem',
          borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, rgba(22, 32, 53, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
          border: '1px solid var(--border-gold)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          gap: '1.5rem',
          boxShadow: 'var(--shadow-gold)'
        }}>
          <span className="badge badge-gold">
            READY IN 60 SECONDS
          </span>
          <h2 style={{ fontSize: '2rem', maxWidth: '650px' }}>
            Personalize Your Style DNA & Unveil Curated Looks
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '580px', fontSize: '0.98rem' }}>
            Set your favorite 26+ colors, custom budget in ₹ INR, body silhouette, and preferred fits.
            Watch our dual AI engine generate 3 cohesive looks instantly.
          </p>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setActiveTab('profile')}
              className="btn-secondary"
              style={{ padding: '0.75rem 1.75rem' }}
            >
              Configure Style Profile
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className="btn-primary"
              style={{ padding: '0.75rem 1.75rem' }}
            >
              Get 3 Curated Looks
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
