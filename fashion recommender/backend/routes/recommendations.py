from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.entities import User, Outfit, OutfitItem, RecommendationHistory
from ..models.schemas import MultiLookResponse, OutfitResponse, MixMatchRequest, MixMatchResponse, MixMatchAlternative, ProductResponse
from ..services.recommendation_service import RecommendationEngine
from .users import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/looks", response_model=MultiLookResponse)
def get_outfit_recommendations(
    occasion: str = Query("College", description="Occasion (College, Office, Engagement, etc.)"),
    gender: Optional[str] = Query(None, description="Gender override (Female, Male)"),
    budget_min: Optional[float] = Query(None, description="Custom minimum budget in ₹"),
    budget_max: Optional[float] = Query(None, description="Custom maximum budget in ₹"),
    weather: str = Query("Mild (24°C)", description="Weather context hint"),
    preferred_style: Optional[str] = Query(None, description="Style override (Streetwear, Minimal, etc.)"),
    color: Optional[str] = Query(None, description="Preferred color override"),
    fit: Optional[str] = Query(None, description="Fit override (Oversized, Slim, etc.)"),
    fabric: Optional[str] = Query(None, description="Fabric override (Silk, Cotton, etc.)"),
    include_unisex: Optional[bool] = Query(None, description="Include unisex items"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate 3 distinct curated looks considering gender, occasion, style, body type,
    colors, fit, fabric, budget, weather, and learned preference weights.
    """
    engine = RecommendationEngine(db)
    user_ctx = engine.get_user_profile_context(user.id)
    active_gender = gender or user_ctx["gender"]

    color_override = [color] if color else None
    raw_looks = engine.generate_three_looks(
        user_id=user.id,
        occasion=occasion,
        gender=active_gender,
        budget_min=budget_min,
        budget_max=budget_max,
        weather=weather,
        preferred_colors=color_override,
        preferred_style=preferred_style,
        preferred_fit=fit,
        preferred_fabric=fabric,
        include_unisex=include_unisex
    )

    if not raw_looks:
        return MultiLookResponse(
            looks=[],
            occasion=occasion,
            user_budget_min=budget_min if budget_min is not None else user_ctx["budget_min"],
            user_budget_max=budget_max if budget_max is not None else user_ctx["budget_max"],
            weather_context=weather,
            generated_by="AI Stylist Recommendation Engine",
            message=f"No matching {active_gender} outfits found for occasion '{occasion}' with the active filters. Try relaxing your budget or colour preferences."
        )

    persisted_looks = []
    for look in raw_looks:
        # Save outfit record in DB
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

        # Link items
        for it in look["items"]:
            db_item = OutfitItem(
                outfit_id=db_outfit.id,
                product_id=it["product"].id,
                role=it["role"]
            )
            db.add(db_item)

        # Log recommendation history with full contextual snapshot
        history_entry = RecommendationHistory(
            user_id=user.id,
            outfit_id=db_outfit.id,
            gender=active_gender,
            occasion=occasion,
            favorite_colors=", ".join(color_override or user_ctx["favorite_colors"]),
            avoid_colors=", ".join(user_ctx["avoid_colors"]),
            aesthetics=preferred_style or ", ".join(user_ctx["preferred_styles"]),
            preferred_fit=fit or user_ctx["preferred_fit"],
            preferred_fabric=fabric or ", ".join(user_ctx["preferred_materials"]),
            budget=budget_max if budget_max is not None else user_ctx["budget_max"]
        )
        db.add(history_entry)

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

    return MultiLookResponse(
        looks=persisted_looks,
        occasion=occasion,
        user_budget_min=budget_min if budget_min is not None else user_ctx["budget_min"],
        user_budget_max=budget_max if budget_max is not None else user_ctx["budget_max"],
        weather_context=weather,
        generated_by="AI Stylist Recommendation Engine"
    )


@router.post("/mix-match", response_model=MixMatchResponse)
def get_mix_match_alternatives(
    payload: MixMatchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Customize outfit by changing a single item while preserving color and style harmony.
    """
    engine = RecommendationEngine(db)
    user_ctx = engine.get_user_profile_context(user.id)

    # Use the same recommendation engine filters to get compatible alternatives
    from ..models.entities import Product
    q = db.query(Product).filter(
        Product.availability == True,
        Product.gender.in_([user_ctx["gender"], "Unisex"] if user_ctx["include_unisex"] else [user_ctx["gender"]])
    )
    if payload.role_to_replace in ["top", "bottom", "footwear", "accessory", "complete_outfit"]:
        q = q.filter(Product.outfit_compatibility == payload.role_to_replace)

    candidates = q.limit(20).all()
    alternatives = []
    for c in candidates:
        if c.id not in payload.accepted_product_ids:
            score = engine.calculate_personalization_score(
                product=c,
                user_ctx=user_ctx,
                target_occasion=payload.occasion or "Casual outing",
                target_style=user_ctx["preferred_styles"][0] if user_ctx["preferred_styles"] else "Casual",
                weather_hint=payload.weather or "Mild"
            )
            alternatives.append(
                MixMatchAlternative(
                    replacement_product=ProductResponse.model_validate(c),
                    compatibility_score=round(score, 1),
                    new_total_price=c.price,
                    explanation=f"Harmonious {c.color} {c.fabric} {c.subcategory} ({c.brand})"
                )
            )

    alternatives.sort(key=lambda x: x.compatibility_score, reverse=True)

    return MixMatchResponse(
        role=payload.role_to_replace,
        alternatives=alternatives[:4]
    )
