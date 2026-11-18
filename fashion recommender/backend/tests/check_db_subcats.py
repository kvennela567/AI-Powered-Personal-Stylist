import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product
from collections import Counter

db = SessionLocal()
for occ in ["Office", "College", "Engagement", "Gym"]:
    print(f"\n==================== PRODUCTS FOR {occ} (FEMALE) ====================")
    prods = db.query(Product).filter(
        Product.gender == "Female",
        (Product.occasion == occ) | (Product.supported_occasions.like(f"%{occ}%"))
    ).all()
    subcats = Counter([p.subcategory for p in prods])
    print(f"Total products: {len(prods)}")
    print("Subcategories:", dict(subcats))
db.close()

