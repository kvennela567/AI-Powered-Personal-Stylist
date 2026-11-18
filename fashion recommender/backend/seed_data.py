"""
Comprehensive e-commerce fashion product database seed.
Loads 1,100+ structured products across Male, Female, and Unisex
covering all 27 Occasions, 26+ Colors, 20 Aesthetics, and detailed garment attributes.
"""

import os
import json
from .data_generator import generate_structured_catalog

CATALOG_FILE = os.path.join(os.path.dirname(__file__), "fashion_catalog.json")


def load_products_data():
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) >= 1000:
                    return data
        except Exception:
            pass
    # Fallback to generator
    data = generate_structured_catalog()
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


PRODUCTS_SEED_DATA = load_products_data()


def seed_database(db):
    """
    Populate database with 1,000+ fashion products, demo user, profile, and initial preferences.
    Ensures existing databases are updated seamlessly.
    """
    from .models.entities import User, UserProfile, UserColorPreference, UserStylePreference, Product

    # 1. Check existing products count
    current_count = db.query(Product).count()
    if current_count < 1000:
        # Populate catalog
        print(f"Current catalog size is {current_count}. Synchronizing full 1,000+ product catalog...")
        existing_names = set(row[0] for row in db.query(Product.name).all())
        added_count = 0
        for p_data in PRODUCTS_SEED_DATA:
            if p_data["name"] not in existing_names:
                # Filter to only valid columns on Product model
                prod_kwargs = {k: v for k, v in p_data.items() if hasattr(Product, k)}
                db.add(Product(**prod_kwargs))
                added_count += 1
                if added_count % 200 == 0:
                    db.commit()
        db.commit()
        print(f"Catalog successfully seeded with {db.query(Product).count()} total products.")

    # 2. Check or create default demo user
    user = db.query(User).filter_by(username="demo_user").first()
    if not user:
        user = User(
            username="demo_user",
            email="demo@stylist.fashion.ai"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Check or create default user profile
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=user.id,
            name="Rhea Sharma",
            age_group="20-29",
            gender="Female",
            height="168 cm",
            weight="58 kg",
            clothing_size="M",
            body_type="Hourglass",
            skin_tone="Neutral / Medium",
            custom_body_type="",
            include_unisex=False,
            strict_preferences=True,
            budget_min=1500.0,
            budget_max=6500.0,
            preferred_fit="Relaxed",
            preferred_sleeve_length="Full Sleeve",
            preferred_clothing_length="Standard",
            preferred_materials="Cotton, Linen, Silk",
            preferred_footwear="Sneakers, Loafers, Heels",
            preferred_accessories="Minimalist watch, Canvas backpack, Pendant",
            preferred_brands="All Brands",
            disliked_clothing="Skinny jeans, Neon colors",
            custom_style_description="I love effortless, clean minimalist and elegant styling with comfortable relaxed fits."
        )
        db.add(profile)
        db.commit()

        # Seed color preferences
        favorite_colors = ["Navy", "White", "Beige", "Olive", "Black"]
        avoid_colors = ["Neon", "Orange"]

        for c in favorite_colors:
            db.add(UserColorPreference(user_id=user.id, color_name=c, preference_type="favorite"))
        for c in avoid_colors:
            db.add(UserColorPreference(user_id=user.id, color_name=c, preference_type="avoid"))

        # Seed style preferences
        styles = ["Casual", "Minimal", "Smart casual", "Streetwear"]
        for s in styles:
            db.add(UserStylePreference(user_id=user.id, style_name=s))

        db.commit()
        print("Demo user, profile, and initial preferences initialized.")
