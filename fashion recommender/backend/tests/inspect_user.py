import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import User

db = SessionLocal()
user = db.query(User).filter(User.username == "demo_user").first()
p = user.profile
print("Gender:", p.gender)
print("Body Type:", p.body_type)
print("Skin Tone:", p.skin_tone)
print("Budget:", p.budget_min, "-", p.budget_max)
print("Preferred fit:", p.preferred_fit)
print("Preferred materials:", p.preferred_materials)
print("Preferred footwear:", p.preferred_footwear)
print("Preferred accessories:", p.preferred_accessories)
print("Strict preferences:", p.strict_preferences)
print("Color prefs:", [(cp.color_name, cp.preference_type) for cp in user.color_preferences])
print("Style prefs:", [sp.style_name for sp in user.style_preferences])
db.close()

