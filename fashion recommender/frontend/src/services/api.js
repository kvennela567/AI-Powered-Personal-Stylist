/**
 * API Service Client for AI Personal Stylist
 * Connects frontend React components to FastAPI backend endpoints.
 */

const API_BASE = '/api';

export async function fetchApi(endpoint, options = {}) {
  try {
    const savedUserId = typeof window !== 'undefined' ? localStorage.getItem('stylesense_user_id') : null;
    const headers = {
      'Content-Type': 'application/json',
      ...(savedUserId ? { 'X-User-Id': savedUserId } : {}),
      ...(options.headers || {})
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `API Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

// User & Profile
export const registerUser = (userData) => fetchApi('/users/register', {
  method: 'POST',
  body: JSON.stringify(userData)
});
export const loginUser = (credentials) => fetchApi('/users/login', {
  method: 'POST',
  body: JSON.stringify(credentials)
});
export const getUserProfile = () => fetchApi('/users/me');
export const getUserProfileById = (userId) => fetchApi(`/users/${userId}/profile`);
export const updateUserProfile = (profileData) => fetchApi('/users/me', {
  method: 'PUT',
  body: JSON.stringify(profileData)
});

// Products & Search
export const getProducts = (params = {}) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      query.append(key, val);
    }
  });
  const queryString = query.toString();
  return fetchApi(`/products${queryString ? `?${queryString}` : ''}`);
};

export const getProductById = (id) => fetchApi(`/products/${id}`);

// Recommendations
export const getRecommendations = (params = {}) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      query.append(key, val);
    }
  });
  const queryString = query.toString();
  return fetchApi(`/recommendations/looks${queryString ? `?${queryString}` : ''}`);
};

export const getMixMatchAlternatives = (payload) => fetchApi('/recommendations/mix-match', {
  method: 'POST',
  body: JSON.stringify(payload)
});

// Outfits (Saved & History)
export const getSavedOutfits = () => fetchApi('/outfits/saved');
export const saveOutfit = (outfitId, notes = '') => fetchApi(`/outfits/saved/${outfitId}?notes=${encodeURIComponent(notes)}`, {
  method: 'POST'
});
export const deleteSavedOutfit = (outfitId) => fetchApi(`/outfits/saved/${outfitId}`, {
  method: 'DELETE'
});
export const getHistory = (limit = 20) => fetchApi(`/outfits/history?limit=${limit}`);

// Feedback
export const submitFeedback = (payload) => fetchApi('/feedback', {
  method: 'POST',
  body: JSON.stringify(payload)
});

// Weather
export const getWeatherContext = (mode = 'mild') => fetchApi(`/weather?mode=${encodeURIComponent(mode)}`);

// Conversational AI Stylist & Visualization
export const chatWithStylist = (payload) => fetchApi('/ai/chat', {
  method: 'POST',
  body: JSON.stringify(payload)
});

export const generateVisualization = (payload) => fetchApi('/ai/visualize', {
  method: 'POST',
  body: JSON.stringify(payload)
});

// Outfit Matching
export const matchOutfitProducts = (payload) => fetchApi('/products/match-outfit', {
  method: 'POST',
  body: JSON.stringify(payload)
});

// AI Style Analysis & Recommendations
export const analyzePhoto = (payload) => fetchApi('/ai/analyze-photo', {
  method: 'POST',
  body: JSON.stringify(payload)
});

export const getRecommendationsFromAnalysis = (payload) => fetchApi('/ai/recommend-from-analysis', {
  method: 'POST',
  body: JSON.stringify(payload)
});

// Backward-compatible alias
export const virtualTryOn = (payload) => fetchApi('/ai/virtual-tryon', {
  method: 'POST',
  body: JSON.stringify(payload)
});

// Dashboard Analytics
export const getDashboardStats = () => fetchApi('/dashboard/stats');
