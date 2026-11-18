from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ColorPreference(BaseModel):
    color_name: str
    preference_type: str = "favorite"  # 'favorite' or 'avoid'


class UserProfileSchema(BaseModel):
    name: str = "Alex Taylor"
    age_group: str = "20-29"
    gender: str = "Female"  # Female, Male, Unisex / All
    height: str = "168 cm"
    weight: Optional[str] = "58 kg"
    clothing_size: str = "M"
    body_type: str = "Hourglass"
    custom_body_type: Optional[str] = ""
    skin_tone: Optional[str] = "Neutral / Medium"
    include_unisex: Optional[bool] = False
    strict_preferences: Optional[bool] = True
    budget_min: float = 1500.0
    budget_max: float = 6500.0
    preferred_fit: str = "Relaxed"
    preferred_sleeve_length: str = "Full Sleeve"
    preferred_clothing_length: str = "Standard"
    preferred_materials: str = "Cotton, Linen, Denim"
    preferred_footwear: str = "Sneakers, Loafers, Heels"
    preferred_accessories: str = "Minimal Watch, Canvas Backpack"
    preferred_brands: Optional[str] = "All Brands"
    disliked_clothing: str = "Skinny jeans, Neon colors"
    custom_style_description: str = "I enjoy relaxed, contemporary casual looks with earthy tones."
    favorite_colors: List[str] = ["Navy", "White", "Beige", "Olive"]
    avoid_colors: List[str] = ["Neon", "Orange"]
    preferred_styles: List[str] = ["Casual", "Minimal", "Smart casual"]


class UserProfileResponse(UserProfileSchema):
    id: int
    user_id: int


class UserRegisterRequest(BaseModel):
    username: str
    email: Optional[str] = None
    name: Optional[str] = "Fashion Stylist User"


class UserLoginRequest(BaseModel):
    username: str


class UserAuthResponse(BaseModel):
    user_id: int
    id: Optional[int] = None
    username: str
    email: str
    message: str
    profile: UserProfileResponse


class ProductResponse(BaseModel):
    id: int
    name: str
    gender: Optional[str] = "Female"
    main_category: Optional[str] = "Western"
    category: str
    subcategory: str
    color: str
    color_family: Optional[str] = "Neutral"
    fabric: Optional[str] = "Cotton"
    material: Optional[str] = "Cotton"
    fit: Optional[str] = "Regular"
    pattern: Optional[str] = "Solid"
    sleeve_length: Optional[str] = "Full Sleeve"
    garment_length: Optional[str] = "Standard"
    body_shape_compatibility: Optional[str] = "All"
    skin_tone_compatibility: Optional[str] = "All"
    season: Optional[str] = "All-Season"
    weather_suitability: Optional[str] = "Mild"
    style: Optional[str] = "Casual"
    style_archetype: Optional[str] = "Casual"
    occasion: Optional[str] = "Casual outing"
    supported_occasions: Optional[str] = "Casual outing"
    clothing_type: Optional[str] = "Topwear"
    price: float
    brand: Optional[str] = "Luxe Fashion"
    rating: Optional[float] = 4.6
    availability: Optional[bool] = True
    image_url: str
    description: Optional[str] = ""
    formality_level: Optional[str] = "Casual"
    outfit_compatibility: Optional[str] = "top"

    model_config = {"from_attributes": True}


class OutfitItemQuery(BaseModel):
    role: str  # top, bottom, footwear, accessory, complete_outfit
    query: str  # e.g. "Black oversized T-shirt"


class MatchOutfitRequest(BaseModel):
    items: List[OutfitItemQuery]
    occasion: Optional[str] = None
    max_price: Optional[float] = None
    gender: Optional[str] = None


class MatchOutfitItemResult(BaseModel):
    role: str
    query: str
    matched_product: ProductResponse
    confidence_score: float
    alternatives: List[ProductResponse] = []


class MatchOutfitResponse(BaseModel):
    outfit_title: Optional[str] = "Shop This Look"
    items: List[MatchOutfitItemResult]
    total_price: float


class TryOnJsonRequest(BaseModel):
    user_photo_base64: str
    outfit_id: Optional[int] = None
    outfit_title: Optional[str] = "Selected Look"
    items: Optional[List[dict]] = []
    style_tag: Optional[str] = "Casual"
    occasion: Optional[str] = "Casual outing"
    filename: Optional[str] = "photo.jpg"


class TryOnResponse(BaseModel):
    status: str
    tryon_image_url: str
    outfit_title: str
    items_summary: List[str]
    disclaimer: str
    mode: str  # "gemini_ai" or "demo_mode"
    processing_time_sec: Optional[float] = 0.8


class OutfitItemDetail(BaseModel):
    role: str  # top, bottom, footwear, accessory, complete_outfit
    product: ProductResponse


class OutfitResponse(BaseModel):
    id: Optional[int] = None
    title: str
    style_tag: str
    occasion: str
    total_price: float
    match_score: float
    explanation: str
    image_url: str
    weather_context: str
    budget_tier: str  # Budget-Friendly, Balanced, Premium
    items: List[OutfitItemDetail]


class DominantColorItem(BaseModel):
    name: str
    hex: str
    percentage: float
    is_neutral: bool = False


class ComplementaryColorItem(BaseModel):
    name: str
    hex: str


class ColorAnalysisResult(BaseModel):
    dominant_colors: List[DominantColorItem]
    complementary_colors: List[ComplementaryColorItem]
    harmony_palette: List[str] = []


class SkinToneResult(BaseModel):
    available: bool
    undertone: Optional[str] = None
    tone_family: Optional[str] = None
    confidence: Optional[float] = None
    note: str


class SilhouetteResult(BaseModel):
    available: bool
    estimated_shape: Optional[str] = None
    confidence: Optional[float] = None
    note: str


class DetectedClothingResult(BaseModel):
    style: str
    pattern: str
    visible_categories: List[str]
    confidence: float


class AnalyzePhotoRequest(BaseModel):
    photo_base64: str
    filename: Optional[str] = "photo.jpg"


class PhotoAnalysisResponse(BaseModel):
    status: str
    colors: ColorAnalysisResult
    skin_tone: SkinToneResult
    silhouette: SilhouetteResult
    clothing: DetectedClothingResult
    styling_summary: str
    engine_used: str
    lighting_quality: str
    is_full_body: bool
    disclaimer: str


class AnalysisRecommendationRequest(BaseModel):
    photo_colors: List[str] = []
    complementary_colors: List[str] = []
    detected_style: Optional[str] = "Casual"
    detected_body_shape: Optional[str] = None
    occasion: str = "Casual outing"
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    weather: Optional[str] = "Mild (24°C)"
    selected_colors: Optional[List[str]] = None
    avoid_colors: Optional[List[str]] = None
    preferred_style: Optional[str] = None
    gender: Optional[str] = None


class AnalysisRecommendationResponse(BaseModel):
    looks: List[OutfitResponse]
    styling_rationale: str
    detected_features_used: List[str]
    engine_used: str
    occasion: str
    budget_min: float
    budget_max: float
    weather_context: str


class MultiLookResponse(BaseModel):
    looks: List[OutfitResponse]
    occasion: str
    user_budget_min: float
    user_budget_max: float
    weather_context: str
    generated_by: str
    filter_summary: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class MixMatchRequest(BaseModel):
    outfit_id: Optional[int] = None
    accepted_product_ids: List[int]
    role_to_replace: str  # "top", "bottom", "footwear", "accessory", "complete_outfit"
    occasion: Optional[str] = "Casual outing"
    budget_max: Optional[float] = 6500.0
    weather: Optional[str] = "Mild (24°C)"


class MixMatchAlternative(BaseModel):
    replacement_product: ProductResponse
    compatibility_score: float
    new_total_price: float
    explanation: str


class MixMatchResponse(BaseModel):
    role: str
    current_product_id: Optional[int] = None
    alternatives: List[MixMatchAlternative]


class FeedbackRequest(BaseModel):
    outfit_id: int
    feedback_type: str  # "like", "dislike", "save", "change_top", "change_bottom", etc.
    item_role: Optional[str] = ""
    comment: Optional[str] = ""


class FeedbackResponse(BaseModel):
    status: str
    message: str
    preference_update: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    occasion_override: Optional[str] = None
    gender_override: Optional[str] = None
    budget_max_override: Optional[float] = None
    weather_override: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    outfit_recommendation: Optional[OutfitResponse] = None
    follow_up_suggestions: List[str] = []
    engine_used: str = "Intelligent Recommendation Engine"
    active_gender: Optional[str] = None
    active_occasion: Optional[str] = None


class VisualizeRequest(BaseModel):
    outfit_title: str
    style_tag: str
    occasion: str
    items_summary: List[str]
    palette: List[str] = []


class VisualizeResponse(BaseModel):
    visualization_url: str
    svg_canvas: Optional[str] = None
    disclaimer: str = "Visualization generated as an AI stylistic preview. Not an exact brand photograph."


class WeatherContext(BaseModel):
    condition: str = "Mild / Pleasant"
    temperature_c: float = 24.0
    humidity: int = 45
    rain_probability: int = 5
    styling_advice: str = "Breathable single layers, natural cottons and open or casual shoes."


class DashboardMetricCard(BaseModel):
    label: str
    value: Any
    subtitle: str
    trend: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    total_recommendations: int
    saved_outfits_count: int
    avg_match_affinity: float
    active_gender: str
    top_occasions: List[Dict[str, Any]]
    top_colors: List[Dict[str, Any]]
    top_aesthetics: List[Dict[str, Any]]
    gender_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    recent_feedback: List[Dict[str, Any]]
    total_products_count: int
    total_products_available: int = 0
