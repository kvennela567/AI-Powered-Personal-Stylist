import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product
from collections import defaultdict

db = SessionLocal()
prods = db.query(Product).all()
print(f"Total products in DB: {len(prods)}")

# Check female products
female_prods = [p for p in prods if p.gender == "Female"]
male_prods = [p for p in prods if p.gender == "Male"]
unisex_prods = [p for p in prods if p.gender == "Unisex"]
print(f"Female: {len(female_prods)}, Male: {len(male_prods)}, Unisex: {len(unisex_prods)}")

# Check how occasions are populated
occ_counts = defaultdict(int)
for p in female_prods:
    occ_counts[p.occasion] += 1
print("\nFemale products primary occasion counts:")
for occ, count in sorted(occ_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {occ}: {count}")

db.close()

