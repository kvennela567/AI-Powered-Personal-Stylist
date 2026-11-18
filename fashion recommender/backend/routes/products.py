from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.entities import Product
from ..models.schemas import (
    ProductResponse,
    MatchOutfitRequest,
    MatchOutfitResponse,
    MatchOutfitItemResult
)
from ..services.product_search_service import ProductSearchService

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    gender: Optional[str] = None,
    include_unisex: bool = False,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    color: Optional[str] = None,
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    material: Optional[str] = None,
    fit: Optional[str] = None,
    size: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Query fashion product catalogue with rich multi-faceted filtering and
    token-based intelligent search matching across gender, names, colors, materials, fits, and styles.
    """
    products = ProductSearchService.search_catalogue(
        db=db,
        query_text=search,
        gender=gender,
        include_unisex=include_unisex,
        category=category,
        subcategory=subcategory,
        color=color,
        style=style,
        occasion=occasion,
        material=material,
        fit=fit,
        size=size,
        min_price=min_price,
        max_price=max_price,
        limit=limit
    )
    return products


@router.post("/match-outfit", response_model=MatchOutfitResponse)
def match_outfit_products(
    payload: MatchOutfitRequest,
    db: Session = Depends(get_db)
):
    """
    Matches recommended outfit descriptions (e.g. 'Black oversized T-shirt', 'Blue straight-fit jeans',
    'White sneakers') to actual product records in the catalogue, with catalogue image and metadata.
    """
    matched_items = []
    total_price = 0.0

    for item_query in payload.items:
        match_info = ProductSearchService.match_outfit_item(
            db=db,
            role=item_query.role,
            query_text=item_query.query,
            gender=payload.gender,
            max_price=payload.max_price
        )

        matched_p = match_info["matched_product"]
        if matched_p:
            total_price += matched_p.price
            matched_items.append(
                MatchOutfitItemResult(
                    role=item_query.role,
                    query=item_query.query,
                    matched_product=ProductResponse.model_validate(matched_p),
                    confidence_score=match_info["confidence_score"],
                    alternatives=[ProductResponse.model_validate(alt) for alt in match_info["alternatives"]]
                )
            )

    return MatchOutfitResponse(
        outfit_title="Shop This Look — Coordinated Pieces",
        items=matched_items,
        total_price=round(total_price, 2)
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed product information by ID."""
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
