from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.entities import User, Outfit, SavedOutfit, RecommendationHistory
from ..models.schemas import OutfitResponse, ProductResponse
from .users import get_current_user

router = APIRouter(prefix="/api/outfits", tags=["Outfits"])


@router.get("/saved", response_model=List[OutfitResponse])
def get_saved_outfits(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all outfits saved by the active user."""
    saved_entries = db.query(SavedOutfit).filter_by(user_id=user.id).order_by(SavedOutfit.saved_at.desc()).all()
    outfits = []
    for se in saved_entries:
        o = se.outfit
        if o:
            items_list = [{"role": it.role, "product": ProductResponse.model_validate(it.product)} for it in o.items if it.product]
            outfits.append(
                OutfitResponse(
                    id=o.id,
                    title=o.title,
                    style_tag=o.style_tag,
                    occasion=o.occasion,
                    total_price=o.total_price,
                    match_score=o.match_score,
                    explanation=o.explanation,
                    image_url=o.image_url,
                    weather_context=o.weather_context,
                    budget_tier=o.budget_tier,
                    items=items_list
                )
            )
    return outfits


@router.post("/saved/{outfit_id}")
def save_outfit(
    outfit_id: int,
    notes: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save an outfit to 'My Outfits'."""
    outfit = db.query(Outfit).filter_by(id=outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    existing = db.query(SavedOutfit).filter_by(user_id=user.id, outfit_id=outfit_id).first()
    if existing:
        return {"status": "already_saved", "message": "Outfit is already in your saved collection."}

    saved = SavedOutfit(user_id=user.id, outfit_id=outfit_id, notes=notes)
    db.add(saved)
    db.commit()
    return {"status": "success", "message": "Outfit saved to My Outfits."}


@router.delete("/saved/{outfit_id}")
def remove_saved_outfit(
    outfit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an outfit from saved collection."""
    entry = db.query(SavedOutfit).filter_by(user_id=user.id, outfit_id=outfit_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Saved outfit not found")

    db.delete(entry)
    db.commit()
    return {"status": "success", "message": "Outfit removed from saved collection."}


@router.get("/history", response_model=List[OutfitResponse])
def get_recommendation_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve recent recommendation history timeline."""

    history_records = (
        db.query(RecommendationHistory)
        .filter_by(user_id=user.id)
        .order_by(RecommendationHistory.generated_at.desc())
        .limit(limit)
        .all()
    )

    outfits = []
    seen_ids = set()
    for hr in history_records:
        if hr.outfit_id in seen_ids:
            continue
        seen_ids.add(hr.outfit_id)
        o = hr.outfit
        if o:
            items_list = [{"role": it.role, "product": ProductResponse.model_validate(it.product)} for it in o.items if it.product]
            outfits.append(
                OutfitResponse(
                    id=o.id,
                    title=o.title,
                    style_tag=o.style_tag,
                    occasion=o.occasion,
                    total_price=o.total_price,
                    match_score=o.match_score,
                    explanation=o.explanation,
                    image_url=o.image_url,
                    weather_context=o.weather_context,
                    budget_tier=o.budget_tier,
                    items=items_list
                )
            )
    return outfits


@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit_by_id(outfit_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed information about a single outfit."""
    outfit = db.query(Outfit).filter_by(id=outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    items_list = [{"role": it.role, "product": ProductResponse.model_validate(it.product)} for it in outfit.items if it.product]
    return OutfitResponse(
        id=outfit.id,
        title=outfit.title,
        style_tag=outfit.style_tag,
        occasion=outfit.occasion,
        total_price=outfit.total_price,
        match_score=outfit.match_score,
        explanation=outfit.explanation,
        image_url=outfit.image_url,
        weather_context=outfit.weather_context,
        budget_tier=outfit.budget_tier,
        items=items_list
    )
