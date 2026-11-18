import React, { useState, useEffect } from 'react';
import { getProducts, matchOutfitProducts } from '../services/api';
import ProductCard from '../components/ProductCard';
import { ALL_COLORS } from '../components/ColorSelector';
import { ALL_STYLES, ALL_FITS, ALL_MATERIALS } from './Profile';
import { ALL_OCCASIONS } from '../components/OccasionSelector';
import { useApp } from '../context/AppContext';
import {
  Search,
  Filter,
  Loader2,
  X,
  Sparkles,
  Shirt,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

export default function Shop() {
  const { userProfile, profileVersion, openTryOn, setSelectedProductDetail, switchActiveGender } = useApp();

  // Mode: 'browse' (Product Search) or 'match' (Find Matching Products / Outfit Matcher)
  const [activeMode, setActiveMode] = useState('browse');

  // Active Gender for Shop: default to Profile gender
  const [shopGender, setShopGender] = useState(userProfile?.gender || 'Female');

  // Search & Filter state
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [selectedOccasion, setSelectedOccasion] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('');
  const [selectedMaterial, setSelectedMaterial] = useState('');
  const [selectedFit, setSelectedFit] = useState('');
  const [maxPrice, setMaxPrice] = useState(15000);

  // Synchronize with user profile gender when profile updates
  useEffect(() => {
    if (userProfile?.gender) {
      setShopGender(userProfile.gender);
    }
  }, [userProfile?.gender, profileVersion]);

  // Outfit Matching state
  const [matchTop, setMatchTop] = useState(
    shopGender === 'Male' ? 'Navy blue formal shirt' : 'Silk embroidered saree'
  );
  const [matchBottom, setMatchBottom] = useState(
    shopGender === 'Male' ? 'Formal tailored trousers' : ''
  );
  const [matchShoes, setMatchShoes] = useState(
    shopGender === 'Male' ? 'Leather formal shoes' : 'Ethnic gold heels'
  );
  const [matchAcc, setMatchAcc] = useState(
    shopGender === 'Male' ? 'Classic leather watch' : 'Designer evening clutch'
  );
  const [matchResult, setMatchResult] = useState(null);
  const [matchingLoading, setMatchingLoading] = useState(false);

  const mainCategories = ['All', 'Traditional', 'Western', 'Footwear', 'Accessories'];

  const quickSearchQueries = shopGender === 'Male'
    ? ['sherwani', 'formal suit', 'cotton t-shirt', 'chinos', 'leather loafers', 'black oversized']
    : ['designer saree', 'lehenga', 'anarkali suit', 'silk dress', 'ethnic heels', 'oversized'];

  const fetchProductsList = async () => {
    try {
      setLoading(true);
      const params = {};
      if (shopGender && shopGender !== 'All Genders') {
        params.gender = shopGender;
      }
      params.include_unisex = Boolean(userProfile?.include_unisex);
      if (activeCategory !== 'All') params.category = activeCategory;
      if (selectedOccasion) params.occasion = selectedOccasion;
      if (search.trim()) params.search = search.trim();
      if (selectedColor) params.color = selectedColor;
      if (selectedStyle) params.style = selectedStyle;
      if (selectedMaterial) params.material = selectedMaterial;
      if (selectedFit) params.fit = selectedFit;
      if (maxPrice) params.max_price = maxPrice;

      const data = await getProducts(params);
      setProducts(data);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProductsList();
  }, [shopGender, activeCategory, selectedOccasion, selectedColor, selectedStyle, selectedMaterial, selectedFit, maxPrice, profileVersion]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchProductsList();
  };

  const handleQuickSearch = (query) => {
    setSearch(query);
    (async () => {
      try {
        setLoading(true);
        const params = { search: query };
        if (shopGender && shopGender !== 'All Genders') params.gender = shopGender;
        params.include_unisex = Boolean(userProfile?.include_unisex);
        const data = await getProducts(params);
        setProducts(data);
      } finally {
        setLoading(false);
      }
    })();
  };

  const clearFilters = () => {
    setSearch('');
    setActiveCategory('All');
    setSelectedOccasion('');
    setSelectedColor('');
    setSelectedStyle('');
    setSelectedMaterial('');
    setSelectedFit('');
    setMaxPrice(15000);
  };

  const handleFindMatchingProducts = async (e) => {
    if (e) e.preventDefault();
    try {
      setMatchingLoading(true);
      const itemsToMatch = [
        { role: 'top', query: matchTop },
        { role: 'bottom', query: matchBottom },
        { role: 'footwear', query: matchShoes },
        { role: 'accessory', query: matchAcc }
      ].filter(it => it.query.trim());

      const res = await matchOutfitProducts({
        items: itemsToMatch,
        gender: shopGender !== 'All Genders' ? shopGender : null
      });
      setMatchResult(res);
    } catch (err) {
      console.error('Outfit match error:', err);
    } finally {
      setMatchingLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 5rem' }}>
      {/* Header */}
      <div className="section-header" style={{ textAlign: 'left', marginBottom: '1.75rem' }}>
        <div className="badge badge-gold" style={{ marginBottom: '0.5rem' }}>
          CENTRALIZED FASHION CATALOGUE (1,100+ PIECES)
        </div>
        <h2>Fashion Shop & Look Matcher</h2>
        <p>
          Browse real fashion records strictly synchronized with your active gender, occasions, aesthetic archetypes, and INR pricing.
        </p>
      </div>

      {/* Gender Synchronization Strip */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        padding: '0.75rem 1.25rem',
        background: 'rgba(212, 175, 55, 0.08)',
        border: '1px solid rgba(212, 175, 55, 0.25)',
        borderRadius: 'var(--radius-md)',
        marginBottom: '1.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ShieldCheck size={18} color="var(--gold-light)" />
          <span style={{ fontSize: '0.85rem' }}>
            Catalog Filter: <strong>{shopGender} Collection</strong> {userProfile?.include_unisex ? '(+ Unisex)' : '(Strictly Isolated)'}
          </span>
        </div>

        {/* Gender Toggle Buttons */}
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          {['Female', 'Male', 'All Genders'].map(g => (
            <button
              key={g}
              type="button"
              onClick={() => {
                setShopGender(g);
                if (g !== 'All Genders' && userProfile?.gender !== g) {
                  switchActiveGender(g);
                }
              }}
              style={{
                padding: '0.35rem 0.85rem',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.8rem',
                fontWeight: shopGender === g ? 700 : 500,
                background: shopGender === g ? 'var(--gold-primary)' : 'rgba(255, 255, 255, 0.05)',
                color: shopGender === g ? '#0A0D14' : 'var(--text-secondary)',
                border: shopGender === g ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                cursor: 'pointer'
              }}
            >
              {g === 'Female' ? '👗 Female' : (g === 'Male' ? '👔 Male' : '✨ All')}
            </button>
          ))}
        </div>
      </div>

      {/* Main Mode Selector Tabs */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '1rem',
        marginBottom: '2rem'
      }}>
        <button
          onClick={() => setActiveMode('browse')}
          style={{
            padding: '0.65rem 1.4rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.92rem',
            fontWeight: activeMode === 'browse' ? 700 : 500,
            background: activeMode === 'browse' ? 'linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(212, 175, 55, 0.1) 100%)' : 'rgba(255, 255, 255, 0.04)',
            border: activeMode === 'browse' ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
            color: activeMode === 'browse' ? 'var(--gold-light)' : 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <Search size={15} />
          <span>Product Catalogue Search</span>
        </button>

        <button
          onClick={() => {
            setActiveMode('match');
            if (!matchResult) handleFindMatchingProducts();
          }}
          style={{
            padding: '0.65rem 1.4rem',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.92rem',
            fontWeight: activeMode === 'match' ? 700 : 500,
            background: activeMode === 'match' ? 'linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(212, 175, 55, 0.1) 100%)' : 'rgba(255, 255, 255, 0.04)',
            border: activeMode === 'match' ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
            color: activeMode === 'match' ? 'var(--gold-light)' : 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <Sparkles size={15} />
          <span>Shop This Look (Outfit Matcher)</span>
        </button>
      </div>

      {/* ================= MODE 1: BROWSE & IMAGE SEARCH ================= */}
      {activeMode === 'browse' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2.5rem' }}>
          {/* Search Bar & Categories */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
            {/* Category Tabs */}
            <div style={{
              display: 'flex',
              gap: '0.4rem',
              background: 'rgba(255, 255, 255, 0.05)',
              padding: '0.25rem',
              borderRadius: 'var(--radius-full)',
              width: 'fit-content',
              flexWrap: 'wrap'
            }}>
              {mainCategories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setActiveCategory(cat)}
                  style={{
                    padding: '0.45rem 1.25rem',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.88rem',
                    fontWeight: activeCategory === cat ? 600 : 400,
                    background: activeCategory === cat ? 'linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(212, 175, 55, 0.1) 100%)' : 'transparent',
                    border: activeCategory === cat ? '1px solid var(--border-gold)' : '1px solid transparent',
                    color: activeCategory === cat ? 'var(--gold-light)' : 'var(--text-secondary)',
                    cursor: 'pointer'
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Keyword Search Input */}
            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', minWidth: '320px', flexGrow: 1, maxWidth: '500px' }}>
              <div style={{ position: 'relative', width: '100%' }}>
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '12px' }} />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={`Search ${shopGender} fashion: 'saree', 'sherwani', 'linen shirt'...`}
                  style={{
                    width: '100%',
                    padding: '0.65rem 1rem 0.65rem 2.5rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.88rem',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>
              <button type="submit" className="btn-secondary" style={{ padding: '0.65rem 1.2rem', borderRadius: 'var(--radius-full)' }}>
                Search
              </button>
            </form>
          </div>

          {/* Quick Search Suggestions Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>POPULAR SEARCHES:</span>
            {quickSearchQueries.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleQuickSearch(q)}
                style={{
                  padding: '0.25rem 0.65rem',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.74rem',
                  background: search === q ? 'rgba(212, 175, 55, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                  border: search === q ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                  color: search === q ? 'var(--gold-light)' : 'var(--text-secondary)',
                  cursor: 'pointer'
                }}
              >
                "{q}"
              </button>
            ))}
          </div>

          {/* Multi-Faceted Filters Strip (Occasion, Colour, Style, Material, Fit, Price) */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            flexWrap: 'wrap',
            background: 'rgba(255, 255, 255, 0.02)',
            padding: '0.85rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <Filter size={14} />
              <span>FACETS:</span>
            </div>

            {/* Occasion Filter */}
            <select
              value={selectedOccasion}
              onChange={(e) => setSelectedOccasion(e.target.value)}
              style={{
                background: '#0F172A',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                padding: '0.35rem 0.65rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem'
              }}
            >
              <option value="">All 27 Occasions</option>
              {ALL_OCCASIONS.map(occ => (
                <option key={occ} value={occ}>{occ}</option>
              ))}
            </select>

            {/* Color Filter */}
            <select
              value={selectedColor}
              onChange={(e) => setSelectedColor(e.target.value)}
              style={{
                background: '#0F172A',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                padding: '0.35rem 0.65rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem'
              }}
            >
              <option value="">All 26+ Colors</option>
              {ALL_COLORS.map(c => (
                <option key={c.name} value={c.name}>{c.name}</option>
              ))}
            </select>

            {/* Style Filter */}
            <select
              value={selectedStyle}
              onChange={(e) => setSelectedStyle(e.target.value)}
              style={{
                background: '#0F172A',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                padding: '0.35rem 0.65rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem'
              }}
            >
              <option value="">All 20 Aesthetics</option>
              {ALL_STYLES.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            {/* Material Filter */}
            <select
              value={selectedMaterial}
              onChange={(e) => setSelectedMaterial(e.target.value)}
              style={{
                background: '#0F172A',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                padding: '0.35rem 0.65rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem'
              }}
            >
              <option value="">All 18 Fabrics</option>
              {ALL_MATERIALS.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>

            {/* Fit Filter */}
            <select
              value={selectedFit}
              onChange={(e) => setSelectedFit(e.target.value)}
              style={{
                background: '#0F172A',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                padding: '0.35rem 0.65rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.8rem'
              }}
            >
              <option value="">All Fits</option>
              {ALL_FITS.map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>

            {/* Max Price Slider */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Max:</span>
              <span style={{ color: 'var(--gold-light)', fontWeight: 600 }}>₹{maxPrice.toLocaleString('en-IN')}</span>
              <input
                type="range"
                min="500"
                max="20000"
                step="500"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
                style={{ width: '90px', accentColor: 'var(--gold-primary)' }}
              />
            </div>

            {(selectedColor || selectedStyle || selectedMaterial || selectedFit || selectedOccasion || search || maxPrice < 15000) && (
              <button
                onClick={clearFilters}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  fontSize: '0.78rem',
                  color: 'var(--accent-rose)',
                  cursor: 'pointer',
                  marginLeft: 'auto'
                }}
              >
                <X size={13} />
                <span>Reset Filters</span>
              </button>
            )}
          </div>

          {/* Product Results Grid */}
          {loading ? (
            <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Loader2 size={36} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--gold-light)' }} />
              <div>Filtering catalogue products...</div>
            </div>
          ) : products.length === 0 ? (
            <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', borderRadius: 'var(--radius-md)' }}>
              <h3>No matching products found</h3>
              <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                No {shopGender} products match the selected filters. Rather than showing unrelated categories, we keep results strictly filtered.
              </p>
              <button onClick={clearFilters} className="btn-secondary" style={{ marginTop: '1rem' }}>
                Reset Filters
              </button>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Showing <strong>{products.length}</strong> {shopGender} products matching search criteria
              </div>
              <div className="grid-cards">
                {products.map(p => (
                  <ProductCard
                    key={p.id}
                    product={p}
                    onOpenTryOn={(prod) => openTryOn({
                      title: prod.name,
                      style_tag: prod.style_archetype || prod.style,
                      occasion: prod.occasion,
                      items: [{ role: prod.clothing_type || 'piece', ...prod }]
                    })}
                    onOpenDetail={(prod) => setSelectedProductDetail(prod)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ================= MODE 2: OUTFIT MATCHER (SHOP THIS LOOK) ================= */}
      {activeMode === 'match' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
              Outfit Matcher — Shop Any Style Look ({shopGender})
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              Enter garment piece descriptions to discover perfectly matched products available in our real catalogue.
            </p>

            <form onSubmit={handleFindMatchingProducts} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                  TOPWEAR / MAIN GARMENT
                </label>
                <input
                  type="text"
                  value={matchTop}
                  onChange={(e) => setMatchTop(e.target.value)}
                  placeholder="E.g. Black oversized cotton T-shirt"
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                  BOTTOMWEAR
                </label>
                <input
                  type="text"
                  value={matchBottom}
                  onChange={(e) => setMatchBottom(e.target.value)}
                  placeholder="E.g. Blue straight-fit jeans"
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                  FOOTWEAR
                </label>
                <input
                  type="text"
                  value={matchShoes}
                  onChange={(e) => setMatchShoes(e.target.value)}
                  placeholder="E.g. White sneakers / Leather loafers"
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem' }}>
                  ACCESSORY
                </label>
                <input
                  type="text"
                  value={matchAcc}
                  onChange={(e) => setMatchAcc(e.target.value)}
                  placeholder="E.g. Minimalist watch"
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>

              <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <button
                  type="submit"
                  disabled={matchingLoading}
                  className="btn-primary"
                  style={{ padding: '0.7rem 1.8rem', fontSize: '0.9rem' }}
                >
                  {matchingLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                  <span>Match Catalogue Pieces</span>
                </button>
              </div>
            </form>
          </div>

          {/* Matching Results */}
          {matchingLoading ? (
            <div style={{ padding: '4rem', textAlign: 'center' }}>
              <Loader2 size={36} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--gold-light)' }} />
              <div>Matching outfit items against 1,100+ catalogue pieces...</div>
            </div>
          ) : matchResult && matchResult.items && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem' }}>{matchResult.outfit_title}</h3>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    Matched {matchResult.items.length} pieces • Total Ensemble: ₹{matchResult.total_price.toLocaleString('en-IN')}
                  </div>
                </div>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                gap: '1.5rem'
              }}>
                {matchResult.items.map((item, idx) => (
                  <div key={idx} className="glass-card" style={{ padding: '1.25rem', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="badge badge-gold">{item.role.toUpperCase()}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                        {item.confidence_score}% Match
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                      Queried: "{item.query}"
                    </div>

                    <ProductCard
                      product={item.matched_product}
                      onOpenDetail={(prod) => setSelectedProductDetail(prod)}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
