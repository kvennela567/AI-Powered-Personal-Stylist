import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product
from backend.services.recommendation_service import normalize_color, get_color_family

db = SessionLocal()
prods = db.query(Product).filter(
    Product.gender.in_(["Female", "Unisex"]),
    Product.category == "Clothing"
).all()

bottoms = [p for p in prods if p.outfit_compatibility == "bottom" or p.subcategory in ["Jeans", "Trousers", "Chinos", "Skirts"]]
print(f"Total female/unisex bottoms: {len(bottoms)}")
for b in bottoms:
    col = normalize_color(b.color)
    fam = get_color_family(b.color)
    print(f"ID {b.id}: {b.name} | Subcat: {b.subcategory} | Color: {b.color} (norm: {col}, fam: {fam}) | Occ: {b.occasion} | Supp: {b.supported_occasions}")
db.close()
