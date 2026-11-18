"""
Centralized Recommendation Engine for AI Personal Stylist for E-Commerce.

Single source of truth used across:
- Recommendations page (multi-look curation)
- AI Stylist Chatbot (context-aware outfit retrieval)
- Shop module (catalogue filtering & outfit matching)
- AI Style Analysis (photo-feature personalized curation)
- History and Dashboard analytics

Two-Stage Process:
1. Hard Filtering: Gender, Occasion, Avoided Colours, Favourite Colours,
   Style Archetype, Strict Fits / Sleeves / Lengths / Fabrics, Budget, Availability.
2. Personalization Ranking: Body Shape, Skin Tone, Colour Suitability,
   Personal Style Description, Brand Affinity, Weather, Feedback Weights.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.entities import (
    Product,
    UserProfile,
    UserColorPreference,
    UserStylePreference,
    UserPreferenceWeight,
    Outfit,
    OutfitItem,
    RecommendationHistory,
    Feedback
)

# Standard Color Family Mapping
COLOR_FAMILIES = {
    "black": "black",
    "white": "neutral",
    "grey": "neutral",
    "gray": "neutral",
    "navy": "blue",
    "blue": "blue",
    "sky blue": "blue",
    "royal blue": "blue",
    "red": "red",
    "maroon": "red",
    "pink": "pink",
    "rose": "pink",
    "purple": "purple",
    "lavender": "purple",
    "green": "green",
    "olive": "green",
    "emerald": "green",
    "yellow": "yellow",
    "mustard": "yellow",
    "orange": "orange",
    "brown": "earth",
    "beige": "neutral",
    "cream": "neutral",
    "tan": "earth",
    "khaki": "earth",
    "burgundy": "red",
    "teal": "blue",
    "turquoise": "blue",
    # Custom shades mapping
    "sage green": "green",
    "terracotta": "earth",
    "peach": "pink",
    "coral": "pink",
    "wine": "red",
    "dusty pink": "pink",
    "champagne": "neutral",
    "mint green": "green",
    "lilac": "purple"
}

# Neutral colours safe for footwear and accessories
NEUTRAL_COLORS = {"black", "white", "grey", "gray", "beige", "cream", "tan", "brown", "navy", "gold", "silver"}


def normalize_color(color_str: str) -> str:
    """Normalize color name to lowercase trimmed."""
    if not color_str:
        return ""
    return color_str.strip().lower()


def get_color_family(color_str: str) -> str:
    norm = normalize_color(color_str)
    return COLOR_FAMILIES.get(norm, norm)


# =========================================================================
# OCCASION & GENDER RULES MATRIX
# Strictly governs appropriate categories per occasion and gender
# =========================================================================
OCCASION_MATRIX = {
    "office": {
        "female": {
            "allowed_tops": ["Shirts", "Blazers", "Tops"],
            "allowed_bottoms": ["Trousers", "Skirts"],
            "allowed_complete": ["Dresses", "Co-ord sets"],
            "allowed_footwear": ["Heels", "Flats", "Loafers"],
            "allowed_accessories": ["Handbags", "Watches", "Belts"],
            "blocked": [
                "Sarees", "Designer sarees", "Lehengas", "Kurtis", "Salwar suits",
                "Sharara sets", "Palazzo sets", "Ethnic gowns", "Indo-western outfits",
                "Jeans", "T-shirts", "Basic T-shirts", "Hoodies", "Sweatshirts",
                "Sneakers", "Caps", "Backpacks", "Ethnic footwear", "Clutches", "Dupattas"
            ]
        },
        "male": {
            "allowed_tops": ["Formal shirts", "Blazers"],
            "allowed_bottoms": ["Formal trousers", "Chinos"],
            "allowed_complete": ["Suits"],
            "allowed_footwear": ["Formal shoes", "Loafers"],
            "allowed_accessories": ["Watches", "Belts", "Ties", "Pocket squares", "Wallets"],
            "blocked": [
                "Sherwanis", "Kurta pyjama sets", "Nehru jackets", "Pathani suits",
                "Traditional waistcoats", "Ethnic sets", "Indo-western outfits",
                "Jeans", "T-shirts", "Casual shirts", "Polo T-shirts", "Hoodies",
                "Sneakers", "Caps", "Backpacks", "Ethnic footwear", "Sandals"
            ]
        }
    },
    "college": {
        "female": {
            "allowed_tops": ["Tops", "Shirts", "Casual wear"],
            "allowed_bottoms": ["Jeans", "Trousers", "Skirts"],
            "allowed_complete": ["Dresses", "Jumpsuits", "Co-ord sets"],
            "allowed_footwear": ["Sneakers", "Flats", "Sandals", "Boots"],
            "allowed_accessories": ["Backpacks", "Watches", "Handbags", "Sunglasses"],
            "blocked": [
                "Sarees", "Designer sarees", "Lehengas", "Salwar suits", "Anarkali suits",
                "Sharara sets", "Palazzo sets", "Ethnic gowns", "Kurtis",
                "Heels", "Ethnic footwear", "Clutches", "Dupattas", "Necklaces", "Earrings"
            ]
        },
        "male": {
            "allowed_tops": ["T-shirts", "Casual shirts", "Polo T-shirts", "Hoodies"],
            "allowed_bottoms": ["Jeans", "Chinos"],
            "allowed_complete": ["Co-ord sets"],
            "allowed_footwear": ["Sneakers", "Loafers", "Sandals", "Boots"],
            "allowed_accessories": ["Backpacks", "Caps", "Watches", "Sunglasses", "Wallets"],
            "blocked": [
                "Sherwanis", "Kurta pyjama sets", "Nehru jackets", "Pathani suits",
                "Traditional waistcoats", "Ethnic sets", "Indo-western outfits",
                "Formal shirts", "Blazers", "Suits", "Formal trousers",
                "Formal shoes", "Ties", "Pocket squares", "Ethnic footwear"
            ]
        }
    },
    "festival": {
        "female": {
            "allowed_tops": [],
            "allowed_bottoms": [],
            "allowed_complete": [
                "Sarees", "Designer sarees", "Lehengas", "Anarkali suits",
                "Sharara sets", "Palazzo sets", "Ethnic gowns", "Indo-western outfits", "Salwar suits"
            ],
            "allowed_footwear": ["Ethnic footwear", "Heels", "Flats", "Sandals"],
            "allowed_accessories": ["Earrings", "Necklaces", "Clutches", "Dupattas", "Handbags", "Watches"],
            "blocked": [
                "Jeans", "T-shirts", "Basic T-shirts", "Hoodies", "Sweatshirts",
                "Shorts", "Casual wear", "Shirts", "Blazers", "Trousers",
                "Sneakers", "Boots", "Caps", "Backpacks"
            ]
        },
        "male": {
            "allowed_tops": ["Nehru jackets", "Traditional waistcoats"],
            "allowed_bottoms": ["Chinos", "Formal trousers"],
            "allowed_complete": [
                "Kurta pyjama sets", "Sherwanis", "Pathani suits", "Ethnic sets", "Indo-western outfits"
            ],
            "allowed_footwear": ["Ethnic footwear", "Loafers", "Formal shoes"],
            "allowed_accessories": ["Watches", "Pocket squares", "Wallets"],
            "blocked": [
                "Jeans", "T-shirts", "Casual shirts", "Polo T-shirts", "Hoodies",
                "Sneakers", "Boots", "Caps", "Backpacks", "Ties"
            ]
        }
    },
    "formal event": {
        "female": {
            "allowed_tops": ["Blazers", "Shirts", "Tops"],
            "allowed_bottoms": ["Trousers", "Skirts"],
            "allowed_complete": ["Dresses", "Co-ord sets", "Ethnic gowns", "Designer sarees"],
            "allowed_footwear": ["Heels", "Flats"],
            "allowed_accessories": ["Clutches", "Handbags", "Watches", "Earrings", "Necklaces"],
            "blocked": [
                "Jeans", "T-shirts", "Basic T-shirts", "Hoodies", "Sweatshirts",
                "Shorts", "Casual wear", "Kurtis", "Salwar suits", "Palazzo sets",
                "Sneakers", "Caps", "Backpacks", "Sandals", "Boots"
            ]
        },
        "male": {
            "allowed_tops": ["Blazers", "Formal shirts"],
            "allowed_bottoms": ["Formal trousers"],
            "allowed_complete": ["Suits", "Indo-western outfits"],
            "allowed_footwear": ["Formal shoes", "Loafers"],
            "allowed_accessories": ["Ties", "Pocket squares", "Watches", "Belts"],
            "blocked": [
                "Jeans", "Chinos", "T-shirts", "Casual shirts", "Polo T-shirts",
                "Hoodies", "Casual wear", "Sneakers", "Sandals", "Boots",
                "Caps", "Backpacks", "Nehru jackets"
            ]
        }
    },
    "gym": {
        "female": {
            "allowed_tops": ["Tops", "Casual wear"],
            "allowed_bottoms": ["Trousers", "Jeans", "Chinos"],
            "allowed_complete": [],
            "allowed_footwear": ["Sneakers", "Sandals"],
            "allowed_accessories": ["Watches", "Caps", "Backpacks", "Sunglasses"],
            "blocked": [
                "Sarees", "Designer sarees", "Lehengas", "Kurtis", "Salwar suits",
                "Sharara sets", "Palazzo sets", "Ethnic gowns", "Indo-western outfits",
                "Heels", "Formal shoes", "Ethnic footwear", "Flats",
                "Clutches", "Necklaces", "Earrings", "Dupattas"
            ]
        },
        "male": {
            "allowed_tops": ["T-shirts", "Polo T-shirts", "Hoodies"],
            "allowed_bottoms": ["Chinos", "Jeans", "Formal trousers"],
            "allowed_complete": [],
            "allowed_footwear": ["Sneakers", "Sandals"],
            "allowed_accessories": ["Caps", "Watches", "Backpacks", "Sunglasses", "Wallets"],
            "blocked": [
                "Sherwanis", "Kurta pyjama sets", "Nehru jackets", "Pathani suits",
                "Formal shirts", "Blazers", "Suits", "Formal shoes", "Loafers",
                "Ties", "Pocket squares", "Ethnic footwear"
            ]
        }
    }
}


def get_canonical_occasion(occasion: str) -> str:
    """Map user/query occasion string to standardized canonical occasion key."""
    occ = (occasion or "Casual outing").strip().lower()
    if any(k in occ for k in ["office", "business", "interview"]):
        return "office"
    if any(k in occ for k in ["college", "university"]):
        return "college"
    if any(k in occ for k in ["festival", "religious", "wedding", "engagement", "family gathering"]):
        return "festival"
    if any(k in occ for k in ["formal event", "semi-formal event"]):
        return "formal event"
    if any(k in occ for k in ["gym", "sports"]):
        return "gym"
    return "casual"


class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_user_profile_context(self, user_id: int) -> Dict[str, Any]:
        """Fetch comprehensive user profile DNA and preferences."""
        profile = self.db.query(UserProfile).filter_by(user_id=user_id).first()
        color_prefs = self.db.query(UserColorPreference).filter_by(user_id=user_id).all()
        style_prefs = self.db.query(UserStylePreference).filter_by(user_id=user_id).all()
        pref_weights = self.db.query(UserPreferenceWeight).filter_by(user_id=user_id).all()

        fav_colors = [cp.color_name for cp in color_prefs if cp.preference_type == "favorite"]
        avoid_colors = [cp.color_name for cp in color_prefs if cp.preference_type == "avoid"]
        styles = [sp.style_name for sp in style_prefs]
        learned_deltas = {f"{w.feature_type}:{w.feature_value.lower()}": w.weight_delta for w in pref_weights}

        # Resolve conflict: If a color is in both, avoid strictly takes priority!
        avoid_norm = {normalize_color(c) for c in avoid_colors}
        clean_fav_colors = [c for c in fav_colors if normalize_color(c) not in avoid_norm]

        return {
            "name": profile.name if profile and profile.name else "Alex Taylor",
            "gender": profile.gender if profile and profile.gender else "Female",
            "include_unisex": profile.include_unisex if profile and profile.include_unisex is not None else False,
            "strict_preferences": profile.strict_preferences if profile and profile.strict_preferences is not None else True,
            "age_group": profile.age_group if profile and profile.age_group else "20-29",
            "height": profile.height if profile and profile.height else "168 cm",
            "weight": profile.weight if profile and profile.weight else "58 kg",
            "clothing_size": profile.clothing_size if profile and profile.clothing_size else "M",
            "body_type": profile.body_type if profile and profile.body_type else "Hourglass",
            "skin_tone": profile.skin_tone if profile and profile.skin_tone else "Neutral / Medium",
            "budget_min": profile.budget_min if profile and profile.budget_min else 1500.0,
            "budget_max": profile.budget_max if profile and profile.budget_max else 6500.0,
            "preferred_fit": profile.preferred_fit if profile and profile.preferred_fit else "Relaxed",
            "preferred_sleeve_length": profile.preferred_sleeve_length if profile and profile.preferred_sleeve_length else "Full Sleeve",
            "preferred_clothing_length": profile.preferred_clothing_length if profile and profile.preferred_clothing_length else "Standard",
            "preferred_materials": [m.strip() for m in (profile.preferred_materials.split(",") if profile and profile.preferred_materials else ["Cotton", "Linen"])],
            "preferred_brands": profile.preferred_brands if profile and profile.preferred_brands else "All Brands",
            "disliked_clothing": profile.disliked_clothing.lower() if profile and profile.disliked_clothing else "",
            "custom_style_description": profile.custom_style_description if profile and profile.custom_style_description else "",
            "favorite_colors": clean_fav_colors,
            "avoid_colors": avoid_colors,
            "preferred_styles": styles or ["Casual", "Minimal", "Elegant"],
            "learned_deltas": learned_deltas
        }

    # =========================================================================
    # STAGE 1: HARD FILTERING
    # =========================================================================
    def passes_hard_filters(
        self,
        product: Product,
        gender: str,
        include_unisex: bool,
        occasion: str,
        avoid_colors: List[str],
        favorite_colors: List[str],
        preferred_styles: List[str],
        preferred_fit: Optional[str],
        preferred_sleeve: Optional[str],
        preferred_length: Optional[str],
        preferred_fabrics: List[str],
        strict_preferences: bool,
        is_main_garment: bool = True
    ) -> Tuple[bool, str]:
        """
        Applies non-negotiable mandatory filters.
        Returns (True, "") or (False, rejection_reason).
        """
        # 1. Product Availability
        if not product.availability:
            return False, "Not available"

        # 2. Gender Filtering (Strict)
        # Female selection must retrieve Female products only (or unisex if enabled).
        # Male selection must retrieve Male products only (or unisex if enabled).
        # NEVER mix male and female products!
        p_gender = product.gender or "Female"
        if gender.lower() == "female":
            if p_gender == "Male":
                return False, "Male product in Female session"
            if p_gender == "Unisex" and not include_unisex:
                return False, "Unisex excluded in Female session"
        elif gender.lower() == "male":
            if p_gender == "Female":
                return False, "Female product in Male session"
            if p_gender == "Unisex" and not include_unisex:
                return False, "Unisex excluded in Male session"

        # 3. Occasion Filtering (Strict)
        occ_target = occasion.strip().lower()
        p_occ_primary = (product.occasion or "").strip().lower()
        p_supp_occs = [o.strip().lower() for o in (product.supported_occasions or "").split(",") if o.strip()]
        all_p_occs = [p_occ_primary] + p_supp_occs

        if occ_target == "formal event":
            target_formal = {"formal event", "business meeting", "interview", "office", "dinner"}
            matches_occ = (p_occ_primary in target_formal) or any(o in target_formal for o in p_supp_occs)
        else:
            matches_occ = (occ_target in p_occ_primary) or (p_occ_primary in occ_target) or (occ_target in p_supp_occs)

        if not matches_occ:
            if occ_target == "formal event":
                target_formal = {"formal event", "business meeting", "interview", "office", "dinner"}
                if any(o.strip() in target_formal for o in all_p_occs):
                    matches_occ = True
            elif any(c in occ_target for c in ["casual", "college", "university", "shopping", "travel", "vacation"]):
                if any(any(k in o for k in ["casual", "college", "university", "shopping", "travel", "vacation", "brunch", "date", "concert"]) for o in all_p_occs):
                    matches_occ = True
            elif any(f in occ_target for f in ["formal", "business", "interview", "office"]):
                if any(any(k in o for k in ["formal", "business", "interview", "office", "semi-formal", "dinner"]) for o in all_p_occs):
                    matches_occ = True
            elif any(w in occ_target for w in ["engagement", "wedding"]):
                if any(any(k in o for k in ["engagement", "wedding", "festival", "family gathering"]) for o in all_p_occs):
                    matches_occ = True
            elif any(w in occ_target for w in ["festival", "religious"]):
                if any(any(k in o for k in ["festival", "religious", "wedding", "engagement", "family gathering"]) for o in all_p_occs):
                    matches_occ = True
            elif any(p in occ_target for p in ["party", "birthday", "dinner"]):
                if any(any(k in o for k in ["party", "birthday", "dinner", "concert", "date", "casual"]) for o in all_p_occs):
                    matches_occ = True
            elif any(s in occ_target for s in ["gym", "sports"]):
                if any(any(k in o for k in ["gym", "sports", "athletic", "fitness"]) for o in all_p_occs):
                    matches_occ = True

        if not matches_occ:
            return False, f"Does not match occasion '{occasion}'"

        # 3b. Occasion Appropriateness Matrix
        canon_occ = get_canonical_occasion(occasion)
        g_key = gender.lower() if gender.lower() in ["female", "male"] else "female"

        if canon_occ in OCCASION_MATRIX and g_key in OCCASION_MATRIX[canon_occ]:
            rules = OCCASION_MATRIX[canon_occ][g_key]
            subcat = product.subcategory

            # Strict Blocklist
            if subcat in rules.get("blocked", []):
                return False, f"Subcategory '{subcat}' is strictly inappropriate for {occasion}"

            if is_main_garment:
                is_complete = (product.clothing_type == "Complete Outfit" or product.outfit_compatibility == "complete_outfit")
                is_top = (product.clothing_type == "Topwear" or product.outfit_compatibility == "top")
                is_bottom = (product.clothing_type == "Bottomwear" or product.outfit_compatibility == "bottom")

                if is_complete:
                    if subcat not in rules.get("allowed_complete", []):
                        return False, f"Complete outfit '{subcat}' not appropriate for {occasion}"
                elif is_top:
                    if subcat not in rules.get("allowed_tops", []):
                        return False, f"Top '{subcat}' not appropriate for {occasion}"
                elif is_bottom:
                    if subcat not in rules.get("allowed_bottoms", []):
                        return False, f"Bottom '{subcat}' not appropriate for {occasion}"
            else:
                is_footwear = (product.category == "Footwear" or product.outfit_compatibility == "footwear")
                is_accessory = (product.category == "Accessories" or product.outfit_compatibility == "accessory")

                if is_footwear:
                    if subcat not in rules.get("allowed_footwear", []):
                        return False, f"Footwear '{subcat}' not appropriate for {occasion}"
                elif is_accessory:
                    if subcat not in rules.get("allowed_accessories", []):
                        return False, f"Accessory '{subcat}' not appropriate for {occasion}"

        # 4. Avoided Colours Filtering (Strict)
        # Check both exact color name and color family
        p_color_norm = normalize_color(product.color)
        p_color_fam = get_color_family(product.color)
        for avoid in avoid_colors:
            a_norm = normalize_color(avoid)
            a_fam = get_color_family(avoid)
            if p_color_norm == a_norm or (a_fam and p_color_fam == a_fam):
                return False, f"Matches avoided colour '{avoid}'"

        # 5. Favourite Colours Filtering (Strict for Main Garments)
        # If user explicitly specified favorite colors, main clothing garments MUST be in those colors/families.
        # Footwear and accessories may be neutral or harmonizing shades.
        if favorite_colors and is_main_garment:
            fav_families = {get_color_family(c) for c in favorite_colors}
            fav_norms = {normalize_color(c) for c in favorite_colors}
            matches_fav = (p_color_norm in fav_norms) or (p_color_fam in fav_families)
            if not matches_fav:
                return False, f"Not in favourite colours: {favorite_colors}"

        # 6. Aesthetic / Style Archetype Filtering (Strict for Main Garments)
        # If user selected specific aesthetics, main garments must belong to one of those aesthetics.
        p_style = product.style_archetype or product.style or ""
        if preferred_styles and is_main_garment:
            selected_styles_norm = [s.strip().lower() for s in preferred_styles]
            if p_style.strip().lower() not in selected_styles_norm:
                # Disallow unrelated aesthetics (e.g. Streetwear when user selected Minimal)
                return False, f"Style '{p_style}' does not match selected aesthetics {preferred_styles}"

        # 7. Strict Nuances (Fit, Sleeve, Length, Fabric) when strict_preferences is True
        if strict_preferences and is_main_garment:
            # Preferred Fit
            if preferred_fit:
                p_fit = (product.fit or "").strip().lower()
                pref_fit_norm = preferred_fit.strip().lower()
                # If user selected Oversized, exclude Slim/Tight/Bodycon
                if "oversized" in pref_fit_norm and ("slim" in p_fit or "bodycon" in p_fit):
                    return False, f"Fit '{product.fit}' conflicts with strict oversized preference"
                elif "slim" in pref_fit_norm and ("oversized" in p_fit or "loose" in p_fit):
                    return False, f"Fit '{product.fit}' conflicts with strict slim fit preference"

            # Sleeve Length (only applies to garments with sleeves: shirts, tops, kurtas, jackets)
            if preferred_sleeve and product.category == "Clothing" and product.sleeve_length != "N/A":
                p_sleeve = (product.sleeve_length or "").strip().lower()
                pref_sleeve_norm = preferred_sleeve.strip().lower()
                if "full" in pref_sleeve_norm and ("sleeveless" in p_sleeve or "half" in p_sleeve or "short" in p_sleeve):
                    return False, f"Sleeve '{product.sleeve_length}' conflicts with strict full sleeve preference"
                elif "sleeveless" in pref_sleeve_norm and "full" in p_sleeve:
                    return False, f"Sleeve '{product.sleeve_length}' conflicts with strict sleeveless preference"

            # Garment Length (applies to dresses, skirts, gowns)
            if preferred_length and product.category == "Clothing" and product.garment_length != "N/A":
                p_len = (product.garment_length or "").strip().lower()
                pref_len_norm = preferred_length.strip().lower()
                if "maxi" in pref_len_norm or "floor" in pref_len_norm:
                    if "short" in p_len or "cropped" in p_len:
                        return False, f"Length '{product.garment_length}' conflicts with strict maxi length"

            # Fabric (if strict, main garments must match preferred fabrics if specified)
            if preferred_fabrics and len(preferred_fabrics) > 0:
                p_fabric = (product.fabric or product.material or "").strip().lower()
                pref_fabrics_norm = [f.strip().lower() for f in preferred_fabrics]
                if not any(pf in p_fabric for pf in pref_fabrics_norm):
                    return False, f"Fabric '{product.fabric}' not in preferred materials {preferred_fabrics}"

        return True, ""

    # =========================================================================
    # STAGE 2: PERSONALIZATION SCORING & RANKING
    # =========================================================================
    def calculate_personalization_score(
        self,
        product: Product,
        user_ctx: Dict[str, Any],
        target_occasion: str,
        target_style: str,
        weather_hint: str
    ) -> float:
        """
        Calculates transparent weighted affinity score (0 to 100):
        - Occasion-Subcategory Alignment: 25% (highest weight - drives correct occasion matching)
        - Body Shape Compatibility: 15%
        - Colour Suitability & Skin Tone: 20%
        - Personal Aesthetic & Style Description: 15%
        - Fabric and Fit Affinity: 10%
        - Brand Preference: 5%
        - Weather Suitability: 5%
        - Previous Feedback & Learned Weights: 5%
        """
        # Baseline (lower to allow alignment to differentiate)
        score = 40.0

        # 0. OCCASION-SUBCATEGORY ALIGNMENT (Weight: 25) — evaluated first as the primary discriminator
        occ_clean = (target_occasion or "").lower()
        sub_clean = (product.subcategory or "")

        if any(f in occ_clean for f in ["office", "business", "interview", "formal"]):
            # Formal separates get full bonus; ethnic/casual get penalty
            if sub_clean in ["Blazers", "Formal shirts", "Shirts", "Formal trousers", "Trousers", "Suits", "Skirts", "Dresses", "Heels", "Formal shoes", "Handbags", "Watches"]:
                score += 25.0
            elif sub_clean in ["Salwar suits", "Indo-western outfits"]:
                score += 10.0  # acceptable ethnic-formal
            elif sub_clean in ["Kurtis"]:
                score += 5.0   # minimal - last resort
            else:
                score += 2.0
        elif any(w in occ_clean for w in ["wedding", "engagement", "festival", "religious"]):
            if sub_clean in ["Lehengas", "Designer sarees", "Sarees", "Anarkali suits", "Sharara sets", "Sherwanis", "Kurta pyjama sets", "Indo-western outfits", "Ethnic gowns", "Ethnic footwear", "Clutches", "Necklaces", "Earrings", "Dupattas"]:
                score += 25.0
            else:
                score += 5.0
        elif any(c in occ_clean for c in ["college", "university"]):
            if sub_clean in ["Jeans", "Tops", "T-shirts", "Casual shirts", "Kurtis", "Hoodies", "Chinos", "Casual wear", "Sneakers", "Flats", "Backpacks", "Watches"]:
                score += 25.0
            elif sub_clean in ["Co-ord sets", "Dresses", "Jumpsuits", "Palazzo sets"]:
                score += 15.0
            else:
                score += 5.0
        elif any(c in occ_clean for c in ["casual", "shopping", "travel", "brunch", "vacation"]):
            if sub_clean in ["Jeans", "Tops", "Casual shirts", "T-shirts", "Dresses", "Jumpsuits", "Chinos", "Casual wear", "Sneakers", "Flats", "Sandals", "Loafers", "Sunglasses", "Handbags", "Co-ord sets"]:
                score += 25.0
            else:
                score += 5.0
        elif any(s in occ_clean for s in ["gym", "sports"]):
            if sub_clean in ["T-shirts", "Basic T-shirts", "Tops", "Casual wear", "Hoodies", "Sweatshirts", "Trousers", "Chinos", "Jeans", "Sneakers", "Caps", "Backpacks", "Watches", "Sandals"]:
                score += 25.0
            else:
                score += 2.0
        elif any(p in occ_clean for p in ["party", "dinner", "date", "birthday", "concert"]):
            if sub_clean in ["Dresses", "Jumpsuits", "Co-ord sets", "Tops", "Skirts", "Heels", "Boots", "Clutches", "Earrings", "Necklaces"]:
                score += 25.0
            else:
                score += 8.0
        else:
            score += 12.0  # default partial credit

        # 1. Body Shape Compatibility (Weight: 15)
        b_type = (user_ctx.get("body_type") or "Hourglass").strip().lower()
        p_b_compat = (product.body_shape_compatibility or "All").strip().lower()
        if p_b_compat == "all" or b_type in p_b_compat or p_b_compat in b_type:
            score += 15.0
        else:
            score += 5.0

        # 2. Colour Suitability & Skin Tone (Weight: 20)
        p_color = normalize_color(product.color)
        p_fam = get_color_family(product.color)
        fav_norms = {normalize_color(c) for c in user_ctx.get("favorite_colors", [])}
        fav_fams = {get_color_family(c) for c in user_ctx.get("favorite_colors", [])}

        if p_color in fav_norms:
            score += 20.0
        elif p_fam in fav_fams:
            score += 15.0
        elif p_color in NEUTRAL_COLORS:
            score += 10.0
        else:
            score += 5.0

        # Skin tone affinity
        skin = (user_ctx.get("skin_tone") or "Neutral").lower()
        p_skin = (product.skin_tone_compatibility or "All").lower()
        if p_skin == "all" or any(s in p_skin for s in skin.split()):
            score += 5.0

        # 3. Personal Aesthetic & Style Description (Weight: 20)
        p_style = (product.style_archetype or product.style or "").strip().lower()
        if p_style == target_style.strip().lower():
            score += 20.0
        elif any(p_style == s.strip().lower() for s in user_ctx.get("preferred_styles", [])):
            score += 14.0
        else:
            score += 6.0

        # Natural language style description keywords bonus
        desc = (user_ctx.get("custom_style_description") or "").lower()
        if desc:
            p_text = f"{product.name} {product.description} {product.fabric} {product.fit}".lower()
            matching_keywords = sum(1 for word in re.findall(r'\w+', desc) if len(word) > 3 and word in p_text)
            score += min(6.0, matching_keywords * 1.5)

        # 4. Fabric and Fit Affinity (Weight: 15)
        p_fit = (product.fit or "").lower()
        user_fit = (user_ctx.get("preferred_fit") or "").lower()
        if p_fit and user_fit and (p_fit == user_fit or user_fit in p_fit or p_fit in user_fit):
            score += 8.0

        p_fab = (product.fabric or "").lower()
        user_fabs = [m.lower() for m in user_ctx.get("preferred_materials", [])]
        if any(uf in p_fab for uf in user_fabs):
            score += 7.0

        # 5. Brand Preference (Weight: 5)
        user_brands = (user_ctx.get("preferred_brands") or "").lower()
        p_brand = (product.brand or "").lower()
        if "all" in user_brands or (p_brand and p_brand in user_brands):
            score += 5.0

        # 6. Weather Suitability (Weight: 10)
        w_hint = weather_hint.lower()
        p_weather = (product.weather_suitability or "All-Weather").lower()
        if "hot" in w_hint or "summer" in w_hint:
            if p_fab in ["linen", "cotton", "rayon"] or "hot" in p_weather:
                score += 10.0
            elif p_fab in ["wool", "velvet", "leather"]:
                score -= 10.0
        elif "cold" in w_hint or "winter" in w_hint:
            if p_fab in ["wool", "velvet", "leather", "knit"] or "cold" in p_weather:
                score += 10.0
            elif p_fab in ["linen", "chiffon"]:
                score -= 8.0
        elif "rain" in w_hint:
            if product.subcategory in ["Boots", "Jackets", "Sandals"]:
                score += 8.0
        else:
            score += 6.0

        # 7. Previous Feedback & Learned Weights (Weight: 5)
        deltas = user_ctx.get("learned_deltas", {})
        color_key = f"color:{p_color}"
        style_key = f"style:{p_style}"
        if color_key in deltas:
            score += deltas[color_key]
        if style_key in deltas:
            score += deltas[style_key]

        return max(40.0, min(99.0, score))

    # =========================================================================
    # COMPLETE OUTFIT GENERATION
    # =========================================================================
    def generate_three_looks(
        self,
        user_id: int,
        occasion: str = "College",
        gender: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        weather: str = "Mild (24°C)",
        preferred_colors: Optional[List[str]] = None,
        avoid_colors: Optional[List[str]] = None,
        preferred_style: Optional[str] = None,
        preferred_fit: Optional[str] = None,
        preferred_fabric: Optional[str] = None,
        include_unisex: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates coordinated outfits adhering to strict two-stage process.
        """
        user_ctx = self.get_user_profile_context(user_id)

        # Apply overrides
        act_gender = gender or user_ctx["gender"]
        b_min = budget_min if budget_min is not None else user_ctx["budget_min"]
        b_max = budget_max if budget_max is not None else user_ctx["budget_max"]
        act_unisex = include_unisex if include_unisex is not None else user_ctx["include_unisex"]
        strict_mode = user_ctx["strict_preferences"]

        # Override handling: None means inherit from user profile context; non-None (even []) is explicit override
        fav_colors = preferred_colors if preferred_colors is not None else user_ctx["favorite_colors"]
        av_colors = avoid_colors if avoid_colors is not None else user_ctx["avoid_colors"]
        # Only hard-filter by style if user explicitly selected a style; otherwise let Stage 2 rank by user preferred styles
        styles = [preferred_style] if (preferred_style is not None and preferred_style != "") else []
        fit_pref = preferred_fit if preferred_fit is not None else (user_ctx["preferred_fit"] if strict_mode else None)
        fab_pref = [preferred_fabric] if preferred_fabric is not None else (user_ctx["preferred_materials"] if strict_mode else [])
        fab_pref = [f for f in fab_pref if f]

        # 1. Fetch available products from database
        all_products = self.db.query(Product).filter(Product.availability == True).all()

        # 2. Hard Filter products for Main Garments and Supporting Pieces
        valid_complete_sets = []
        valid_tops = []
        valid_bottoms = []
        valid_footwear = []
        valid_accessories = []

        for p in all_products:
            # Check main garment filters
            passes_main, _ = self.passes_hard_filters(
                product=p,
                gender=act_gender,
                include_unisex=act_unisex,
                occasion=occasion,
                avoid_colors=av_colors,
                favorite_colors=fav_colors,
                preferred_styles=styles,
                preferred_fit=fit_pref,
                preferred_sleeve=user_ctx["preferred_sleeve_length"],
                preferred_length=user_ctx["preferred_clothing_length"],
                preferred_fabrics=fab_pref,
                strict_preferences=strict_mode,
                is_main_garment=True
            )

            # Check supporting piece filters (footwear & accessories - colors can be neutral/complementary)
            passes_support, _ = self.passes_hard_filters(
                product=p,
                gender=act_gender,
                include_unisex=act_unisex,
                occasion=occasion,
                avoid_colors=av_colors,
                favorite_colors=[],  # allow neutral/complementary for accessories/footwear
                preferred_styles=[],
                preferred_fit=None,
                preferred_sleeve=None,
                preferred_length=None,
                preferred_fabrics=[],
                strict_preferences=False,
                is_main_garment=False
            )

            if passes_main:
                if p.clothing_type == "Complete Outfit" or p.outfit_compatibility == "complete_outfit":
                    valid_complete_sets.append(p)
                elif p.clothing_type == "Topwear" or p.outfit_compatibility == "top":
                    valid_tops.append(p)
                elif p.clothing_type == "Bottomwear" or p.outfit_compatibility == "bottom":
                    valid_bottoms.append(p)

            if passes_support:
                if p.category == "Footwear" or p.outfit_compatibility == "footwear":
                    valid_footwear.append(p)
                elif p.category == "Accessories" or p.outfit_compatibility == "accessory":
                    valid_accessories.append(p)

        # Supporting pieces fallback (ensure footwear and accessories exist while respecting gender and avoid colors)
        if (len(valid_complete_sets) > 0 or (len(valid_tops) > 0 and len(valid_bottoms) > 0)) and len(valid_footwear) == 0:
            for p in all_products:
                if (p.category == "Footwear" or p.outfit_compatibility == "footwear") and (p.gender in [act_gender, "Unisex"] if act_unisex else [act_gender]):
                    p_col = normalize_color(p.color)
                    p_fam = get_color_family(p.color)
                    if not any(normalize_color(a) in [p_col, p_fam] for a in av_colors):
                        valid_footwear.append(p)

        if (len(valid_complete_sets) > 0 or (len(valid_tops) > 0 and len(valid_bottoms) > 0)) and len(valid_accessories) == 0:
            for p in all_products:
                if (p.category == "Accessories" or p.outfit_compatibility == "accessory") and (p.gender in [act_gender, "Unisex"] if act_unisex else [act_gender]):
                    p_col = normalize_color(p.color)
                    p_fam = get_color_family(p.color)
                    if not any(normalize_color(a) in [p_col, p_fam] for a in av_colors):
                        valid_accessories.append(p)

        # If insufficient products to build an outfit
        has_complete = len(valid_complete_sets) > 0 and len(valid_footwear) > 0
        has_separates = len(valid_tops) > 0 and len(valid_bottoms) > 0 and len(valid_footwear) > 0

        if not has_complete and not has_separates:
            return []

        # Determine target styles for 3 looks:
        occ_target = (occasion or "Casual outing").strip().lower()
        if any(w in occ_target for w in ["wedding", "engagement", "festival", "religious"]):
            occ_defaults = ["Traditional", "Elegant", "Ethnic", "Luxury"]
        elif any(f in occ_target for f in ["office", "business", "interview", "formal"]):
            occ_defaults = ["Formal", "Smart Casual", "Minimal", "Classic", "Elegant"]
        elif any(s in occ_target for s in ["gym", "sports"]):
            occ_defaults = ["Sporty", "Athleisure", "Casual"]
        else:
            occ_defaults = ["Casual", "Smart Casual", "Streetwear", "Minimal", "Trendy", "Bohemian"]

        user_matched_styles = [s for s in user_ctx.get("preferred_styles", []) if s in occ_defaults]
        style_candidates = [preferred_style] if preferred_style else (user_matched_styles if user_matched_styles else occ_defaults)
        for d in occ_defaults:
            if d not in style_candidates:
                style_candidates.append(d)
            if len(style_candidates) >= 3:
                break

        # Determine whether occasion naturally favors complete sets (Traditional) or separates (Casual/Office/Gym)
        is_traditional_occ = any(w in occ_target for w in ["wedding", "engagement", "festival", "religious event", "family gathering"])
        is_formal_occ = any(f in occ_target for f in ["office", "business meeting", "interview", "formal event"])

        # Track used products across the 3 looks to guarantee diversity
        used_main_ids = set()
        used_shoe_ids = set()
        used_acc_ids = set()

        looks = []
        look_titles = [
            ("Look 1: Signature Ensemble", "Budget-Friendly"),
            ("Look 2: Contemporary Elegance", "Balanced"),
            ("Look 3: Premium Curated Look", "Premium")
        ]

        # Budget multipliers for tiers
        tier_multipliers = [0.65, 0.85, 1.0]

        for idx in range(3):
            target_style = style_candidates[idx % len(style_candidates)]
            title, tier = look_titles[idx]
            tier_max_budget = b_max * tier_multipliers[idx]

            # Decide whether to assemble a Complete Outfit (Traditional / Dress / Suit) or Top + Bottom
            use_complete = False
            canon_occ = get_canonical_occasion(occasion)
            if canon_occ in ["festival", "wedding"]:
                use_complete = len(valid_complete_sets) > 0
            elif canon_occ == "formal event":
                # Look 1 & 2: Sharp formal separates (Shirts/Blazers + Trousers); Look 3: tailored formal dress or full suit
                if idx == 2 and valid_complete_sets:
                    use_complete = True
                else:
                    use_complete = not (valid_tops and valid_bottoms)
            elif canon_occ in ["office", "college", "gym"]:
                # Office and College are predominantly separates (tops + bottoms)
                # Look 3 can only use complete if it's a dedicated formal dress / co-ord for office or casual dress for college
                if canon_occ == "office" and idx == 2 and valid_complete_sets and any(c.subcategory in ["Dresses", "Co-ord sets"] for c in valid_complete_sets):
                    use_complete = True
                elif canon_occ == "college" and idx == 2 and valid_complete_sets and any(c.subcategory in ["Dresses", "Co-ord sets", "Jumpsuits"] for c in valid_complete_sets):
                    use_complete = True
                else:
                    use_complete = False
            else:
                if idx == 2 and valid_complete_sets:
                    use_complete = True
                else:
                    use_complete = not (valid_tops and valid_bottoms)

            outfit_items = []
            total_price = 0.0

            if use_complete and valid_complete_sets:
                # Rank complete sets by score, then filter by budget
                scored_sets = sorted(
                    valid_complete_sets,
                    key=lambda p: self.calculate_personalization_score(p, user_ctx, occasion, target_style, weather),
                    reverse=True
                )
                unused_sets = [cs for cs in scored_sets if cs.id not in used_main_ids]
                candidate_pool = unused_sets if unused_sets else scored_sets

                min_shoe_cost = min((s.price for s in valid_footwear), default=0.0) if valid_footwear else 0.0
                max_set_cap = max(0.0, b_max - min_shoe_cost) if min_shoe_cost > 0 else b_max

                chosen_set = None
                for cs in candidate_pool:
                    if cs.price <= min(tier_max_budget * 0.85, max_set_cap):
                        chosen_set = cs
                        break
                if chosen_set is None:
                    for cs in candidate_pool:
                        if cs.price <= max_set_cap:
                            chosen_set = cs
                            break
                if chosen_set is None:
                    for cs in candidate_pool:
                        if cs.price <= b_max:
                            chosen_set = cs
                            break
                if chosen_set is None:
                    chosen_set = min(candidate_pool, key=lambda p: p.price)

                used_main_ids.add(chosen_set.id)
                outfit_items.append({"role": "complete_outfit", "product": chosen_set})
                total_price += chosen_set.price
            elif valid_tops and valid_bottoms:
                # Rank tops and bottoms
                scored_tops = sorted(
                    valid_tops,
                    key=lambda p: self.calculate_personalization_score(p, user_ctx, occasion, target_style, weather),
                    reverse=True
                )
                scored_bottoms = sorted(
                    valid_bottoms,
                    key=lambda p: self.calculate_personalization_score(p, user_ctx, occasion, target_style, weather),
                    reverse=True
                )

                unused_tops = [t for t in scored_tops if t.id not in used_main_ids]
                tops_pool = unused_tops if unused_tops else scored_tops

                unused_bottoms = [b for b in scored_bottoms if b.id not in used_main_ids]
                bottoms_pool = unused_bottoms if unused_bottoms else scored_bottoms

                min_shoe_cost = min((s.price for s in valid_footwear), default=0.0) if valid_footwear else 0.0
                budget_for_clothes = min(tier_max_budget * 0.75, max(0.0, b_max - min_shoe_cost)) if min_shoe_cost > 0 else tier_max_budget * 0.75
                chosen_top = None
                for t in tops_pool:
                    if t.price <= budget_for_clothes * 0.6:
                        chosen_top = t
                        break
                if chosen_top is None:
                    affordable_tops = [t for t in tops_pool if t.price <= budget_for_clothes]
                    chosen_top = min(affordable_tops, key=lambda p: p.price) if affordable_tops else min(tops_pool, key=lambda p: p.price)

                remaining_clothes = max(0.0, budget_for_clothes - chosen_top.price)
                chosen_bottom = None
                for b in bottoms_pool:
                    if b.price <= remaining_clothes:
                        chosen_bottom = b
                        break
                if chosen_bottom is None:
                    max_b = max(0.0, b_max - chosen_top.price - min_shoe_cost)
                    affordable_bottoms = [b for b in bottoms_pool if b.price <= max_b]
                    chosen_bottom = min(affordable_bottoms, key=lambda p: p.price) if affordable_bottoms else min(bottoms_pool, key=lambda p: p.price)

                used_main_ids.add(chosen_top.id)
                used_main_ids.add(chosen_bottom.id)
                outfit_items.append({"role": "top", "product": chosen_top})
                outfit_items.append({"role": "bottom", "product": chosen_bottom})
                total_price += chosen_top.price + chosen_bottom.price
            elif valid_complete_sets:
                unused_sets = [cs for cs in valid_complete_sets if cs.id not in used_main_ids]
                candidate_pool = unused_sets if unused_sets else valid_complete_sets
                within_budget = [cs for cs in candidate_pool if cs.price <= b_max]
                pool_to_use = within_budget if within_budget else candidate_pool
                chosen_set = pool_to_use[idx % len(pool_to_use)]
                used_main_ids.add(chosen_set.id)
                outfit_items.append({"role": "complete_outfit", "product": chosen_set})
                total_price += chosen_set.price
            else:
                continue

            # Add Footwear (prioritize unused footwear)
            if valid_footwear and total_price < b_max:
                scored_shoes = sorted(
                    valid_footwear,
                    key=lambda p: self.calculate_personalization_score(p, user_ctx, occasion, target_style, weather),
                    reverse=True
                )
                unused_shoes = [s for s in scored_shoes if s.id not in used_shoe_ids]
                shoes_pool = unused_shoes if unused_shoes else scored_shoes

                remaining = b_max - total_price
                chosen_shoe = None
                for s in shoes_pool:
                    if s.price <= remaining:
                        chosen_shoe = s
                        break
                if chosen_shoe is None and shoes_pool:
                    cheapest = sorted(shoes_pool, key=lambda p: p.price)
                    if cheapest and (total_price + cheapest[0].price <= b_max):
                        chosen_shoe = cheapest[0]
                if chosen_shoe:
                    used_shoe_ids.add(chosen_shoe.id)
                    outfit_items.append({"role": "footwear", "product": chosen_shoe})
                    total_price += chosen_shoe.price

            # Add Accessory (prioritize unused accessory)
            if valid_accessories and total_price < b_max:
                scored_accs = sorted(
                    valid_accessories,
                    key=lambda p: self.calculate_personalization_score(p, user_ctx, occasion, target_style, weather),
                    reverse=True
                )
                unused_accs = [a for a in scored_accs if a.id not in used_acc_ids]
                accs_pool = unused_accs if unused_accs else scored_accs

                remaining = b_max - total_price
                chosen_acc = None
                for a in accs_pool:
                    if a.price <= remaining:
                        chosen_acc = a
                        break
                if chosen_acc is None and accs_pool:
                    cheapest = sorted(accs_pool, key=lambda p: p.price)
                    if cheapest and (total_price + cheapest[0].price <= b_max):
                        chosen_acc = cheapest[0]
                if chosen_acc:
                    used_acc_ids.add(chosen_acc.id)
                    outfit_items.append({"role": "accessory", "product": chosen_acc})
                    total_price += chosen_acc.price

            # Compute combined match percentage
            avg_score = sum(self.calculate_personalization_score(it["product"], user_ctx, occasion, target_style, weather) for it in outfit_items) / max(1, len(outfit_items))
            match_score = round(min(98.5, max(85.0, avg_score)), 1)

            # Generate dynamic explanation
            main_p = outfit_items[0]["product"]
            explanation = (
                f"Curated for {act_gender} {occasion} in an authentic {target_style} aesthetic. "
                f"Featuring {main_p.brand}'s {main_p.color} {main_p.fabric} {main_p.subcategory} "
                f"tailored in a {main_p.fit} that harmonizes with your {user_ctx['body_type']} silhouette, "
                f"complemented by coordinated pieces respecting your ₹{b_max:,.0f} budget."
            )

            # Complete outfit image: use primary garment image
            hero_image = main_p.image_url

            looks.append({
                "id": None,
                "title": f"{title} ({target_style})",
                "style_tag": target_style,
                "occasion": occasion,
                "total_price": round(total_price, 2),
                "match_score": match_score,
                "explanation": explanation,
                "image_url": hero_image,
                "weather_context": weather,
                "budget_tier": tier,
                "items": outfit_items
            })

        return looks

    def get_mix_match_alternatives(
        self,
        user_id: int,
        accepted_product_ids: List[int],
        role_to_replace: str,
        occasion: str = "College",
        budget_max: float = 6500.0,
        weather: str = "Mild (24°C)"
    ) -> List[Dict[str, Any]]:
        """Find compatible replacement items for an outfit item."""
        user_ctx = self.get_user_profile_context(user_id)
        q = self.db.query(Product).filter(
            Product.availability == True,
            Product.gender.in_([user_ctx["gender"], "Unisex"] if user_ctx["include_unisex"] else [user_ctx["gender"]])
        )
        if role_to_replace in ["top", "bottom", "footwear", "accessory", "complete_outfit"]:
            q = q.filter(Product.outfit_compatibility == role_to_replace)

        candidates = q.limit(20).all()
        alternatives = []
        for c in candidates:
            if c.id not in accepted_product_ids:
                score = self.calculate_personalization_score(
                    product=c,
                    user_ctx=user_ctx,
                    target_occasion=occasion,
                    target_style=user_ctx["preferred_styles"][0] if user_ctx["preferred_styles"] else "Casual",
                    weather_hint=weather
                )
                alternatives.append({
                    "replacement_product": c,
                    "compatibility_score": round(score, 1),
                    "new_total_price": c.price,
                    "explanation": f"Harmonious {c.color} {c.fabric} {c.subcategory} ({c.brand})"
                })
        alternatives.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return alternatives[:4]
