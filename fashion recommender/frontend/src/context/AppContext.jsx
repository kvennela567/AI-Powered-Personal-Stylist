import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  getUserProfile,
  updateUserProfile as apiUpdateProfile,
  getSavedOutfits,
  getWeatherContext,
  getDashboardStats
} from '../services/api';

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  const [activeTab, setActiveTab] = useState('home');
  const [userProfile, setUserProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileVersion, setProfileVersion] = useState(1);
  const [savedOutfits, setSavedOutfits] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [activeOccasion, setActiveOccasion] = useState('College');
  const [weatherMode, setWeatherMode] = useState('mild');
  const [weatherData, setWeatherData] = useState({
    condition: 'Mild / Pleasant',
    temperature_c: 24,
    humidity: 45,
    rain_probability: 10,
    styling_advice: 'Breathable single-layer styling: light cottons, relaxed trousers, and sneakers.'
  });
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Load initial profile, saved outfits, and dashboard stats
  useEffect(() => {
    async function loadInitialData() {
      try {
        setProfileLoading(true);
        const profile = await getUserProfile();
        setUserProfile(profile);
      } catch (err) {
        console.warn('Using default demo profile fallback:', err);
        setUserProfile({
          name: 'Rhea Sharma',
          age_group: '20-29',
          gender: 'Female',
          height: '168 cm',
          weight: '58 kg',
          clothing_size: 'M',
          body_type: 'Hourglass',
          skin_tone: 'Neutral / Medium',
          custom_body_type: '',
          include_unisex: false,
          strict_preferences: true,
          budget_min: 1500,
          budget_max: 6500,
          preferred_fit: 'Relaxed',
          preferred_sleeve_length: 'Full Sleeve',
          preferred_clothing_length: 'Standard',
          preferred_materials: 'Cotton, Linen, Silk',
          preferred_footwear: 'Sneakers, Loafers, Heels',
          preferred_accessories: 'Minimalist watch, Canvas backpack',
          preferred_brands: 'All Brands',
          disliked_clothing: 'Skinny jeans, Neon colors',
          custom_style_description: 'Effortless, clean minimalist styling with comfortable relaxed fits and neutral/earthy tones.',
          favorite_colors: ['Navy', 'White', 'Beige', 'Olive', 'Black'],
          avoid_colors: ['Neon', 'Orange'],
          preferred_styles: ['Casual', 'Minimal', 'Smart casual', 'Streetwear']
        });
      } finally {
        setProfileLoading(false);
      }

      try {
        const saved = await getSavedOutfits();
        setSavedOutfits(saved);
      } catch (err) {
        console.warn('Could not load saved outfits initially:', err);
      }

      try {
        const stats = await getDashboardStats();
        setDashboardStats(stats);
      } catch (err) {
        console.warn('Could not load dashboard stats initially:', err);
      }
    }

    loadInitialData();
  }, []);

  // Update weather when mode changes
  useEffect(() => {
    async function updateWeather() {
      try {
        const w = await getWeatherContext(weatherMode);
        setWeatherData(w);
      } catch (err) {
        console.warn('Weather fetch fallback:', err);
      }
    }
    updateWeather();
  }, [weatherMode]);

  const saveUserProfile = async (updatedData) => {
    try {
      const saved = await apiUpdateProfile(updatedData);
      setUserProfile(saved);
      setProfileVersion(v => v + 1);
      showToast('Style Profile successfully updated! Recommendations synchronized.');
      refreshDashboardStats();
      return true;
    } catch (err) {
      showToast(err.message || 'Failed to update profile', 'error');
      return false;
    }
  };

  const switchActiveGender = async (newGender) => {
    if (!userProfile) return;
    const updated = { ...userProfile, gender: newGender };
    setUserProfile(updated);
    setProfileVersion(v => v + 1);
    await saveUserProfile(updated);
  };

  const refreshSavedOutfits = async () => {
    try {
      const saved = await getSavedOutfits();
      setSavedOutfits(saved);
    } catch (err) {
      console.warn('Failed to refresh saved outfits:', err);
    }
  };

  const refreshDashboardStats = async () => {
    try {
      const stats = await getDashboardStats();
      setDashboardStats(stats);
    } catch (err) {
      console.warn('Failed to refresh dashboard stats:', err);
    }
  };

  // Outfits and Modal states for Style Analysis and Shop This Look
  const [selectedTryOnOutfit, setSelectedTryOnOutfit] = useState(null);
  const [selectedShopOutfit, setSelectedShopOutfit] = useState(null);
  const [selectedProductDetail, setSelectedProductDetail] = useState(null);

  const openStyleAnalysis = (outfit = null) => {
    if (outfit) setSelectedTryOnOutfit(outfit);
    setActiveTab('tryon');
  };

  const openTryOn = (outfit) => {
    openStyleAnalysis(outfit);
  };

  const openShopThisLook = (outfit) => {
    if (outfit) setSelectedShopOutfit(outfit);
  };

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        userProfile,
        profileLoading,
        profileVersion,
        saveUserProfile,
        switchActiveGender,
        savedOutfits,
        refreshSavedOutfits,
        dashboardStats,
        refreshDashboardStats,
        activeOccasion,
        setActiveOccasion,
        weatherMode,
        setWeatherMode,
        weatherData,
        toast,
        showToast,
        selectedTryOnOutfit,
        setSelectedTryOnOutfit,
        selectedShopOutfit,
        setSelectedShopOutfit,
        selectedProductDetail,
        setSelectedProductDetail,
        openStyleAnalysis,
        openTryOn,
        openShopThisLook
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
