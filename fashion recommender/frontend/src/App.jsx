import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Stylist from './pages/Stylist';
import Recommendations from './pages/Recommendations';
import Shop from './pages/Shop';
import VirtualTryOn from './pages/VirtualTryOn';
import SavedOutfits from './pages/SavedOutfits';
import History from './pages/History';
import Dashboard from './pages/Dashboard';
import ShopThisLookModal from './components/ShopThisLookModal';
import ProductDetailModal from './components/ProductDetailModal';
import { Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

function MainContent() {
  const {
    activeTab,
    setActiveTab,
    toast,
    selectedTryOnOutfit,
    selectedShopOutfit,
    setSelectedShopOutfit,
    selectedProductDetail,
    setSelectedProductDetail,
    openTryOn,
    openShopThisLook
  } = useApp();

  const renderActivePage = () => {
    switch (activeTab) {
      case 'home':
        return <Home />;
      case 'profile':
        return <Profile />;
      case 'stylist':
        return <Stylist />;
      case 'recommendations':
        return <Recommendations />;
      case 'shop':
        return <Shop />;
      case 'style-analysis':
      case 'tryon':
        return (
          <VirtualTryOn
            preselectedOutfit={selectedTryOnOutfit}
            onBackToRecommendations={() => setActiveTab('recommendations')}
            onOpenShopLook={(outfit) => openShopThisLook(outfit)}
          />
        );
      case 'saved':
        return <SavedOutfits />;
      case 'history':
        return <History />;
      case 'dashboard':
        return <Dashboard />;
      default:
        return <Home />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />

      {/* Floating Toast Notification */}
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 2000,
          background: toast.type === 'error' ? 'rgba(239, 68, 68, 0.95)' : 'rgba(16, 185, 129, 0.95)',
          color: '#FFF',
          padding: '0.85rem 1.4rem',
          borderRadius: 'var(--radius-full)',
          boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          fontSize: '0.88rem',
          fontWeight: 600,
          animation: 'fadeIn 0.3s ease'
        }}>
          {toast.type === 'error' ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
          <span>{toast.message}</span>
        </div>
      )}

      {/* Dynamic Active View */}
      <main style={{ flexGrow: 1 }}>
        {renderActivePage()}

        {/* Global Shop This Look Modal */}
        <ShopThisLookModal
          isOpen={Boolean(selectedShopOutfit)}
          onClose={() => setSelectedShopOutfit(null)}
          outfit={selectedShopOutfit}
          onProductClick={(product) => setSelectedProductDetail(product)}
          onTryOutfit={(outfit) => {
            setSelectedShopOutfit(null);
            openTryOn(outfit);
          }}
        />

        {/* Global Product Detail Modal */}
        <ProductDetailModal
          isOpen={Boolean(selectedProductDetail)}
          onClose={() => setSelectedProductDetail(null)}
          product={selectedProductDetail}
          onTryOnProduct={(product) => {
            // Create a temporary outfit or try-on context with this piece
            const customLook = {
              id: 9999,
              title: `Look with ${product.name}`,
              style_tag: product.style,
              occasion: product.occasion,
              total_price: product.price,
              items: [{ role: 'top', product: product }]
            };
            openTryOn(customLook);
          }}
        />
      </main>

      {/* Luxury Fashion-Tech Footer */}
      <footer style={{
        background: 'rgba(9, 13, 22, 0.95)',
        borderTop: '1px solid var(--border-subtle)',
        padding: '3rem 0 2rem',
        marginTop: 'auto'
      }}>
        <div className="container" style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1.5rem',
          textAlign: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #D4AF37 0%, #B8860B 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles size={16} color="#0A0D14" />
            </div>
            <span style={{
              fontFamily: 'var(--font-heading)',
              fontWeight: 800,
              fontSize: '1.1rem',
              color: 'var(--text-primary)'
            }}>
              AI Personal Stylist
            </span>
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '600px' }}>
            Virtual personal stylist and outfit recommendation platform for e-commerce fashion retailers.
            Powered by multi-attribute scoring, dynamic preference learning, and the Google Gemini API.
          </p>

          <div style={{
            display: 'flex',
            gap: '1.5rem',
            fontSize: '0.8rem',
            color: 'var(--text-secondary)',
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <span>• Full-Stack Architecture (FastAPI + React 18)</span>
            <span>• Dual Gemini AI & Intelligent Demo Mode</span>
            <span>• Weather-Aware Fabric Algorithms</span>
            <span>• 4-Piece Look Coordination</span>
          </div>

          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem', width: '100%' }}>
            AI Personal Stylist © {new Date().getFullYear()} — Designed for Fashion-Tech E-Commerce Demonstration
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <MainContent />
    </AppProvider>
  );
}
