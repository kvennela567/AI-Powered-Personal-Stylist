import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product
from backend.services.recommendation_service import normalize_color, get_color_family

db = SessionLocal()

# Check which tops pass office filter
prods = db.query(Product).filter(
    Product.gender == "Female",
    Product.category == "Clothing",
    Product.outfit_compatibility == "top"
).all()

print(f"Total female tops: {len(prods)}")
print("\nTops with Office/Business/Formal in occasion or supported_occasions:")
for p in prods:
    supp = p.supported_occasions or ""
    occ = p.occasion or ""
    if any(k in occ.lower() or k in supp.lower() for k in ["office", "business", "formal", "interview"]):
        print(f"  ID {p.id}: {p.name} | Subcat: {p.subcategory} | Style: {p.style_archetype} | Color: {p.color} | Occasion: {occ}")

db.close()

