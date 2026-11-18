import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product, User
from backend.services.recommendation_service import RecommendationEngine

db = SessionLocal()
engine = RecommendationEngine(db)
user = db.query(User).filter(User.username == "demo_user").first()
user_ctx = engine.get_user_profile_context(user.id)

# Check which Shirts/Blazers pass the Office hard filter
prods = db.query(Product).filter(
    Product.gender == "Female",
    Product.subcategory.in_(["Shirts", "Blazers"]),
    Product.outfit_compatibility == "top"
).all()

print(f"Testing {len(prods)} Shirts+Blazers against Office filter:")
passed = []
for p in prods:
    ok, reason = engine.passes_hard_filters(
        product=p,
        gender="Female",
        include_unisex=False,
        occasion="Office",
        avoid_colors=user_ctx["avoid_colors"],
        favorite_colors=user_ctx["favorite_colors"],
        preferred_styles=[],
        preferred_fit=None,
        preferred_sleeve=None,
        preferred_length=None,
        preferred_fabrics=[],
        strict_preferences=False,
        is_main_garment=True
    )
    if ok:
        passed.append(p)
        print(f"  PASS: {p.name} | Color: {p.color} | Style: {p.style_archetype}")
    else:
        print(f"  FAIL: {p.name} | Reason: {reason}")

print(f"\n{len(passed)}/{len(prods)} passed")
db.close()

