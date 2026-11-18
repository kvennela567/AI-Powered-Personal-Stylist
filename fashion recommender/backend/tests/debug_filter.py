import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product, User
from backend.services.recommendation_service import RecommendationEngine

db = SessionLocal()
engine = RecommendationEngine(db)
user = db.query(User).filter(User.username == "demo_user").first()
user_ctx = engine.get_user_profile_context(user.id)
print("User ctx:", user_ctx)

all_prods = db.query(Product).all()
for occ in ["Office", "College", "Engagement", "Gym"]:
    passed = []
    failed_reasons = {}
    for p in all_prods:
        ok, reason = engine.passes_hard_filters(
            product=p,
            gender="Female",
            include_unisex=False,
            occasion=occ,
            avoid_colors=user_ctx["avoid_colors"],
            favorite_colors=user_ctx["favorite_colors"],
            preferred_styles=user_ctx["preferred_styles"],
            preferred_fit=user_ctx["preferred_fit"],
            preferred_sleeve=user_ctx["preferred_sleeve_length"],
            preferred_length=user_ctx["preferred_clothing_length"],
            preferred_fabrics=user_ctx["preferred_materials"],
            strict_preferences=user_ctx["strict_preferences"],
            is_main_garment=(p.category == "Clothing")
        )
        if ok:
            passed.append(p)
        else:
            failed_reasons[reason] = failed_reasons.get(reason, 0) + 1
    print(f"\nOccasion: {occ} -> {len(passed)} products passed hard filters")
    print(f"Passed subcategories: {set(p.subcategory for p in passed)}")
    cats = {p.category for p in passed}
    print(f"Passed categories: {cats}")
    compat = {p.outfit_compatibility for p in passed}
    print(f"Passed outfit_compatibilities: {compat}")
    # Check tops, bottoms, complete_sets, footwear, accessories
    tops = [p for p in passed if p.outfit_compatibility == "top" or p.subcategory in ["Shirts", "T-Shirts", "Tops", "Kurtis", "Blazers"]]
    bottoms = [p for p in passed if p.outfit_compatibility == "bottom" or p.subcategory in ["Jeans", "Trousers", "Chinos", "Skirts"]]
    complete = [p for p in passed if p.outfit_compatibility == "complete_outfit" or p.subcategory in ["Dresses", "Lehengas", "Sarees", "Designer sarees", "Salwar suits", "Jumpsuits"]]
    shoes = [p for p in passed if p.category == "Footwear" or p.outfit_compatibility == "footwear"]
    accs = [p for p in passed if p.category == "Accessories" or p.outfit_compatibility == "accessory"]
    print(f"Tops: {len(tops)}, Bottoms: {len(bottoms)}, Complete: {len(complete)}, Shoes: {len(shoes)}, Accs: {len(accs)}")
db.close()
