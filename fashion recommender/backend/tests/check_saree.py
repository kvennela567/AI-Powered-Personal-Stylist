import sys, os
sys.path.insert(0, os.path.abspath("."))
from backend.models.database import SessionLocal
from backend.models.entities import Product
db = SessionLocal()
count = db.query(Product).filter(
    Product.subcategory.in_(['Sarees', 'Designer sarees', 'Lehengas']),
    (Product.supported_occasions.like('%Office%') | Product.supported_occasions.like('%Gym%'))
).count()
print("Count of bad sarees/lehengas with Office or Gym:", count)
db.close()
