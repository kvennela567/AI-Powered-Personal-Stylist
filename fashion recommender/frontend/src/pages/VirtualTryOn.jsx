import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../context/AppContext';
import {
  analyzePhoto,
  getRecommendationsFromAnalysis,
  saveOutfit,
  submitFeedback
} from '../services/api';
import { ALL_COLORS } from '../components/ColorSelector';
import {
  Upload,
  Sparkles,
  Trash2,
  AlertCircle,
  CheckCircle,
  Loader2,
  ArrowLeft,
  ShoppingBag,
  Info,
  Sliders,
  Bookmark,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Palette,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Shirt,
  User,
  Layers,
  Sparkle
} from 'lucide-react';

const ALL_OCCASIONS = [
  'Casual outing',
  'College',
  'Office',
  'Date',
  'Party',
  'Wedding',
  'Brunch',
  'Formal event',
  'Dinner'
];

const ALL_STYLES = [
  'Casual',
  'Smart casual',
  'Streetwear',
  'Formal',
  'Ethnic',
  'Minimal',
  'Athleisure'
];

const BODY_SHAPES = [
  'Hourglass',
  'Rectangle',
  'Pear / Triangle',
  'Inverted Triangle',
  'Athletic',
  'Apple'
];

export default function VirtualTryOn({
  preselectedOutfit,
  onBackToRecommendations,
  onOpenShopLook
}) {
  const { userProfile, showToast, refreshSavedOutfits, setSelectedProductDetail } = useApp();

  // Photo state
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoBase64, setPhotoBase64] = useState(null);

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [stepStage, setStepStage] = useState(1); // 1: Upload, 2: Analyzing, 3: Analyzed, 4: Recommending, 5: Ready

  // Recommendations state
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [recommendationData, setRecommendationData] = useState(null);
  const [selectedLookIndex, setSelectedLookIndex] = useState(0);
  const [savedOutfitIds, setSavedOutfitIds] = useState(new Set());
  const [likedLooks, setLikedLooks] = useState({});

  // Manual Adjustments state
  const [showEditControls, setShowEditControls] = useState(false);
  const [selectedOccasion, setSelectedOccasion] = useState(preselectedOutfit?.occasion || 'Casual outing');
  const [selectedStyle, setSelectedStyle] = useState(preselectedOutfit?.style_tag || 'Casual');
  const [selectedBodyShape, setSelectedBodyShape] = useState('');
  const [selectedColors, setSelectedColors] = useState([]);
  const [avoidColors, setAvoidColors] = useState([]);
  const [budgetMax, setBudgetMax] = useState(6000);
  const [budgetMin, setBudgetMin] = useState(1500);

  const [errorMsg, setErrorMsg] = useState(null);
  const fileInputRef = useRef(null);

  // Initialize with user profile defaults if present
  useEffect(() => {
    if (userProfile) {
      if (userProfile.body_type) setSelectedBodyShape(userProfile.body_type);
      if (userProfile.budget_max) setBudgetMax(userProfile.budget_max);
      if (userProfile.budget_min) setBudgetMin(userProfile.budget_min);
      if (userProfile.avoid_colors) setAvoidColors(userProfile.avoid_colors);
      if (userProfile.preferred_styles && userProfile.preferred_styles.length > 0) {
        setSelectedStyle(userProfile.preferred_styles[0]);
      }
    }
  }, [userProfile]);

  // Handle Photo File Selection
  const handlePhotoSelect = (file) => {
    setErrorMsg(null);
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setErrorMsg('Unsupported image format! Please upload a JPG, PNG, or WEBP photo.');
      showToast('Unsupported format. Please use JPG, PNG, or WEBP.', 'error');
      return;
    }

    // Validate size (10 MB max)
    if (file.size > 10 * 1024 * 1024) {
      const mb = (file.size / (1024 * 1024)).toFixed(1);
      setErrorMsg(`Photo is too large (${mb} MB). Maximum allowed size is 10 MB.`);
      showToast('Photo too large (max 10MB)', 'error');
      return;
    }

    setPhotoFile(file);
    setAnalysisResult(null);
    setRecommendationData(null);
    setStepStage(1);

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      setPhotoPreview(dataUrl);
      setPhotoBase64(dataUrl);
      setStepStage(1);
    };
    reader.onerror = () => {
      setErrorMsg('Failed to read image file. Please try another photo.');
      showToast('Failed to read file', 'error');
    };
    reader.readAsDataURL(file);
  };

  const handleClearPhoto = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
    setPhotoBase64(null);
    setAnalysisResult(null);
    setRecommendationData(null);
    setErrorMsg(null);
    setStepStage(1);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Step 2: Trigger AI Photo Analysis
  const handleAnalyzePhoto = async () => {
    if (!photoBase64) {
      setErrorMsg('Please upload a photo of yourself first.');
      showToast('Please upload a photo first', 'error');
      return;
    }

    try {
      setAnalyzing(true);
      setErrorMsg(null);
      setStepStage(2);

      const res = await analyzePhoto({
        photo_base64: photoBase64,
        filename: photoFile ? photoFile.name : 'photo.jpg'
      });

      setAnalysisResult(res);
      setStepStage(3);

      // Populate interactive manual controls from detected features
      const domColors = res.colors?.dominant_colors?.map(c => c.name) || [];
      const compColors = res.colors?.complementary_colors?.map(c => c.name) || [];
      setSelectedColors(Array.from(new Set([...domColors, ...compColors])));

      if (res.clothing?.style) {
        setSelectedStyle(res.clothing.style);
      }
      if (res.silhouette?.available && res.silhouette.estimated_shape) {
        setSelectedBodyShape(res.silhouette.estimated_shape);
      }

      showToast('Photo analysis complete!', 'success');

      // Automatically proceed to fetch initial recommendations
      await fetchRecommendations(res, {
        colors: Array.from(new Set([...domColors, ...compColors])),
        style: res.clothing?.style || selectedStyle,
        bodyShape: res.silhouette?.available ? res.silhouette.estimated_shape : selectedBodyShape,
        occasion: selectedOccasion,
        bMax: budgetMax,
        bMin: budgetMin
      });
    } catch (err) {
      console.error('Photo analysis error:', err);
      const msg = err.message || 'AI Photo Analysis failed. Please check your photo and try again.';
      setErrorMsg(msg);
      showToast(msg, 'error');
      setStepStage(1);
    } finally {
      setAnalyzing(false);
    }
  };

  // Step 4: Fetch recommendations based on analysis & user choices
  const fetchRecommendations = async (analysisData = analysisResult, overrides = {}) => {
    if (!analysisData) return;

    try {
      setRecommendationsLoading(true);
      setStepStage(4);
      setErrorMsg(null);

      const photoColors = analysisData.colors?.dominant_colors?.map(c => c.name) || [];
      const compColors = analysisData.colors?.complementary_colors?.map(c => c.name) || [];

      const payload = {
        photo_colors: photoColors,
        complementary_colors: compColors,
        detected_style: analysisData.clothing?.style || 'Casual',
        detected_body_shape: analysisData.silhouette?.available ? analysisData.silhouette.estimated_shape : null,
        occasion: overrides.occasion || selectedOccasion,
        budget_min: overrides.bMin !== undefined ? overrides.bMin : budgetMin,
        budget_max: overrides.bMax !== undefined ? overrides.bMax : budgetMax,
        selected_colors: overrides.colors || selectedColors,
        avoid_colors: avoidColors,
        preferred_style: overrides.style || selectedStyle
      };

      const res = await getRecommendationsFromAnalysis(payload);
      setRecommendationData(res);
      setSelectedLookIndex(0);
      setStepStage(5);
      showToast('Personalized outfit recommendations ready!', 'success');
    } catch (err) {
      console.error('Recommendation generation error:', err);
      const msg = err.message || 'Failed to generate recommendations. Please try again.';
      setErrorMsg(msg);
      showToast(msg, 'error');
      setStepStage(3);
    } finally {
      setRecommendationsLoading(false);
    }
  };

  // Handle Save Outfit
  const handleSaveOutfit = async (outfit) => {
    if (!outfit || !outfit.id) return;
    try {
      await saveOutfit(outfit.id, 'Saved from AI Style Analysis');
      setSavedOutfitIds(prev => new Set(prev).add(outfit.id));
      showToast(`'${outfit.title}' saved to My Outfits!`, 'success');
      if (refreshSavedOutfits) refreshSavedOutfits();
    } catch (err) {
      showToast(err.message || 'Could not save outfit', 'error');
    }
  };

  // Handle Like / Dislike Feedback
  const handleFeedback = async (outfit, feedbackType) => {
    if (!outfit || !outfit.id) return;
    try {
      await submitFeedback({
        outfit_id: outfit.id,
        feedback_type: feedbackType
      });
      setLikedLooks(prev => ({ ...prev, [outfit.id]: feedbackType }));
      showToast(feedbackType === 'like' ? 'Thanks! We will recommend more looks like this.' : 'Preference recorded.', 'success');
    } catch (err) {
      console.warn('Feedback submit error:', err);
    }
  };

  const activeLook = recommendationData?.looks?.[selectedLookIndex] || null;

  return (
    <div className="container" style={{ padding: '2.5rem 1.5rem 5rem' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <span className="badge badge-gold">
              <Sparkles size={12} />
              AI STYLE ANALYSIS
            </span>
            <span className="badge badge-cyan">
              AUTHENTIC CATALOGUE MATCHING
            </span>
          </div>
          <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>
            AI Style Analysis & Outfit Recommendations
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '680px' }}>
            Upload your photograph to analyze visual clothing colors, fabric patterns, and aesthetic styling.
            Receive complete personalized outfit recommendations curated from our real catalogue with INR pricing.
          </p>
        </div>

        {onBackToRecommendations && (
          <button
            onClick={onBackToRecommendations}
            className="btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}
          >
            <ArrowLeft size={15} />
            <span>Back to Recommendations</span>
          </button>
        )}
      </div>

      {/* 5-Step Visual Progress Bar */}
      <div style={{
        background: 'rgba(15, 23, 42, 0.65)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '0.85rem 1.25rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.75rem',
        marginBottom: '2rem',
        fontSize: '0.8rem'
      }}>
        {[
          { num: 1, label: 'Photo Upload' },
          { num: 2, label: 'Visual Analysis' },
          { num: 3, label: 'Features Extracted' },
          { num: 4, label: 'Catalogue Curation' },
          { num: 5, label: 'Outfits Ready' }
        ].map((s) => {
          const isDone = stepStage > s.num;
          const isCurrent = stepStage === s.num;
          return (
            <div
              key={s.num}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                color: isCurrent ? 'var(--gold-light)' : (isDone ? 'var(--accent-emerald)' : 'var(--text-muted)'),
                fontWeight: isCurrent || isDone ? 700 : 500
              }}
            >
              <div style={{
                width: '22px',
                height: '22px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                background: isCurrent ? 'rgba(212, 175, 55, 0.2)' : (isDone ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255,255,255,0.06)'),
                border: isCurrent ? '1px solid var(--gold-light)' : (isDone ? '1px solid var(--accent-emerald)' : '1px solid var(--border-subtle)')
              }}>
                {isDone ? '✓' : s.num}
              </div>
              <span>{s.label}</span>
            </div>
          );
        })}
      </div>

      {/* Error Alert */}
      {errorMsg && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          marginBottom: '1.5rem',
          fontSize: '0.85rem',
          color: '#FCA5A5'
        }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main 2-Column Grid: Photo Upload & Visual Analysis Preview */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '1.75rem',
        marginBottom: '2.5rem'
      }}>
        {/* Step 1: Upload Your Photo */}
        <div className="glass-card" style={{
          padding: '1.75rem',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
                STEP 1
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Upload Your Photo</h3>
            </div>

            {photoPreview && (
              <button
                onClick={handleClearPhoto}
                className="btn-icon"
                title="Remove photo"
                style={{ color: 'var(--accent-rose)' }}
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>

          {/* Photo Dropzone or Preview */}
          {photoPreview ? (
            <div style={{
              position: 'relative',
              borderRadius: 'var(--radius-md)',
              overflow: 'hidden',
              background: '#0B1120',
              maxHeight: '380px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid var(--border-subtle)'
            }}>
              <img
                src={photoPreview}
                alt="Uploaded style photo"
                style={{ width: '100%', height: 'auto', maxHeight: '380px', objectFit: 'contain' }}
              />
              <div style={{
                position: 'absolute',
                bottom: '12px',
                left: '12px',
                background: 'rgba(9, 13, 22, 0.85)',
                backdropFilter: 'blur(8px)',
                padding: '0.3rem 0.75rem',
                borderRadius: 'var(--radius-full)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontSize: '0.75rem',
                color: 'var(--accent-emerald)'
              }}>
                <CheckCircle size={13} />
                <span>Photo Ready for AI Analysis</span>
              </div>
            </div>
          ) : (
            <div
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handlePhotoSelect(e.dataTransfer.files[0]);
                }
              }}
              style={{
                border: '2px dashed var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                padding: '3rem 1.5rem',
                textAlign: 'center',
                cursor: 'pointer',
                background: 'rgba(255, 255, 255, 0.02)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.85rem',
                transition: 'border-color 0.2s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--gold-light)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-medium)'}
            >
              <div style={{
                width: '54px',
                height: '54px',
                borderRadius: '50%',
                background: 'rgba(212, 175, 55, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--gold-light)'
              }}>
                <Upload size={24} />
              </div>

              <div>
                <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                  Click to upload or drag photo here
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  Supports JPG, JPEG, PNG, WEBP • Max 10 MB
                </div>
              </div>

              <div style={{
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '0.4rem 0.8rem',
                borderRadius: 'var(--radius-sm)'
              }}>
                Clear full-body or upper-body photos with natural lighting work best
              </div>
            </div>
          )}

          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handlePhotoSelect(e.target.files[0]);
              }
            }}
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
          />

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className="btn-secondary"
              style={{ flex: 1, fontSize: '0.82rem' }}
            >
              {photoPreview ? 'Change Photo' : 'Select Photo'}
            </button>
            {photoPreview && (
              <button
                onClick={handleClearPhoto}
                className="btn-secondary"
                style={{ fontSize: '0.82rem', color: 'var(--accent-rose)' }}
              >
                Clear Photo
              </button>
            )}
          </div>

          {/* Action Button: Analyze My Style */}
          <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
            <button
              onClick={handleAnalyzePhoto}
              disabled={analyzing || recommendationsLoading || !photoBase64}
              className="btn-primary"
              style={{
                width: '100%',
                padding: '0.85rem',
                fontSize: '1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.6rem'
              }}
            >
              {analyzing ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  <span>Analyzing Visual Features...</span>
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  <span>Analyze My Style</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Step 2: Visual Analysis Results Card */}
        <div className="glass-card" style={{
          padding: '1.75rem',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
                STEP 2
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Image Analysis Results</h3>
            </div>

            {analysisResult && (
              <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                {analysisResult.engine_used}
              </span>
            )}
          </div>

          {analyzing && (
            <div style={{
              padding: '3rem 1rem',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '1rem'
            }}>
              <Loader2 size={36} className="animate-spin" color="var(--gold-light)" />
              <div style={{ fontSize: '0.95rem', fontWeight: 600 }}>Analyzing Photograph...</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '320px' }}>
                Evaluating lighting, extracting dominant clothing colors, inspecting fabric patterns, and assessing silhouette cues...
              </div>
            </div>
          )}

          {!analyzing && !analysisResult && (
            <div style={{
              padding: '3rem 1rem',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.85rem',
              color: 'var(--text-muted)'
            }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.04)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-muted)'
              }}>
                <Palette size={22} />
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                No Image Analyzed Yet
              </div>
              <div style={{ fontSize: '0.8rem', maxWidth: '300px' }}>
                Upload your photograph and click &ldquo;Analyze My Style&rdquo; to extract dominant colors, styling traits, and get personalized recommendations.
              </div>
            </div>
          )}

          {!analyzing && analysisResult && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
              {/* Dominant Clothing Colors */}
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem', display: 'block' }}>
                  Detected Dominant Colors
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
                  {analysisResult.colors?.dominant_colors?.map((col, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.35rem 0.65rem',
                        background: 'rgba(15, 23, 42, 0.75)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.78rem'
                      }}
                    >
                      <span style={{
                        width: '14px',
                        height: '14px',
                        borderRadius: '50%',
                        background: col.hex,
                        border: '1px solid rgba(255,255,255,0.2)'
                      }} />
                      <span style={{ fontWeight: 600 }}>{col.name}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>{col.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Complementary Palette */}
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem', display: 'block' }}>
                  Harmonizing Complementary Accents
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysisResult.colors?.complementary_colors?.map((col, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        padding: '0.3rem 0.55rem',
                        background: 'rgba(212, 175, 55, 0.08)',
                        border: '1px solid var(--border-gold)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.75rem',
                        color: 'var(--gold-light)'
                      }}
                    >
                      <span style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '3px',
                        background: col.hex
                      }} />
                      <span>{col.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Garment Style & Fabric Pattern */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '0.75rem',
                padding: '0.75rem',
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)'
              }}>
                <div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Garment Pattern
                  </div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {analysisResult.clothing?.pattern || 'Solid'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Detected Style
                  </div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--gold-light)' }}>
                    {analysisResult.clothing?.style || 'Casual'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Photo Lighting
                  </div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--accent-emerald)' }}>
                    {analysisResult.lighting_quality || 'Good'}
                  </div>
                </div>
              </div>

              {/* Skin Tone & Silhouette Section */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {/* Skin tone */}
                <div style={{
                  padding: '0.65rem 0.85rem',
                  background: 'rgba(15, 23, 42, 0.65)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.78rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      Skin-Tone Color Family:
                    </span>
                    <span style={{
                      color: analysisResult.skin_tone?.available ? 'var(--accent-emerald)' : 'var(--text-muted)',
                      fontSize: '0.7rem',
                      fontWeight: 600
                    }}>
                      {analysisResult.skin_tone?.available ? 'Detected' : 'Unavailable'}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)' }}>
                    {analysisResult.skin_tone?.available
                      ? `${analysisResult.skin_tone.tone_family} (${analysisResult.skin_tone.undertone} undertone)`
                      : analysisResult.skin_tone?.note || 'Unavailable due to photo lighting/framing. Can be customized below.'}
                  </div>
                </div>

                {/* Silhouette */}
                <div style={{
                  padding: '0.65rem 0.85rem',
                  background: 'rgba(15, 23, 42, 0.65)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.78rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      Body-Shape Silhouette:
                    </span>
                    <span style={{
                      color: analysisResult.silhouette?.available ? 'var(--accent-emerald)' : 'var(--text-muted)',
                      fontSize: '0.7rem',
                      fontWeight: 600
                    }}>
                      {analysisResult.silhouette?.available ? 'Detected' : 'Unavailable (Requires Full-Body)'}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)' }}>
                    {analysisResult.silhouette?.available
                      ? `${analysisResult.silhouette.estimated_shape} silhouette proportions`
                      : 'Not detected as a full-body standing photo. You can select your body shape manually below.'}
                  </div>
                </div>
              </div>

              {/* Toggle Manual Edit Button */}
              <button
                type="button"
                onClick={() => setShowEditControls(!showEditControls)}
                className="btn-secondary"
                style={{
                  fontSize: '0.8rem',
                  padding: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.4rem',
                  borderColor: 'var(--border-gold)',
                  color: 'var(--gold-light)'
                }}
              >
                <Sliders size={14} />
                <span>{showEditControls ? 'Hide Manual Adjustments' : 'Edit Analysis & Styling Preferences'}</span>
                {showEditControls ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Manual Adjustments & Preferences Panel */}
      {analysisResult && showEditControls && (
        <div className="glass-card" style={{
          padding: '1.75rem',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-gold)',
          marginBottom: '2.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
          animation: 'fadeIn 0.3s ease'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sliders size={16} color="var(--gold-light)" />
                <span>Fine-Tune Analysis & Recommendations</span>
              </h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Adjust occasion, budget in ₹ INR, colors, or body-shape. Image analysis supplements your choices.
              </p>
            </div>

            <button
              onClick={() => fetchRecommendations(analysisResult, {
                colors: selectedColors,
                style: selectedStyle,
                bodyShape: selectedBodyShape,
                occasion: selectedOccasion,
                bMax: budgetMax,
                bMin: budgetMin
              })}
              disabled={recommendationsLoading}
              className="btn-primary"
              style={{ fontSize: '0.85rem', padding: '0.55rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              {recommendationsLoading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              <span>Update Recommendations</span>
            </button>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1.25rem'
          }}>
            {/* Occasion */}
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Occasion:
              </label>
              <select
                value={selectedOccasion}
                onChange={(e) => setSelectedOccasion(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  padding: '0.55rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem'
                }}
              >
                {ALL_OCCASIONS.map((occ) => (
                  <option key={occ} value={occ}>{occ}</option>
                ))}
              </select>
            </div>

            {/* Style Category */}
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Preferred Style:
              </label>
              <select
                value={selectedStyle}
                onChange={(e) => setSelectedStyle(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  padding: '0.55rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem'
                }}
              >
                {ALL_STYLES.map((st) => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </div>

            {/* Body Shape Override */}
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Body Shape / Silhouette:
              </label>
              <select
                value={selectedBodyShape}
                onChange={(e) => setSelectedBodyShape(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0F172A',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  padding: '0.55rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem'
                }}
              >
                <option value="">Default / Relaxed</option>
                {BODY_SHAPES.map((bs) => (
                  <option key={bs} value={bs}>{bs}</option>
                ))}
              </select>
            </div>

            {/* Budget Max in INR */}
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'block' }}>
                Max Budget: ₹{budgetMax.toLocaleString('en-IN')}
              </label>
              <input
                type="range"
                min="2000"
                max="15000"
                step="500"
                value={budgetMax}
                onChange={(e) => setBudgetMax(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--gold-light)' }}
              />
            </div>
          </div>

          {/* Color Palettes toggle */}
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.45rem', display: 'block' }}>
              Selected Active Colors (Tap to toggle):
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem' }}>
              {ALL_COLORS.slice(0, 16).map((c) => {
                const isSelected = selectedColors.includes(c.name);
                return (
                  <button
                    key={c.name}
                    type="button"
                    onClick={() => {
                      if (isSelected) {
                        setSelectedColors(selectedColors.filter(sc => sc !== c.name));
                      } else {
                        setSelectedColors([...selectedColors, c.name]);
                      }
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                      padding: '0.3rem 0.6rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      border: isSelected ? '1px solid var(--gold-light)' : '1px solid var(--border-subtle)',
                      background: isSelected ? 'rgba(212, 175, 55, 0.18)' : 'rgba(15, 23, 42, 0.5)',
                      color: isSelected ? '#FFF' : 'var(--text-secondary)'
                    }}
                  >
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: c.hex }} />
                    <span>{c.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Step 4 & 5: Recommended Personalized Outfits Section */}
      {recommendationsLoading && (
        <div className="glass-card" style={{
          padding: '3rem 1.5rem',
          textAlign: 'center',
          borderRadius: 'var(--radius-lg)',
          marginBottom: '2.5rem'
        }}>
          <Loader2 size={44} className="animate-spin" style={{ margin: '0 auto 1.25rem', color: 'var(--gold-light)' }} />
          <h3 style={{ fontSize: '1.35rem', marginBottom: '0.5rem' }}>Curating Personalized Outfits...</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '520px', margin: '0 auto' }}>
            Matching detected visual features with authentic catalogue products, verifying INR budget allocations,
            and composing complete 4-piece coordinated looks.
          </p>
        </div>
      )}

      {recommendationData && !recommendationsLoading && activeLook && (
        <div className="glass-card" style={{
          padding: '2rem',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-gold)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.75rem',
          animation: 'fadeIn 0.4s ease'
        }}>
          {/* Section Header & Look Selector Tabs */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '1.25rem'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <span className="badge badge-gold">
                  RECOMMENDED OUTFIT LOOKS
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {recommendationData.looks.length} Tailored Looks Curated
                </span>
              </div>
              <h3 style={{ fontSize: '1.45rem', fontWeight: 800 }}>
                Personalized Outfits for {recommendationData.occasion}
              </h3>
            </div>

            {/* Look Selector Pills */}
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {recommendationData.looks.map((look, idx) => (
                <button
                  key={look.id || idx}
                  onClick={() => setSelectedLookIndex(idx)}
                  className={selectedLookIndex === idx ? 'btn-primary' : 'btn-secondary'}
                  style={{
                    fontSize: '0.82rem',
                    padding: '0.45rem 0.9rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  <span>{look.title.split(':')[0]}</span>
                  <span style={{ fontSize: '0.72rem', opacity: 0.85 }}>₹{Math.round(look.total_price).toLocaleString('en-IN')}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Active Look Meta Banner */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            padding: '1rem 1.25rem',
            background: 'rgba(212, 175, 55, 0.05)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <span className="badge badge-cyan">{activeLook.budget_tier}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--gold-light)', fontWeight: 700 }}>
                  {activeLook.match_score}% MATCH SCORE
                </span>
              </div>
              <h4 style={{ fontSize: '1.15rem', fontWeight: 800 }}>{activeLook.title}</h4>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {activeLook.occasion} • {activeLook.style_tag} styling
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Total Outfit Price
              </div>
              <div style={{
                fontSize: '1.65rem',
                fontWeight: 800,
                color: 'var(--gold-light)',
                fontFamily: 'var(--font-heading)'
              }}>
                ₹{Math.round(activeLook.total_price).toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          {/* Dynamic Explanation Rationale */}
          <div style={{
            padding: '1rem 1.25rem',
            background: 'rgba(15, 23, 42, 0.75)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.85rem',
            lineHeight: 1.6,
            color: 'var(--text-secondary)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              color: 'var(--gold-light)',
              fontWeight: 700,
              marginBottom: '0.35rem',
              fontSize: '0.82rem'
            }}>
              <Info size={15} />
              <span>Why This Outfit Matches:</span>
            </div>
            <div>{activeLook.explanation}</div>
          </div>

          {/* 4 Individual Product Cards (Actual Catalogue Products) */}
          <div>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.85rem' }}>
              Ensemble Pieces (Actual Catalogue Items)
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1.15rem'
            }}>
              {activeLook.items.map((it, idx) => {
                const p = it.product;
                if (!p) return null;
                return (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(15, 22, 38, 0.75)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      overflow: 'hidden',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.2s ease, border-color 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--gold-light)';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-subtle)';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                  >
                    {/* Real Catalogue Image */}
                    <div style={{
                      position: 'relative',
                      height: '210px',
                      overflow: 'hidden',
                      background: '#0B1120'
                    }}>
                      <img
                        src={p.image_url}
                        alt={p.name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                      <span style={{
                        position: 'absolute',
                        top: '8px',
                        left: '8px',
                        background: 'rgba(9, 13, 22, 0.85)',
                        backdropFilter: 'blur(6px)',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        color: 'var(--gold-light)',
                        textTransform: 'uppercase',
                        border: '1px solid var(--border-subtle)'
                      }}>
                        {it.role}
                      </span>
                    </div>

                    {/* Product Details */}
                    <div style={{ padding: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.4rem', flexGrow: 1 }}>
                      <div style={{
                        fontSize: '0.88rem',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        lineHeight: 1.3
                      }}>
                        {p.name}
                      </div>

                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {p.color} • {p.material} • {p.fit} fit
                      </div>

                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginTop: 'auto',
                        paddingTop: '0.6rem',
                        borderTop: '1px solid rgba(255, 255, 255, 0.05)'
                      }}>
                        <div style={{
                          fontSize: '1.05rem',
                          fontWeight: 800,
                          color: 'var(--gold-light)',
                          fontFamily: 'var(--font-heading)'
                        }}>
                          ₹{Math.round(p.price).toLocaleString('en-IN')}
                        </div>

                        <button
                          type="button"
                          onClick={() => setSelectedProductDetail(p)}
                          className="btn-secondary"
                          style={{
                            fontSize: '0.72rem',
                            padding: '0.3rem 0.6rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.3rem'
                          }}
                        >
                          <span>Details</span>
                          <ExternalLink size={12} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Outfit Actions */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-subtle)'
          }}>
            {/* Feedback Buttons */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                type="button"
                onClick={() => handleFeedback(activeLook, 'like')}
                className="btn-secondary"
                style={{
                  fontSize: '0.82rem',
                  padding: '0.45rem 0.85rem',
                  color: likedLooks[activeLook.id] === 'like' ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                  borderColor: likedLooks[activeLook.id] === 'like' ? 'var(--accent-emerald)' : 'var(--border-subtle)'
                }}
              >
                <ThumbsUp size={14} />
                <span>Like</span>
              </button>

              <button
                type="button"
                onClick={() => handleFeedback(activeLook, 'dislike')}
                className="btn-secondary"
                style={{
                  fontSize: '0.82rem',
                  padding: '0.45rem 0.85rem',
                  color: likedLooks[activeLook.id] === 'dislike' ? 'var(--accent-rose)' : 'var(--text-secondary)',
                  borderColor: likedLooks[activeLook.id] === 'dislike' ? 'var(--accent-rose)' : 'var(--border-subtle)'
                }}
              >
                <ThumbsDown size={14} />
                <span>Dislike</span>
              </button>
            </div>

            {/* Save & Shop This Look Actions */}
            <div style={{ display: 'flex', gap: '0.65rem' }}>
              <button
                type="button"
                onClick={() => handleSaveOutfit(activeLook)}
                className="btn-secondary"
                style={{
                  fontSize: '0.85rem',
                  padding: '0.55rem 1.1rem',
                  color: savedOutfitIds.has(activeLook.id) ? 'var(--gold-light)' : '#FFF',
                  borderColor: savedOutfitIds.has(activeLook.id) ? 'var(--border-gold)' : 'var(--border-subtle)'
                }}
              >
                <Bookmark size={15} />
                <span>{savedOutfitIds.has(activeLook.id) ? 'Saved' : 'Save to My Outfits'}</span>
              </button>

              {onOpenShopLook && (
                <button
                  type="button"
                  onClick={() => onOpenShopLook(activeLook)}
                  className="btn-primary"
                  style={{ fontSize: '0.85rem', padding: '0.55rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                >
                  <ShoppingBag size={15} />
                  <span>Shop This Look</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
