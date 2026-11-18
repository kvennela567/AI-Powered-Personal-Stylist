import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import ColorSelector from '../components/ColorSelector';
import BudgetSelector from '../components/BudgetSelector';
import BodyTypeSelector from '../components/BodyTypeSelector';
import { Save, Sparkles, Check, Sliders, ShieldCheck, ToggleLeft, ToggleRight, AlertCircle } from 'lucide-react';

export const ALL_STYLES = [
  'Casual', 'Formal', 'Semi-formal', 'Smart Casual', 'Streetwear',
  'Minimal', 'Oversized', 'Elegant', 'Traditional', 'Ethnic',
  'Western', 'Sporty', 'Vintage', 'Y2K', 'Trendy',
  'Classic', 'Luxury', 'Bohemian', 'Preppy', 'Athleisure'
];

export const ALL_MATERIALS = [
  'Cotton', 'Linen', 'Denim', 'Wool', 'Silk', 'Polyester', 'Leather',
  'Rayon', 'Chiffon', 'Georgette', 'Satin', 'Velvet', 'Crepe',
  'Organza', 'Khadi', 'Modal', 'Knit', 'Jersey'
];

export const ALL_FITS = [
  'Slim Fit', 'Regular Fit', 'Relaxed Fit', 'Oversized',
  'Loose Fit', 'Tailored Fit', 'Bodycon Fit', 'Straight Fit'
];

export const ALL_SLEEVES = [
  'Sleeveless', 'Cap Sleeve', 'Half Sleeve', 'Three-Quarter Sleeve',
  'Full Sleeve', 'Adjustable / Variable'
];

export const ALL_LENGTHS = [
  'Cropped', 'Short', 'Standard', 'Long', 'Maxi', 'Ankle Length', 'Floor Length'
];

export const SKIN_TONES = [
  'Warm Fair', 'Warm Medium', 'Warm Deep',
  'Cool Fair', 'Cool Medium', 'Cool Deep',
  'Neutral Fair', 'Neutral Medium', 'Neutral Deep'
];

export default function Profile() {
  const { userProfile, saveUserProfile, showToast } = useApp();
  const [formData, setFormData] = useState({
    name: 'Rhea Sharma',
    age_group: '20-29',
    gender: 'Female',
    height: '168 cm',
    weight: '58 kg',
    clothing_size: 'M',
    body_type: 'Hourglass',
    custom_body_type: '',
    skin_tone: 'Neutral / Medium',
    include_unisex: false,
    strict_preferences: true,
    budget_min: 1500,
    budget_max: 6500,
    preferred_fit: 'Relaxed Fit',
    preferred_sleeve_length: 'Full Sleeve',
    preferred_clothing_length: 'Standard',
    preferred_materials: 'Cotton, Linen, Silk',
    preferred_footwear: 'Sneakers, Loafers, Heels',
    preferred_accessories: 'Minimalist watch, Canvas backpack',
    preferred_brands: 'All Brands',
    disliked_clothing: 'Skinny jeans, Neon colors',
    custom_style_description: 'I enjoy relaxed, contemporary casual looks with earthy tones and minimal accessories.',
    favorite_colors: ['Navy', 'White', 'Beige', 'Olive', 'Black'],
    avoid_colors: ['Neon', 'Orange'],
    preferred_styles: ['Casual', 'Minimal', 'Smart Casual', 'Streetwear']
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (userProfile) {
      setFormData({
        ...userProfile,
        favorite_colors: userProfile.favorite_colors || ['Navy', 'White'],
        avoid_colors: userProfile.avoid_colors || ['Neon'],
        preferred_styles: userProfile.preferred_styles || ['Casual', 'Minimal']
      });
    }
  }, [userProfile]);

  const toggleStyle = (styleName) => {
    const current = formData.preferred_styles || [];
    if (current.includes(styleName)) {
      setFormData({ ...formData, preferred_styles: current.filter(s => s !== styleName) });
    } else {
      setFormData({ ...formData, preferred_styles: [...current, styleName] });
    }
  };

  const toggleMaterial = (mat) => {
    const currentMats = (formData.preferred_materials || '').split(',').map(m => m.trim()).filter(Boolean);
    let updated;
    if (currentMats.includes(mat)) {
      updated = currentMats.filter(m => m !== mat);
    } else {
      updated = [...currentMats, mat];
    }
    setFormData({ ...formData, preferred_materials: updated.join(', ') });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    await saveUserProfile(formData);
    setSaving(false);
  };

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 5rem', maxWidth: '960px' }}>
      <div className="section-header" style={{ textAlign: 'left', marginBottom: '2rem' }}>
        <div className="badge badge-gold" style={{ marginBottom: '0.5rem' }}>
          CENTRALIZED STYLE DNA & PREFERENCES
        </div>
        <h2>Personal Style Profile</h2>
        <p>
          Configure your gender, body proportions, colour palette, aesthetics, fits, and fabrics.
          Every feature in the application (Recommendations, AI Stylist Chatbot, Shop, Dashboard) synchronizes in real time with this centralized profile.
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* 1. Basic Information */}
        <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '1.25rem' }}>
            1. Personal Information & Gender
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.25rem',
            marginBottom: '1.25rem'
          }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                FULL NAME
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                GENDER IDENTITY (STRICT ENGINE FILTER)
              </label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: '#0F172A',
                  border: '1px solid var(--border-gold)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--gold-light)',
                  fontWeight: 600
                }}
              >
                <option value="Female">Female (Strictly Female Products)</option>
                <option value="Male">Male (Strictly Male Products)</option>
                <option value="Unisex / All">Unisex / All Genders</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                AGE GROUP
              </label>
              <select
                value={formData.age_group}
                onChange={(e) => setFormData({ ...formData, age_group: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              >
                <option value="Under 20">Under 20</option>
                <option value="20-29">20–29</option>
                <option value="30-39">30–39</option>
                <option value="40-49">40–49</option>
                <option value="50+">50+</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                HEIGHT
              </label>
              <input
                type="text"
                value={formData.height}
                onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                placeholder="E.g. 168 cm / 5'6''"
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                WEIGHT
              </label>
              <input
                type="text"
                value={formData.weight}
                onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                placeholder="E.g. 58 kg"
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                STANDARD CLOTHING SIZE
              </label>
              <select
                value={formData.clothing_size}
                onChange={(e) => setFormData({ ...formData, clothing_size: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              >
                <option value="XS">XS</option>
                <option value="S">S</option>
                <option value="M">M</option>
                <option value="L">L</option>
                <option value="XL">XL</option>
                <option value="XXL">XXL</option>
              </select>
            </div>
          </div>

          {/* Unisex Setting */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.85rem 1.25rem',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)'
          }}>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>Include Unisex Products</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                When turned off (default), Female selection retrieves Female products only, and Male selection retrieves Male products only.
              </div>
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, include_unisex: !formData.include_unisex })}
              style={{
                background: 'transparent',
                border: 'none',
                color: formData.include_unisex ? 'var(--accent-emerald)' : 'var(--text-muted)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontSize: '0.85rem',
                fontWeight: 600
              }}
            >
              {formData.include_unisex ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              <span>{formData.include_unisex ? 'Enabled' : 'Disabled (Strict)'}</span>
            </button>
          </div>
        </div>

        {/* 2. Body Silhouette & Skin Tone */}
        <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
            2. Body Silhouette & Skin Tone
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Select your closest silhouette and skin undertone to help the engine tailor garment proportions and color depth.
          </p>
          <BodyTypeSelector
            selectedBodyType={formData.body_type}
            customBodyType={formData.custom_body_type}
            onSelectBodyType={(bt) => setFormData({ ...formData, body_type: bt })}
            onChangeCustom={(val) => setFormData({ ...formData, custom_body_type: val })}
          />

          <div style={{ marginTop: '1.5rem' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
              SKIN TONE & UNDERTONE COMPATIBILITY
            </label>
            <select
              value={formData.skin_tone}
              onChange={(e) => setFormData({ ...formData, skin_tone: e.target.value })}
              style={{
                width: '100%',
                maxWidth: '360px',
                padding: '0.6rem 0.85rem',
                background: '#0F172A',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.9rem',
                color: 'var(--text-primary)'
              }}
            >
              {SKIN_TONES.map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>
        </div>

        {/* 3. Flexible Budget System */}
        <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
            3. Budget Preferences (INR ₹)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Set your target spending range. Outfits and looks will strictly respect your maximum budget limit.
          </p>
          <BudgetSelector
            budgetMin={formData.budget_min}
            budgetMax={formData.budget_max}
            onChangeMin={(min) => setFormData({ ...formData, budget_min: min })}
            onChangeMax={(max) => setFormData({ ...formData, budget_max: max })}
          />
        </div>

        {/* 4. Large Color Preferences */}
        <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
            4. Colour Palette Preferences (26+ Shades)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Select your favourite colours to anchor your outfits, and colours to avoid to strictly exclude them.
          </p>
          <ColorSelector
            favoriteColors={formData.favorite_colors || []}
            avoidColors={formData.avoid_colors || []}
            onChangeFavorites={(favs) => setFormData(prev => ({ ...prev, favorite_colors: favs }))}
            onChangeAvoids={(avoids) => setFormData(prev => ({ ...prev, avoid_colors: avoids }))}
          />
        </div>

        {/* 5. Style Preferences */}
        <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
            5. Style Archetypes (20 Aesthetics)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Select all style aesthetics that match your wardrobe identity:
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
            {ALL_STYLES.map((st) => {
              const active = (formData.preferred_styles || []).includes(st);
              return (
                <button
                  key={st}
                  type="button"
                  onClick={() => toggleStyle(st)}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.85rem',
                    fontWeight: 500,
                    background: active ? 'rgba(212, 175, 55, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                    border: active ? '1px solid var(--border-gold)' : '1px solid var(--border-subtle)',
                    color: active ? 'var(--gold-light)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {st}
                </button>
              );
            })}
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
              DESCRIBE YOUR PERSONAL STYLE (IN YOUR OWN WORDS)
            </label>
            <textarea
              rows="3"
              value={formData.custom_style_description}
              onChange={(e) => setFormData({ ...formData, custom_style_description: e.target.value })}
              placeholder="E.g. I enjoy relaxed, contemporary casual looks with earthy tones and minimal accessories."
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '0.75rem 1rem',
                fontSize: '0.9rem',
                color: 'var(--text-primary)'
              }}
            />
          </div>
        </div>

        {/* 6. Garment & Material Nuances */}
        <div className="glass-card" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h3 style={{ fontSize: '1.25rem' }}>
              6. Clothing Cut, Fits & Material Nuances
            </h3>

            {/* Strict / Flexible preference setting */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              background: 'rgba(255, 255, 255, 0.04)',
              padding: '0.35rem 0.85rem',
              borderRadius: 'var(--radius-full)',
              border: '1px solid var(--border-subtle)'
            }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Filtering Mode:</span>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, strict_preferences: !formData.strict_preferences })}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: formData.strict_preferences ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}
              >
                {formData.strict_preferences ? '🔒 Strict Fit & Fabric' : '🔓 Flexible Ranking'}
              </button>
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1.25rem',
            marginBottom: '1.5rem'
          }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                PREFERRED FIT
              </label>
              <select
                value={formData.preferred_fit}
                onChange={(e) => setFormData({ ...formData, preferred_fit: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              >
                {ALL_FITS.map(f => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                SLEEVE LENGTH
              </label>
              <select
                value={formData.preferred_sleeve_length}
                onChange={(e) => setFormData({ ...formData, preferred_sleeve_length: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              >
                {ALL_SLEEVES.map(sl => (
                  <option key={sl} value={sl}>{sl}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                GARMENT LENGTH
              </label>
              <select
                value={formData.preferred_clothing_length}
                onChange={(e) => setFormData({ ...formData, preferred_clothing_length: e.target.value })}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              >
                {ALL_LENGTHS.map(gl => (
                  <option key={gl} value={gl}>{gl}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Materials Multi-chips (18 fabrics) */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>
              PREFERRED FABRICS & MATERIALS (18 FABRICS)
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {ALL_MATERIALS.map(m => {
                const currentMats = (formData.preferred_materials || '').split(',').map(x => x.trim().toLowerCase());
                const active = currentMats.includes(m.toLowerCase());
                return (
                  <button
                    key={m}
                    type="button"
                    onClick={() => toggleMaterial(m)}
                    style={{
                      padding: '0.4rem 0.85rem',
                      borderRadius: 'var(--radius-full)',
                      fontSize: '0.82rem',
                      background: active ? 'rgba(52, 211, 153, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                      border: active ? '1px solid rgba(52, 211, 153, 0.4)' : '1px solid var(--border-subtle)',
                      color: active ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                      cursor: 'pointer'
                    }}
                  >
                    {m}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Brand Preferences & Disliked Clothing */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '1.25rem'
          }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                PREFERRED BRANDS
              </label>
              <input
                type="text"
                value={formData.preferred_brands}
                onChange={(e) => setFormData({ ...formData, preferred_brands: e.target.value })}
                placeholder="E.g. FabIndia, Manyavar, Zara, Raymond, Levi's..."
                style={{
                  width: '100%',
                  padding: '0.65rem 1rem',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                CLOTHING ITEMS YOU DISLIKE / NEVER WANT RECOMMENDED
              </label>
              <input
                type="text"
                value={formData.disliked_clothing}
                onChange={(e) => setFormData({ ...formData, disliked_clothing: e.target.value })}
                placeholder="E.g. Skinny jeans, Polyester tops, Neon sneakers..."
                style={{
                  width: '100%',
                  padding: '0.65rem 1rem',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)'
                }}
              />
            </div>
          </div>
        </div>

        {/* Save CTA */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            type="submit"
            disabled={saving}
            className="btn-primary"
            style={{ padding: '0.85rem 2.5rem', fontSize: '1rem', cursor: 'pointer' }}
          >
            <Save size={18} />
            <span>{saving ? 'Saving Profile...' : 'Save Style Profile & Synchronize'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
