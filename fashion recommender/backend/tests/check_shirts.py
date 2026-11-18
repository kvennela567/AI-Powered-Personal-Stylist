import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product

db = SessionLocal()
shirts = db.query(Product).filter(Product.gender == "Female", Product.subcategory == "Shirts").count()
blazers = db.query(Product).filter(Product.gender == "Female", Product.subcategory == "Blazers").count()
trousers = db.query(Product).filter(Product.gender == "Female", Product.subcategory == "Trousers").count()
kurtis = db.query(Product).filter(Product.gender == "Female", Product.subcategory == "Kurtis").count()
print(f"Shirts: {shirts}, Blazers: {blazers}, Trousers: {trousers}, Kurtis: {kurtis}")

# Check which shirts and blazers pass the office hard filter
prods = db.query(Product).filter(
    Product.gender == "Female",
    Product.subcategory.in_(["Shirts", "Blazers"]),
    Product.outfit_compatibility == "top"
).all()
print(f"\nShirts + Blazers with outfit_compatibility='top': {len(prods)}")
for p in prods[:5]:
    print(f"  {p.name} | Occ: {p.occasion} | Supp: {p.supported_occasions}")
db.close()

