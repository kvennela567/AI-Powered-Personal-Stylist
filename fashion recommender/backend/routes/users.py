from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.entities import User, UserProfile, UserColorPreference, UserStylePreference
from ..models.schemas import (
    UserProfileSchema,
    UserProfileResponse,
    UserRegisterRequest,
    UserLoginRequest,
    UserAuthResponse
)

router = APIRouter(prefix="/api/users", tags=["Users"])


def get_current_user(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[int] = Query(None, description="Optional user ID override")
) -> User:
    """
    Identifies the active user cleanly:
    1. If user_id query param is supplied: finds by ID.
    2. If X-User-Id header is supplied (int ID or string username): finds by ID or username.
    3. Defaults to 'demo_user' (or first user in the database) so single-user demo continues seamlessly.
    """
    target = None
    if user_id is not None:
        target = db.query(User).filter_by(id=user_id).first()
        if not target:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return target

    if x_user_id:
        val = str(x_user_id).strip()
        if val.isdigit():
            target = db.query(User).filter_by(id=int(val)).first()
        if not target:
            target = db.query(User).filter_by(username=val).first()
        if not target:
            raise HTTPException(status_code=404, detail=f"User '{x_user_id}' not found")
        return target

    # Default fallback to demo_user or first available user
    user = db.query(User).filter_by(username="demo_user").first()
    if not user:
        user = db.query(User).first()
    if not user:
        user = User(username="demo_user", email="demo@stylist.fashion.ai")
        db.add(user)
        db.commit()
        db.refresh(user)
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()

    return user


def build_user_profile_response(user: User, db: Session) -> UserProfileResponse:
    """Helper to assemble a complete UserProfileResponse from DB records."""
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    fav_colors = [
        c.color_name for c in db.query(UserColorPreference).filter_by(user_id=user.id, preference_type="favorite").all()
    ]
    avoid_colors = [
        c.color_name for c in db.query(UserColorPreference).filter_by(user_id=user.id, preference_type="avoid").all()
    ]
    styles = [
        s.style_name for s in db.query(UserStylePreference).filter_by(user_id=user.id).all()
    ]

    return UserProfileResponse(
        id=profile.id,
        user_id=user.id,
        name=profile.name or "Rhea Sharma",
        age_group=profile.age_group or "20-29",
        gender=profile.gender or "Female",
        height=profile.height or "168 cm",
        weight=profile.weight or "58 kg",
        clothing_size=profile.clothing_size or "M",
        body_type=profile.body_type or "Hourglass",
        custom_body_type=profile.custom_body_type or "",
        skin_tone=profile.skin_tone or "Neutral / Medium",
        include_unisex=profile.include_unisex if profile.include_unisex is not None else False,
        strict_preferences=profile.strict_preferences if profile.strict_preferences is not None else True,
        budget_min=profile.budget_min if profile.budget_min is not None else 1500.0,
        budget_max=profile.budget_max if profile.budget_max is not None else 6500.0,
        preferred_fit=profile.preferred_fit or "Relaxed",
        preferred_sleeve_length=profile.preferred_sleeve_length or "Full Sleeve",
        preferred_clothing_length=profile.preferred_clothing_length or "Standard",
        preferred_materials=profile.preferred_materials or "Cotton, Linen, Silk",
        preferred_footwear=profile.preferred_footwear or "Sneakers, Loafers, Heels",
        preferred_accessories=profile.preferred_accessories or "Minimal Watch, Canvas Backpack",
        preferred_brands=profile.preferred_brands or "All Brands",
        disliked_clothing=profile.disliked_clothing or "Skinny jeans, Neon colors",
        custom_style_description=profile.custom_style_description or "I enjoy relaxed, contemporary casual looks with earthy tones.",
        favorite_colors=fav_colors or ["Navy", "White", "Beige", "Olive", "Black"],
        avoid_colors=avoid_colors or ["Neon", "Orange"],
        preferred_styles=styles or ["Casual", "Minimal", "Smart casual", "Streetwear"],
    )


@router.post("/register", response_model=UserAuthResponse)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user with their own dedicated profile and styling preferences.
    Guarantees user data isolation.
    """
    existing = db.query(User).filter_by(username=payload.username).first()
    if existing:
        profile_res = build_user_profile_response(existing, db)
        return UserAuthResponse(
            user_id=existing.id,
            id=existing.id,
            username=existing.username,
            email=existing.email or "",
            message="User already exists, logged in successfully.",
            profile=profile_res
        )

    new_user = User(
        username=payload.username,
        email=payload.email or f"{payload.username}@stylist.fashion.ai"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create default user profile
    profile = UserProfile(
        user_id=new_user.id,
        name=payload.name or payload.username,
        gender="Female",
        height="168 cm",
        weight="58 kg",
        clothing_size="M",
        body_type="Hourglass",
        skin_tone="Neutral / Medium",
        include_unisex=False,
        strict_preferences=True,
        budget_min=1500.0,
        budget_max=6500.0,
        preferred_fit="Relaxed"
    )
    db.add(profile)

    # Initial default color preferences
    for c in ["Navy", "White", "Beige", "Olive", "Black"]:
        db.add(UserColorPreference(user_id=new_user.id, color_name=c, preference_type="favorite"))
    for c in ["Neon", "Orange"]:
        db.add(UserColorPreference(user_id=new_user.id, color_name=c, preference_type="avoid"))

    # Initial default style preferences
    for s in ["Casual", "Minimal", "Smart casual", "Streetwear"]:
        db.add(UserStylePreference(user_id=new_user.id, style_name=s))

    db.commit()

    profile_res = build_user_profile_response(new_user, db)
    return UserAuthResponse(
        user_id=new_user.id,
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        message="User registered successfully.",
        profile=profile_res
    )


@router.post("/login", response_model=UserAuthResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate or switch to a specific user by username."""
    user = (
        db.query(User).filter(
            (User.username == payload.username) | (User.email == payload.username)
        ).first()
    )
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{payload.username}' not found.")

    profile_res = build_user_profile_response(user, db)
    return UserAuthResponse(
        user_id=user.id,
        id=user.id,
        username=user.username,
        email=user.email or "",
        message="Logged in successfully.",
        profile=profile_res
    )


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the active user's style profile and preferences."""
    return build_user_profile_response(user, db)


@router.put("/me", response_model=UserProfileResponse)
def update_current_user_profile(
    payload: UserProfileSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update active user profile, color palette, and style preferences."""
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    # Update basic profile fields
    profile.name = payload.name
    profile.age_group = payload.age_group
    profile.gender = payload.gender
    profile.height = payload.height
    profile.weight = payload.weight or profile.weight
    profile.clothing_size = payload.clothing_size
    profile.body_type = payload.body_type
    profile.custom_body_type = payload.custom_body_type or ""
    profile.skin_tone = payload.skin_tone or profile.skin_tone
    profile.include_unisex = payload.include_unisex if payload.include_unisex is not None else False
    profile.strict_preferences = payload.strict_preferences if payload.strict_preferences is not None else True
    profile.budget_min = payload.budget_min
    profile.budget_max = payload.budget_max
    profile.preferred_fit = payload.preferred_fit
    profile.preferred_sleeve_length = payload.preferred_sleeve_length
    profile.preferred_clothing_length = payload.preferred_clothing_length
    profile.preferred_materials = payload.preferred_materials
    profile.preferred_footwear = payload.preferred_footwear
    profile.preferred_accessories = payload.preferred_accessories
    profile.preferred_brands = payload.preferred_brands or "All Brands"
    profile.disliked_clothing = payload.disliked_clothing
    profile.custom_style_description = payload.custom_style_description

    # Replace color preferences
    db.query(UserColorPreference).filter_by(user_id=user.id).delete()
    for fav in payload.favorite_colors:
        db.add(UserColorPreference(user_id=user.id, color_name=fav, preference_type="favorite"))
    for avoid in payload.avoid_colors:
        db.add(UserColorPreference(user_id=user.id, color_name=avoid, preference_type="avoid"))

    # Replace style preferences
    db.query(UserStylePreference).filter_by(user_id=user.id).delete()
    for st in payload.preferred_styles:
        db.add(UserStylePreference(user_id=user.id, style_name=st))

    db.commit()
    db.refresh(profile)

    return build_user_profile_response(user, db)


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profile_by_id(user_id: int, db: Session = Depends(get_db)):
    """Retrieve profile for a specific user ID."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return build_user_profile_response(user, db)
