import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, default="guest_fashionista")
    email = Column(String(255), unique=True, index=True, default="guest@fashionstylist.ai")
    created_at = Column(DateTime, default=get_utc_now)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    color_preferences = relationship("UserColorPreference", back_populates="user", cascade="all, delete-orphan")
    style_preferences = relationship("UserStylePreference", back_populates="user", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    saved_outfits = relationship("SavedOutfit", back_populates="user", cascade="all, delete-orphan")
    history = relationship("RecommendationHistory", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    preference_weights = relationship("UserPreferenceWeight", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    name = Column(String(120), default="Alex Taylor")
    age_group = Column(String(50), default="20-29")
    gender = Column(String(50), default="Female")  # Female, Male, Unisex / All
    height = Column(String(50), default="168 cm")
    weight = Column(String(50), default="58 kg")
    clothing_size = Column(String(20), default="M")
    
    # Body silhouette & physical tone
    body_type = Column(String(60), default="Hourglass")
    custom_body_type = Column(String(255), default="")
    skin_tone = Column(String(60), default="Neutral / Medium")  # Warm Fair, Warm Medium, Cool Medium, etc.

    # Gender settings
    include_unisex = Column(Boolean, default=False)
    strict_preferences = Column(Boolean, default=True)

    # Flexible Budget in INR
    budget_min = Column(Float, default=1500.0)
    budget_max = Column(Float, default=6500.0)

    # Detailed clothing cut & material nuances
    preferred_fit = Column(String(100), default="Relaxed")  # Slim Fit, Regular Fit, Relaxed Fit, Oversized, Loose Fit, Tailored Fit, Bodycon Fit, Straight Fit
    preferred_sleeve_length = Column(String(100), default="Full Sleeve")
    preferred_clothing_length = Column(String(100), default="Standard")
    preferred_materials = Column(String(255), default="Cotton, Linen, Denim")
    preferred_footwear = Column(String(255), default="Sneakers, Loafers, Heels")
    preferred_accessories = Column(String(255), default="Minimal Watch, Canvas Backpack")
    preferred_brands = Column(String(255), default="All Brands")
    disliked_clothing = Column(String(255), default="Skinny jeans, Neon colors")
    custom_style_description = Column(Text, default="I enjoy relaxed, contemporary casual looks with earthy tones and minimal accessories.")

    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="profile")


class UserColorPreference(Base):
    __tablename__ = "user_color_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    color_name = Column(String(60), nullable=False)
    preference_type = Column(String(20), nullable=False)  # 'favorite' or 'avoid'

    user = relationship("User", back_populates="color_preferences")


class UserStylePreference(Base):
    __tablename__ = "user_style_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    style_name = Column(String(80), nullable=False)

    user = relationship("User", back_populates="style_preferences")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    gender = Column(String(50), nullable=False, default="Female", index=True)  # Female, Male, Unisex
    main_category = Column(String(80), default="Western", index=True)  # Traditional, Western, Footwear, Accessories
    category = Column(String(60), nullable=False, index=True)  # Clothing, Footwear, Accessories
    subcategory = Column(String(80), nullable=False, index=True)  # Sarees, Lehengas, T-Shirts, Jeans, Sherwanis, etc.
    occasion = Column(String(120), default="Casual outing", index=True)  # Primary occasion
    supported_occasions = Column(String(500), default="Casual outing")  # Comma-separated list of compatible occasions
    clothing_type = Column(String(60), default="Topwear", index=True)  # Complete Outfit, Topwear, Bottomwear, Footwear, Accessory
    style_archetype = Column(String(80), default="Casual", index=True)  # Casual, Formal, Streetwear, Minimal, Elegant, etc.
    style = Column(String(80), default="Casual", index=True)  # Backward compatibility alias
    color = Column(String(60), nullable=False, index=True)
    color_family = Column(String(60), default="Neutral", index=True)  # Blue, Green, Black, Pink, Earth, etc.
    fabric = Column(String(100), default="Cotton", index=True)  # Cotton, Linen, Denim, Wool, Silk, etc.
    material = Column(String(100), default="Cotton")  # Backward compatibility alias
    pattern = Column(String(80), default="Solid")  # Solid, Printed, Striped, Embroidered, etc.
    fit = Column(String(60), default="Regular", index=True)  # Slim Fit, Regular Fit, Relaxed Fit, Oversized, etc.
    sleeve_length = Column(String(60), default="Full Sleeve")  # Sleeveless, Cap Sleeve, Half Sleeve, Full Sleeve, N/A
    garment_length = Column(String(60), default="Standard")  # Cropped, Short, Standard, Long, Maxi, Floor Length, N/A
    body_shape_compatibility = Column(String(100), default="All")  # Hourglass, Rectangle, Pear / Triangle, etc.
    skin_tone_compatibility = Column(String(100), default="All")  # Warm, Cool, Neutral, Fair, Medium, Deep, All
    season = Column(String(60), default="All-Season")  # Summer, Winter, Monsoon, Spring, Autumn, All-Season
    weather_suitability = Column(String(60), default="Mild")  # Hot, Warm, Mild, Cold, Rainy, All-Weather
    price = Column(Float, nullable=False, index=True)  # Price in INR
    brand = Column(String(100), default="Luxe Fashion", index=True)
    rating = Column(Float, default=4.6)
    availability = Column(Boolean, default=True)
    image_url = Column(String(500), nullable=False)
    description = Column(Text, default="")
    formality_level = Column(String(60), default="Casual")  # Casual, Smart Casual, Semi-Formal, Formal, Festive/Traditional
    outfit_compatibility = Column(String(100), default="top")  # complete_outfit, top, bottom, footwear, accessory

    outfit_items = relationship("OutfitItem", back_populates="product")


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(200), nullable=False)
    style_tag = Column(String(80), default="Casual")
    occasion = Column(String(120), default="Casual outing")
    total_price = Column(Float, nullable=False)
    match_score = Column(Float, default=92.0)
    explanation = Column(Text, default="")
    image_url = Column(String(500), default="")
    weather_context = Column(String(120), default="Mild (24°C)")
    budget_tier = Column(String(60), default="Balanced")  # Budget-Friendly, Balanced, Premium
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    saved_entries = relationship("SavedOutfit", back_populates="outfit", cascade="all, delete-orphan")
    history_entries = relationship("RecommendationHistory", back_populates="outfit", cascade="all, delete-orphan")
    feedback_entries = relationship("Feedback", back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    role = Column(String(50), nullable=False)  # 'complete_outfit', 'top', 'bottom', 'footwear', 'accessory'

    outfit = relationship("Outfit", back_populates="items")
    product = relationship("Product", back_populates="outfit_items")


class SavedOutfit(Base):
    __tablename__ = "saved_outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), index=True)
    notes = Column(String(255), default="")
    saved_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="saved_outfits")
    outfit = relationship("Outfit", back_populates="saved_entries")


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), index=True)
    gender = Column(String(50), default="Female")
    occasion = Column(String(120), default="Casual outing")
    favorite_colors = Column(String(255), default="")
    avoid_colors = Column(String(255), default="")
    aesthetics = Column(String(255), default="")
    preferred_fit = Column(String(100), default="")
    preferred_fabric = Column(String(100), default="")
    budget = Column(Float, default=5000.0)
    generated_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="history")
    outfit = relationship("Outfit", back_populates="history_entries")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), index=True)
    feedback_type = Column(String(50), nullable=False)  # like, dislike, change_item, custom_text
    item_role = Column(String(50), default="")  # top, bottom, footwear, accessory (if item swap)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="feedback")
    outfit = relationship("Outfit", back_populates="feedback_entries")


class UserPreferenceWeight(Base):
    """
    Lightweight, continuous preference learning table that stores dynamic score boosts
    derived from user likes, dislikes, and free-text feedback.
    """
    __tablename__ = "user_preference_weights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    feature_type = Column(String(50), nullable=False)  # color, style, subcategory, material
    feature_value = Column(String(100), nullable=False)
    weight_delta = Column(Float, default=0.0)  # Positive for likes, negative for dislikes
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="preference_weights")
