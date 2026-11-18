import base64
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.entities import User, Outfit, OutfitItem, RecommendationHistory, UserProfile
from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    VisualizeRequest,
    VisualizeResponse,
    OutfitResponse,
    TryOnJsonRequest,
    TryOnResponse,
    AnalyzePhotoRequest,
    PhotoAnalysisResponse,
    AnalysisRecommendationRequest,
    AnalysisRecommendationResponse,
    ProductResponse
)
from .users import get_current_user
from ..services.gemini_service import GeminiStylistService
from ..services.recommendation_service import RecommendationEngine
from ..services.image_service import OutfitVisualizationService
from ..services.photo_analysis_service import PhotoAnalysisService

router = APIRouter(prefix="/api/ai", tags=["AI Stylist"])

gemini_service = GeminiStylistService()


@router.post("/chat", response_model=ChatResponse)
def chat_with_stylist(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Conversational AI Stylist endpoint.
    Understands user profile, active gender, occasions, budgets, colors, fits, and aesthetics,
    and retrieves real product recommendations from the centralized recommendation engine.
    """
    rec_engine = RecommendationEngine(db)
    user_ctx = rec_engine.get_user_profile_context(user.id)

    msg_lower = payload.message.lower()
    recommended_outfit_data = None
    outfit_response = None

    # Detect gender from request or message
    active_gender = payload.gender_override or user_ctx["gender"]
    gender_conflict_detected = False

    if any(w in msg_lower for w in ["men's", "male", "for men", "for him", "his", "brother", "husband", "boyfriend"]):
        if user_ctx["gender"].lower() == "female":
            active_gender = "Male"
            gender_conflict_detected = True
    elif any(w in msg_lower for w in ["women's", "female", "for women", "for her", "hers", "sister", "wife", "girlfriend"]):
        if user_ctx["gender"].lower() == "male":
            active_gender = "Female"
            gender_conflict_detected = True

    # Keywords triggering outfit recommendation
    trigger_words = [
        "outfit", "wear", "look", "dress", "style", "recommend", "need something",
        "going to", "tomorrow", "tonight", "suggest", "show me", "what should i"
    ]
    should_recommend = any(w in msg_lower for w in trigger_words)

    # Detect occasion from message or fallback to override
    occasion = payload.occasion_override or "Casual outing"
    occasions_map = [
        ("engagement", "Engagement"),
        ("wedding", "Wedding"),
        ("business meeting", "Business Meeting"),
        ("interview", "Interview"),
        ("office", "Office"),
        ("college", "College"),
        ("university", "University"),
        ("date", "Date"),
        ("dinner", "Dinner"),
        ("party", "Party"),
        ("birthday", "Birthday"),
        ("festival", "Festival"),
        ("religious", "Religious Event"),
        ("family gathering", "Family Gathering"),
        ("brunch", "Brunch"),
        ("beach", "Beach"),
        ("gym", "Gym"),
        ("sports", "Sports"),
        ("concert", "Concert"),
        ("formal event", "Formal Event"),
        ("semi-formal", "Semi-Formal Event"),
        ("photoshoot", "Photoshoot"),
        ("shopping", "Shopping"),
        ("vacation", "Vacation"),
        ("travel", "Travel")
    ]
    for key, occ_name in occasions_map:
        if key in msg_lower:
            occasion = occ_name
            break

    weather = payload.weather_override or "Mild (24°C)"
    budget_max = payload.budget_max_override or user_ctx["budget_max"]

    # Parse budget from message if mentioned (e.g., 'under 2000', 'budget 2500', 'under ₹3,000')
    budget_matches = re.findall(r'(?:under|budget|below|max|within|around)?\s*(?:₹|rs\.?|inr)?\s*(\d{3,6})', msg_lower)
    if budget_matches:
        try:
            for m in budget_matches:
                val = float(m)
                if 500 <= val <= 50000:
                    budget_max = val
                    break
        except Exception:
            pass

    # Parse preferred colors from chat message
    detected_chat_colors = []
    fashion_colors = [
        "black", "white", "navy", "blue", "sky blue", "grey", "gray", "beige", "brown", "green",
        "red", "pink", "yellow", "olive", "emerald", "maroon", "burgundy", "charcoal", "khaki",
        "cream", "tan", "teal", "turquoise", "mustard", "orange", "purple", "lavender"
    ]
    for color_word in fashion_colors:
        if re.search(r'\b' + color_word + r'\b', msg_lower):
            detected_chat_colors.append(color_word.title())

    # Parse preferred style from chat message
    detected_chat_style = None
    fashion_styles = [
        "casual", "formal", "streetwear", "party", "traditional", "ethnic", "smart casual",
        "minimal", "oversized", "elegant", "sporty", "vintage", "y2k", "trendy", "classic",
        "luxury", "bohemian", "preppy", "athleisure"
    ]
    for style_word in fashion_styles:
        if style_word in msg_lower:
            detected_chat_style = style_word.title()
            break

    # Parse preferred fit & fabric
    detected_fit = None
    for f in ["oversized", "slim", "relaxed", "regular", "loose", "tailored"]:
        if f in msg_lower:
            detected_fit = f.capitalize()
            break

    detected_fabric = None
    for fb in ["silk", "cotton", "linen", "denim", "wool", "velvet", "satin", "leather"]:
        if fb in msg_lower:
            detected_fabric = fb.capitalize()
            break

    if should_recommend:
        looks = rec_engine.generate_three_looks(
            user_id=user.id,
            occasion=occasion,
            gender=active_gender,
            budget_max=budget_max,
            weather=weather,
            preferred_colors=detected_chat_colors if detected_chat_colors else None,
            preferred_style=detected_chat_style,
            preferred_fit=detected_fit,
            preferred_fabric=detected_fabric
        )
        if looks:
            recommended_outfit_data = looks[0]

            # Persist outfit in database
            db_outfit = Outfit(
                user_id=user.id,
                title=recommended_outfit_data["title"],
                style_tag=recommended_outfit_data["style_tag"],
                occasion=recommended_outfit_data["occasion"],
                total_price=recommended_outfit_data["total_price"],
                match_score=recommended_outfit_data["match_score"],
                explanation=recommended_outfit_data["explanation"],
                image_url=recommended_outfit_data["image_url"],
                weather_context=recommended_outfit_data["weather_context"],
                budget_tier=recommended_outfit_data["budget_tier"]
            )
            db.add(db_outfit)
            db.flush()

            for it in recommended_outfit_data["items"]:
                db.add(OutfitItem(outfit_id=db_outfit.id, product_id=it["product"].id, role=it["role"]))

            db.add(RecommendationHistory(
                user_id=user.id,
                outfit_id=db_outfit.id,
                gender=active_gender,
                occasion=occasion,
                favorite_colors=", ".join(detected_chat_colors or user_ctx["favorite_colors"]),
                avoid_colors=", ".join(user_ctx["avoid_colors"]),
                aesthetics=detected_chat_style or ", ".join(user_ctx["preferred_styles"]),
                budget=budget_max
            ))
            db.commit()

            outfit_response = OutfitResponse(
                id=db_outfit.id,
                title=db_outfit.title,
                style_tag=db_outfit.style_tag,
                occasion=db_outfit.occasion,
                total_price=db_outfit.total_price,
                match_score=db_outfit.match_score,
                explanation=db_outfit.explanation,
                image_url=db_outfit.image_url,
                weather_context=db_outfit.weather_context,
                budget_tier=db_outfit.budget_tier,
                items=[{"role": it["role"], "product": ProductResponse.model_validate(it["product"])} for it in recommended_outfit_data["items"]]
            )

    # Process conversation with AI stylist
    history_dicts = [{"role": m.role, "content": m.content} for m in payload.conversation_history] if payload.conversation_history else []
    chat_result = gemini_service.chat_with_stylist(
        message=payload.message,
        user_ctx={**user_ctx, "gender": active_gender},
        conversation_history=history_dicts,
        recommended_outfit=recommended_outfit_data,
        weather_context=payload.weather_override or "Mild (24°C)"
    )

    reply_text = chat_result["reply"]
    if gender_conflict_detected:
        reply_text = f"*(Note: I've adapted this recommendation for {active_gender} fashion per your message. You can permanently switch your profile gender anytime in Profile settings.)*\n\n" + reply_text

    if should_recommend and not outfit_response:
        reply_text += f"\n\nI couldn't find any {active_gender} items matching all your strict criteria for {occasion} within your ₹{budget_max:,.0f} budget. Try broadening your budget or relaxing colour restrictions!"

    return ChatResponse(
        reply=reply_text,
        outfit_recommendation=outfit_response,
        follow_up_suggestions=chat_result["follow_up_suggestions"],
        engine_used=chat_result["engine_used"],
        active_gender=active_gender,
        active_occasion=occasion
    )


@router.post("/visualize", response_model=VisualizeResponse)
def generate_outfit_visualization(payload: VisualizeRequest):
    """
    Generate an AI visual representation / lookbook canvas for a recommended outfit.
    """
    vis_data = OutfitVisualizationService.generate_visualization(
        outfit_title=payload.outfit_title,
        style_tag=payload.style_tag,
        occasion=payload.occasion,
        items_summary=payload.items_summary,
        palette=payload.palette
    )
    return VisualizeResponse(
        visualization_url=vis_data["visualization_url"],
        svg_canvas=vis_data["svg_canvas"],
        disclaimer=vis_data["disclaimer"]
    )


@router.post("/analyze-photo", response_model=PhotoAnalysisResponse)
def analyze_user_photo(
    payload: AnalyzePhotoRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    AI STYLE ANALYSIS — STEP 1 & 2:
    Validates uploaded photograph, assesses lighting conditions, extracts dominant
    and complementary clothing colors, detects fabric texture/patterns, detects clothing
    style cues, and evaluates skin tone and silhouette when suitable.
    Saves detected skin tone and silhouette into user profile.
    """
    raw_b64 = payload.photo_base64.strip() if payload.photo_base64 else ""
    if not raw_b64:
        raise HTTPException(status_code=400, detail="No photo uploaded. Please select and upload a clear photo.")

    if "," in raw_b64:
        header, raw_b64 = raw_b64.split(",", 1)

    try:
        image_bytes = base64.b64decode(raw_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid photo encoding. Please upload a standard image file.")

    try:
        analysis_data = PhotoAnalysisService.analyze_photo(
            image_bytes=image_bytes,
            filename=payload.filename
        )

        # Synchronize detected profile attributes into UserProfile
        profile = db.query(UserProfile).filter_by(user_id=user.id).first()
        if profile:
            if analysis_data.get("skin_tone", {}).get("available"):
                tone = analysis_data["skin_tone"].get("tone_family", "")
                undertone = analysis_data["skin_tone"].get("undertone", "")
                profile.skin_tone = f"{undertone} {tone}".strip()
            if analysis_data.get("silhouette", {}).get("available"):
                shape = analysis_data["silhouette"].get("estimated_shape", "")
                if shape:
                    profile.body_type = shape
            db.commit()

        return PhotoAnalysisResponse(**analysis_data)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI Photo Analysis failed to process image: {str(exc)}"
        )


@router.post("/recommend-from-analysis", response_model=AnalysisRecommendationResponse)
def recommend_from_analysis(
    payload: AnalysisRecommendationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    AI STYLE ANALYSIS — STEP 3 & 4:
    Uses centralized recommendation engine to curate complete outfits from the REAL catalogue
    matching the user's active gender, detected features, occasion, and preferences.
    """
    rec_engine = RecommendationEngine(db)
    user_ctx = rec_engine.get_user_profile_context(user.id)
    active_gender = payload.gender or user_ctx["gender"]

    # Combine photo colors with selected colors
    fav_colors = payload.selected_colors if payload.selected_colors else (payload.photo_colors or user_ctx["favorite_colors"])
    avoid_colors = payload.avoid_colors if payload.avoid_colors else user_ctx["avoid_colors"]

    raw_looks = rec_engine.generate_three_looks(
        user_id=user.id,
        occasion=payload.occasion,
        gender=active_gender,
        budget_min=payload.budget_min,
        budget_max=payload.budget_max,
        weather=payload.weather or "Mild (24°C)",
        preferred_colors=fav_colors,
        avoid_colors=avoid_colors,
        preferred_style=payload.preferred_style or payload.detected_style
    )

    persisted_looks = []
    for look in raw_looks:
        db_outfit = Outfit(
            user_id=user.id,
            title=look["title"],
            style_tag=look["style_tag"],
            occasion=look["occasion"],
            total_price=look["total_price"],
            match_score=look["match_score"],
            explanation=look["explanation"],
            image_url=look["image_url"],
            weather_context=look["weather_context"],
            budget_tier=look["budget_tier"]
        )
        db.add(db_outfit)
        db.flush()

        for it in look["items"]:
            db.add(OutfitItem(outfit_id=db_outfit.id, product_id=it["product"].id, role=it["role"]))

        db.add(RecommendationHistory(
            user_id=user.id,
            outfit_id=db_outfit.id,
            gender=active_gender,
            occasion=payload.occasion,
            favorite_colors=", ".join(fav_colors),
            avoid_colors=", ".join(avoid_colors),
            budget=payload.budget_max or user_ctx["budget_max"]
        ))

        persisted_looks.append(
            OutfitResponse(
                id=db_outfit.id,
                title=db_outfit.title,
                style_tag=db_outfit.style_tag,
                occasion=db_outfit.occasion,
                total_price=db_outfit.total_price,
                match_score=db_outfit.match_score,
                explanation=db_outfit.explanation,
                image_url=db_outfit.image_url,
                weather_context=db_outfit.weather_context,
                budget_tier=db_outfit.budget_tier,
                items=[{"role": it["role"], "product": ProductResponse.model_validate(it["product"])} for it in look["items"]]
            )
        )

    db.commit()

    return AnalysisRecommendationResponse(
        looks=persisted_looks,
        styling_rationale=f"Curated {active_gender} outfits derived from your photo analysis and color harmony palette for {payload.occasion}.",
        detected_features_used=list(set(payload.photo_colors + ([payload.detected_style] if payload.detected_style else []))),
        engine_used="Centralized Recommendation Engine (AI Style Analysis)",
        occasion=payload.occasion,
        budget_min=payload.budget_min or user_ctx["budget_min"],
        budget_max=payload.budget_max or user_ctx["budget_max"],
        weather_context=payload.weather or "Mild (24°C)"
    )


@router.post("/virtual-tryon", response_model=TryOnResponse)
def run_virtual_tryon(payload: TryOnJsonRequest):
    """
    Legacy virtual try-on route preserved for API compatibility.
    Does NOT generate synthetic images of the person wearing clothes.
    Returns real catalogue item preview with clear styling notice.
    """
    first_item_img = ""
    items_summary = []
    if payload.items:
        for it in payload.items:
            name = it.get("name", "Fashion Item")
            role = it.get("role", "piece")
            price = it.get("price", 0)
            items_summary.append(f"{role.capitalize()}: {name} (₹{price})")
            if not first_item_img and it.get("image_url"):
                first_item_img = it.get("image_url")

    if not first_item_img:
        first_item_img = "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80"

    return TryOnResponse(
        status="success",
        tryon_image_url=first_item_img,
        outfit_title=payload.outfit_title or "Personalized Outfit Recommendation",
        items_summary=items_summary or ["Coordinated outfit from authentic catalogue"],
        disclaimer="AI Personal Stylist recommends authentic catalogue products based on your style profile. Synthetic try-on images are not generated.",
        mode="ai_style_analysis",
        processing_time_sec=0.25
    )
