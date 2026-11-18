"""
Intelligent Product and Image Search Service for Fashion Retail Catalogue.

Provides flexible, multi-attribute, token-based matching across:
- Gender
- Product name
- Category & Subcategory
- Color & Color Family
- Material / Fabric
- Fit
- Style & Style Archetype
- Occasion
- Price & Size
- Semantic fashion synonyms (e.g. 'jeans' <-> 'denim', 'tee' <-> 't-shirt')
"""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.entities import Product

# Fashion synonyms and category heuristics
SYNONYMS = {
    "jeans": ["jeans", "denim"],
    "denim": ["denim", "jeans"],
    "tee": ["tee", "t-shirt", "tshirt", "t-shirts"],
    "t-shirt": ["t-shirt", "tee", "tshirt", "t-shirts"],
    "tshirt": ["t-shirt", "tee", "tshirt", "t-shirts"],
    "sneakers": ["sneakers", "shoes", "trainers", "kicks"],
    "shoes": ["shoes", "sneakers", "loafers", "boots", "heels", "sandals"],
    "kicks": ["sneakers", "shoes"],
    "loafers": ["loafers", "shoes"],
    "boots": ["boots", "shoes"],
    "heels": ["heels", "shoes", "sandals"],
    "sandals": ["sandals", "shoes"],
    "blazer": ["blazer", "suit", "jacket"],
    "jacket": ["jacket", "blazer", "outerwear"],
    "hoodie": ["hoodie", "sweatshirt"],
    "sweatshirt": ["sweatshirt", "hoodie"],
    "pants": ["trousers", "pants", "chinos", "jeans"],
    "trousers": ["trousers", "pants", "chinos"],
    "bag": ["bag", "backpack", "handbag", "tote", "clutch"],
    "backpack": ["backpack", "bag"],
    "handbag": ["handbag", "bag", "clutch"],
    "clutch": ["clutch", "bag", "handbag"],
    "watch": ["watch", "timepiece"],
    "shades": ["sunglasses", "glasses"],
    "sunglasses": ["sunglasses", "shades"],
    "saree": ["saree", "sarees"],
    "sarees": ["sarees", "saree"],
    "lehenga": ["lehenga", "lehengas"],
    "lehengas": ["lehengas", "lehenga"],
    "sherwani": ["sherwani", "sherwanis"],
    "sherwanis": ["sherwanis", "sherwani"],
    "kurta": ["kurta", "kurti", "kurtas", "kurtis"],
    "kurti": ["kurti", "kurta", "kurtis"]
}

ROLE_CATEGORY_MAP = {
    "complete_outfit": {
        "categories": ["Clothing"],
        "subcategories": ["Sarees", "Designer sarees", "Lehengas", "Anarkali suits", "Salwar suits", "Sharara sets", "Palazzo sets", "Ethnic gowns", "Indo-western outfits", "Dresses", "Jumpsuits", "Co-ord sets", "Sherwanis", "Kurta pyjama sets", "Pathani suits", "Suits", "Ethnic sets"]
    },
    "top": {
        "categories": ["Clothing"],
        "subcategories": ["T-Shirts", "Shirts", "Tops", "Blouses", "Sweaters", "Hoodies", "Blazers", "Kurtis", "Nehru jackets", "Traditional waistcoats", "Casual shirts", "Formal shirts", "Polo T-shirts", "Jackets", "Basic T-shirts", "Sweatshirts", "Casual wear"]
    },
    "bottom": {
        "categories": ["Clothing"],
        "subcategories": ["Jeans", "Trousers", "Skirts", "Shorts", "Formal trousers", "Chinos"]
    },
    "footwear": {
        "categories": ["Footwear"],
        "subcategories": ["Sneakers", "Loafers", "Boots", "Sandals", "Formal shoes", "Heels", "Flats", "Ethnic footwear"]
    },
    "shoes": {
        "categories": ["Footwear"],
        "subcategories": ["Sneakers", "Loafers", "Boots", "Sandals", "Formal shoes", "Heels", "Flats", "Ethnic footwear"]
    },
    "accessory": {
        "categories": ["Accessories"],
        "subcategories": ["Watches", "Handbags", "Clutches", "Earrings", "Necklaces", "Bracelets", "Dupattas", "Scarves", "Belts", "Wallets", "Ties", "Pocket squares", "Sunglasses", "Caps", "Backpacks"]
    },
    "accessories": {
        "categories": ["Accessories"],
        "subcategories": ["Watches", "Handbags", "Clutches", "Earrings", "Necklaces", "Bracelets", "Dupattas", "Scarves", "Belts", "Wallets", "Ties", "Pocket squares", "Sunglasses", "Caps", "Backpacks"]
    }
}


class ProductSearchService:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Normalize and split search text into clean lowercase tokens."""
        if not text:
            return []
        cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return tokens

    @classmethod
    def calculate_relevance(cls, product: Product, tokens: List[str], raw_query: str) -> float:
        """
        Calculates flexible relevance score for a product given search tokens.
        Considers name, color, subcategory, category, material, fit, style, occasion, and description.
        """
        if not tokens:
            return 50.0

        p_name = product.name.lower()
        p_color = product.color.lower()
        p_subcat = product.subcategory.lower()
        p_cat = product.category.lower()
        p_material = (product.fabric or product.material or "").lower()
        p_fit = (product.fit or "").lower()
        p_style = (product.style_archetype or product.style or "").lower()
        p_occasion = (product.occasion or "").lower()
        p_desc = (product.description or "").lower()

        raw_lower = raw_query.lower()
        score = 0.0

        # Exact whole phrase in name
        if raw_lower in p_name:
            score += 50.0

        matched_tokens = 0

        for token in tokens:
            synonym_group = SYNONYMS.get(token, [token])
            token_matched = False

            # Check exact or synonym matches across fields
            for term in synonym_group:
                if term in p_color:
                    score += 25.0
                    token_matched = True
                if term in p_name:
                    score += 22.0
                    token_matched = True
                if term in p_subcat:
                    score += 20.0
                    token_matched = True
                if term in p_material:
                    score += 18.0
                    token_matched = True
                if term in p_fit:
                    score += 15.0
                    token_matched = True
                if term in p_style:
                    score += 12.0
                    token_matched = True
                if term in p_occasion:
                    score += 10.0
                    token_matched = True
                if term in p_cat:
                    score += 8.0
                    token_matched = True
                if term in p_desc:
                    score += 5.0
                    token_matched = True

            if token_matched:
                matched_tokens += 1

        # Fraction of user tokens satisfied
        token_coverage = matched_tokens / max(len(tokens), 1)
        score *= (0.5 + 0.5 * token_coverage)

        # Small boost for high ratings
        score += (product.rating or 4.0) * 2.0

        return score

    @classmethod
    def search_catalogue(
        cls,
        db: Session,
        query_text: Optional[str] = None,
        gender: Optional[str] = None,
        include_unisex: bool = False,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        color: Optional[str] = None,
        style: Optional[str] = None,
        occasion: Optional[str] = None,
        material: Optional[str] = None,
        fit: Optional[str] = None,
        size: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 50
    ) -> List[Product]:
        """
        Executes faceted filtering and token-based fuzzy matching.
        """
        q = db.query(Product).filter(Product.availability == True)

        # Gender filtering
        if isinstance(gender, str):
            g_clean = gender.strip().lower()
            if g_clean == "female":
                if include_unisex:
                    q = q.filter(Product.gender.in_(["Female", "Unisex"]))
                else:
                    q = q.filter(Product.gender == "Female")
            elif g_clean == "male":
                if include_unisex:
                    q = q.filter(Product.gender.in_(["Male", "Unisex"]))
                else:
                    q = q.filter(Product.gender == "Male")

        if isinstance(category, str) and category.lower() != "all":
            q = q.filter(Product.category.ilike(f"%{category}%"))
        if isinstance(subcategory, str) and subcategory.strip():
            q = q.filter(Product.subcategory.ilike(f"%{subcategory}%"))
        if isinstance(color, str) and color.strip():
            q = q.filter(Product.color.ilike(f"%{color}%"))
        if isinstance(style, str) and style.strip():
            q = q.filter((Product.style.ilike(f"%{style}%")) | (Product.style_archetype.ilike(f"%{style}%")))
        if isinstance(occasion, str) and occasion.strip():
            q = q.filter((Product.occasion.ilike(f"%{occasion}%")) | (Product.supported_occasions.ilike(f"%{occasion}%")))
        if isinstance(material, str) and material.strip():
            q = q.filter((Product.fabric.ilike(f"%{material}%")) | (Product.material.ilike(f"%{material}%")))
        if isinstance(fit, str) and fit.strip():
            q = q.filter(Product.fit.ilike(f"%{fit}%"))
        if isinstance(min_price, (int, float)):
            q = q.filter(Product.price >= min_price)
        if isinstance(max_price, (int, float)):
            q = q.filter(Product.price <= max_price)

        candidates = q.all()

        if not query_text or not query_text.strip():
            # Return sorted by rating
            candidates.sort(key=lambda p: (p.rating or 0.0), reverse=True)
            return candidates[:limit]

        tokens = cls.tokenize(query_text)
        scored_candidates = []

        for p in candidates:
            score = cls.calculate_relevance(p, tokens, query_text)
            if score > 15.0:
                scored_candidates.append((score, p))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_candidates][:limit]

    @classmethod
    def match_outfit_item(
        cls,
        db: Session,
        role: str,
        query_text: str,
        gender: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Matches a specific recommended outfit piece (e.g., 'Black oversized T-shirt')
        against the product catalogue within its appropriate role/category.
        """
        role_norm = role.lower().strip()
        category_spec = ROLE_CATEGORY_MAP.get(role_norm, {
            "categories": ["Clothing", "Footwear", "Accessories"],
            "subcategories": []
        })

        q = db.query(Product).filter(
            Product.availability == True,
            Product.category.in_(category_spec["categories"])
        )
        if category_spec["subcategories"]:
            q = q.filter(Product.subcategory.in_(category_spec["subcategories"]))

        if gender:
            g_clean = gender.strip().lower()
            if g_clean == "female":
                q = q.filter(Product.gender.in_(["Female", "Unisex"]))
            elif g_clean == "male":
                q = q.filter(Product.gender.in_(["Male", "Unisex"]))

        if max_price is not None:
            q = q.filter(Product.price <= max_price)

        candidates = q.all()
        tokens = cls.tokenize(query_text)

        scored = []
        for p in candidates:
            score = cls.calculate_relevance(p, tokens, query_text)
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            fallback = db.query(Product).filter(
                Product.availability == True,
                Product.category.in_(category_spec["categories"])
            ).first()
            return {
                "matched_product": fallback,
                "confidence_score": 50.0,
                "alternatives": []
            }

        best_product = scored[0][1]
        best_score = min(98.0, max(60.0, scored[0][0]))
        alternatives = [p for _, p in scored[1:4]]

        return {
            "matched_product": best_product,
            "confidence_score": round(best_score, 1),
            "alternatives": alternatives
        }
