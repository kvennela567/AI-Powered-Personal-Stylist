import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product, User
from backend.services.recommendation_service import RecommendationEngine

db = SessionLocal()
engine = RecommendationEngine(db)
user = db.query(User).filter(User.username == "demo_user").first()
user_ctx = engine.get_user_profile_context(user.id)

# Check scoring of Kurtis vs Shirts/Blazers for Office
prods_kurtis = db.query(Product).filter(
    Product.gender == "Female",
    Product.subcategory == "Kurtis"
).all()

prods_shirts = db.query(Product).filter(
    Product.gender == "Female",
    Product.subcategory.in_(["Shirts", "Blazers"])
).all()

print("== KURTI SCORES FOR OFFICE ==")
kurti_scores = []
for p in prods_kurtis:
    score = engine.calculate_personalization_score(p, user_ctx, "Office", "Formal", "Mild (24C)")
    kurti_scores.append((score, p))
kurti_scores.sort(key=lambda x: x[0], reverse=True)
for score, p in kurti_scores[:5]:
    print(f"  {score:.1f} | {p.name} | {p.color} | {p.style_archetype}")

print("\n== SHIRT/BLAZER SCORES FOR OFFICE ==")
shirt_scores = []
for p in prods_shirts:
    score = engine.calculate_personalization_score(p, user_ctx, "Office", "Formal", "Mild (24C)")
    shirt_scores.append((score, p))
shirt_scores.sort(key=lambda x: x[0], reverse=True)
for score, p in shirt_scores[:5]:
    print(f"  {score:.1f} | {p.name} | {p.color} | {p.style_archetype}")

db.close()
