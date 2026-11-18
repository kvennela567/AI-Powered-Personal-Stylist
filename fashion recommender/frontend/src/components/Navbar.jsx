import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { 
  Sparkles, 
  User, 
  ShoppingBag, 
  Bookmark, 
  History, 
  LayoutDashboard, 
  Compass, 
  MessageSquareHeart, 
  CloudSun, 
  Sun, 
  CloudRain, 
  Snowflake,
  Menu,
  X,
  Camera
} from 'lucide-react';

export default function Navbar() {
  const { activeTab, setActiveTab, weatherMode, setWeatherMode, savedOutfits, userProfile } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [weatherDropdownOpen, setWeatherDropdownOpen] = useState(false);

  const navItems = [
    { id: 'home', label: 'Home', icon: Compass },
    { id: 'stylist', label: 'AI Stylist', icon: MessageSquareHeart },
    { id: 'recommendations', label: 'Recommendations', icon: Sparkles },
    { id: 'shop', label: 'Shop', icon: ShoppingBag },
    { id: 'tryon', label: 'AI Style Analysis', icon: Sparkles },
    { id: 'saved', label: `My Outfits (${savedOutfits.length})`, icon: Bookmark },
    { id: 'history', label: 'History', icon: History },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  const weatherIcons = {
    mild: CloudSun,
    hot: Sun,
    cold: Snowflake,
    rainy: CloudRain
  };
  const ActiveWeatherIcon = weatherIcons[weatherMode] || CloudSun;

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-subtle)'
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '74px'
      }}>
        {/* Brand Logo */}
        <div 
          onClick={() => setActiveTab('home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            cursor: 'pointer'
          }}
        >
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #D4AF37 0%, #B8860B 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 15px rgba(212, 175, 55, 0.3)'
          }}>
            <Sparkles size={22} color="#0A0D14" />
          </div>
          <div>
            <span style={{
              fontFamily: 'var(--font-heading)',
              fontWeight: 800,
              fontSize: '1.25rem',
              letterSpacing: '-0.02em',
              background: 'linear-gradient(135deg, #FFF 0%, #D4AF37 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              AI Personal Stylist
            </span>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              LUXURY FASHION INTELLIGENCE
            </div>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav style={{ display: 'none', gap: '0.4rem', alignItems: 'center' }} className="desktop-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.5rem 0.85rem',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.88rem',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--gold-light)' : 'var(--text-secondary)',
                  background: isActive ? 'rgba(212, 175, 55, 0.12)' : 'transparent',
                  border: isActive ? '1px solid var(--border-gold)' : '1px solid transparent',
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={15} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Tools */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Weather Selector Pill */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setWeatherDropdownOpen(!weatherDropdownOpen)}
              title="Click to change weather context for outfit styling"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.4rem 0.8rem',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                fontSize: '0.8rem'
              }}
            >
              <ActiveWeatherIcon size={15} color="var(--gold-light)" />
              <span style={{ textTransform: 'capitalize' }}>{weatherMode}</span>
            </button>

            {weatherDropdownOpen && (
              <div style={{
                position: 'absolute',
                top: '110%',
                right: 0,
                width: '180px',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                boxShadow: 'var(--shadow-lg)',
                padding: '0.5rem',
                zIndex: 200
              }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', padding: '0.25rem 0.5rem', fontWeight: 600 }}>
                  WEATHER STYLING MODE
                </div>
                {[
                  { id: 'mild', label: 'Mild (24°C)', icon: CloudSun },
                  { id: 'hot', label: 'Hot / Sunny (34°C)', icon: Sun },
                  { id: 'cold', label: 'Cold / Winter (12°C)', icon: Snowflake },
                  { id: 'rainy', label: 'Rain / Monsoon (22°C)', icon: CloudRain }
                ].map(w => {
                  const Icon = w.icon;
                  return (
                    <button
                      key={w.id}
                      onClick={() => {
                        setWeatherMode(w.id);
                        setWeatherDropdownOpen(false);
                      }}
                      style={{
                        width: '100%',
                        textAlign: 'left',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.82rem',
                        color: weatherMode === w.id ? 'var(--gold-light)' : 'var(--text-primary)',
                        background: weatherMode === w.id ? 'rgba(212, 175, 55, 0.1)' : 'transparent'
                      }}
                    >
                      <Icon size={14} />
                      {w.label}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Demo Engine Tag */}
          <span className="badge badge-gold" title="Dual Engine: Works both with live Gemini API and offline Intelligent Demo Engine">
            AI READY
          </span>

          {/* Primary Action CTA */}
          <button
            className="btn-primary"
            onClick={() => setActiveTab('recommendations')}
            style={{ padding: '0.5rem 1.1rem', fontSize: '0.85rem' }}
          >
            <Sparkles size={15} />
            <span>Get Styled</span>
          </button>

          {/* Mobile Menu Hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{ display: 'flex', padding: '0.4rem', color: 'var(--text-primary)' }}
            className="mobile-hamburger"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div style={{
          background: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-medium)',
          padding: '1rem'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setMobileMenuOpen(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.75rem 1rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.95rem',
                    color: isActive ? 'var(--gold-light)' : 'var(--text-primary)',
                    background: isActive ? 'rgba(212, 175, 55, 0.12)' : 'transparent',
                    textAlign: 'left'
                  }}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Desktop media query CSS */}
      <style>{`
        @media (min-width: 960px) {
          .desktop-nav { display: flex !important; }
          .mobile-hamburger { display: none !important; }
        }
      `}</style>
    </header>
  );
}
