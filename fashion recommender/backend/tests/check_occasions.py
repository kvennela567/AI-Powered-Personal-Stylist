import sys
import os
sys.path.insert(0, os.path.abspath("."))
from backend.services.recommendation_service import RecommendationEngine
from backend.models.database import SessionLocal
from backend.models.entities import User

db = SessionLocal()
engine = RecommendationEngine(db)
user = db.query(User).filter(User.username == "demo_user").first()
print(f"User: {user.username}, Gender: {user.profile.gender if user.profile else 'None'}")
print(f"Profile style preferences: {[sp.style_name for sp in user.style_preferences] if user else 'None'}")

for occ in ["Office", "College", "Engagement", "Gym"]:
    res = engine.generate_three_looks(user_id=user.id, occasion=occ)
    print(f"\n==================== OCCASION: {occ} ====================")
    for i, look in enumerate(res):
        items_desc = ", ".join([f"{it.get('role')}: {it['product'].name} ({it['product'].subcategory}, {it['product'].color}, INR {it['product'].price})" for it in look.get('items', [])])
        print(f"Look {i+1} [{look.get('budget_tier')}] ({look.get('title')}) [Total INR {look.get('total_price')}]:\n  {items_desc}")
db.close()
