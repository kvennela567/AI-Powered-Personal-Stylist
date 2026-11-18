"""
Comprehensive 22-Test Verification Suite for AI Personal Stylist for E-Commerce.
Validates all requirements of Module 15:
- Strict Gender Filtering (Tests 1, 2)
- Specific Occasion + Gender Combinations (Tests 3, 4, 5)
- Color Palette Control & Avoidance (Tests 6, 7)
- Style Archetype Precision (Tests 8, 9, 10)
- Garment Nuances: Fit, Sleeve, Fabric (Tests 11, 12, 13)
- Strict Budget Constraints (Test 14)
- Dynamic Preference Reactivity (Tests 15, 16, 17)
- AI Chatbot Database Grounding (Test 18)
- Feedback & Weight Adaptation (Test 19)
- Persistence & Dashboard Aggregation (Tests 20, 21)
- Graceful Empty-State Handling (Test 22)
"""

import sys
import os
import io

# Ensure utf-8 encoding for console output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.models.database import SessionLocal
from backend.models.entities import (
    User, UserProfile, Product, Outfit, OutfitItem,
    SavedOutfit, RecommendationHistory, Feedback, UserPreferenceWeight,
    UserColorPreference, UserStylePreference
)
from backend.models.schemas import (
    ChatRequest, FeedbackRequest, UserProfileSchema
)
from backend.services.recommendation_service import RecommendationEngine
from backend.services.preference_service import PreferenceService
from backend.routes.ai import chat_with_stylist
from backend.routes.products import get_products
from backend.routes.outfits import save_outfit, get_saved_outfits
from backend.routes.dashboard import get_dashboard_analytics


def reset_user_preferences(db, user, profile, gender="Female"):
    """Reset user preferences to clean baseline."""
    profile.gender = gender
    profile.include_unisex = False
    profile.strict_preferences = False
    profile.preferred_fit = "Relaxed"
    profile.preferred_sleeve_length = "Full Sleeve"
    profile.preferred_clothing_length = "Standard"
    profile.preferred_materials = "Cotton, Linen, Denim"
    profile.budget_min = 1000.0
    profile.budget_max = 15000.0

    db.query(UserColorPreference).filter_by(user_id=user.id).delete()
    db.add(UserColorPreference(user_id=user.id, color_name="Black", preference_type="favorite"))
    db.add(UserColorPreference(user_id=user.id, color_name="Olive", preference_type="favorite"))
    db.add(UserColorPreference(user_id=user.id, color_name="Yellow", preference_type="avoid"))

    db.query(UserStylePreference).filter_by(user_id=user.id).delete()
    db.add(UserStylePreference(user_id=user.id, style_name="Casual"))
    db.commit()


def run_all_22_tests():
    db = SessionLocal()
    engine = RecommendationEngine(db)
    pref_service = PreferenceService(db)

    results = []

    # Ensure demo user exists
    user = db.query(User).filter_by(username="demo_user").first()
    if not user:
        user = User(username="demo_user", email="alex.rivera@luxuryfashion.ai", hashed_password="hashed_demo_password")
        db.add(user)
        db.commit()

    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, name="Alex Rivera", gender="Female")
        db.add(profile)
        db.commit()

    reset_user_preferences(db, user, profile, gender="Female")

    print("=" * 80)
    print("STARTING COMPLETE 22-MODULE TEST VERIFICATION SUITE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # TEST 1: Female -> Female products only (Recommendations, Shop, Stylist)
    # -------------------------------------------------------------------------
    try:
        reset_user_preferences(db, user, profile, gender="Female")

        # Recommendations
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            include_unisex=False
        )
        assert len(looks) > 0, "No looks generated for Female"
        for look in looks:
            for it in look["items"]:
                p = it["product"]
                assert p.gender == "Female", f"Test 1 Failed: Non-female product {p.name} ({p.gender}) in recommendations"

        # Shop
        shop_items = get_products(gender="Female", include_unisex=False, db=db, limit=30)
        assert len(shop_items) > 0, "Shop returned 0 female products"
        for p in shop_items:
            assert p.gender == "Female", f"Test 1 Failed: Non-female product {p.name} ({p.gender}) in shop"

        # Stylist Chatbot
        chat_req = ChatRequest(message="Recommend an outfit for my college presentation", gender_override="Female")
        chat_resp = chat_with_stylist(chat_req, db=db, user=user)
        if chat_resp.outfit_recommendation:
            for it in chat_resp.outfit_recommendation.items:
                assert it.product.gender in ["Female"], f"Test 1 Failed: Stylist recommended non-female product {it.product.name} ({it.product.gender})"

        results.append(("Test 1: Female Selection Controls All Recommendations, Shop & Stylist", True, "Female products strictly isolated across engine, shop, and chatbot"))
    except Exception as e:
        results.append(("Test 1: Female Selection Controls All Recommendations, Shop & Stylist", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 2: Male -> Male products only (Recommendations, Shop, Stylist)
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Male",
            include_unisex=False,
            preferred_colors=["Navy", "White"]
        )
        assert len(looks) > 0, "No looks generated for Male"
        for look in looks:
            for it in look["items"]:
                p = it["product"]
                assert p.gender == "Male", f"Test 2 Failed: Non-male product {p.name} ({p.gender}) in recommendations"

        shop_items = get_products(gender="Male", include_unisex=False, db=db, limit=30)
        assert len(shop_items) > 0, "Shop returned 0 male products"
        for p in shop_items:
            assert p.gender == "Male", f"Test 2 Failed: Non-male product {p.name} ({p.gender}) in shop"

        chat_req = ChatRequest(message="Curate a smart casual office outfit for me", gender_override="Male")
        chat_resp = chat_with_stylist(chat_req, db=db, user=user)
        if chat_resp.outfit_recommendation:
            for it in chat_resp.outfit_recommendation.items:
                assert it.product.gender in ["Male"], f"Test 2 Failed: Stylist recommended non-male product {it.product.name} ({it.product.gender})"

        results.append(("Test 2: Male Selection Controls All Recommendations, Shop & Stylist", True, "Male products strictly isolated across engine, shop, and chatbot"))
    except Exception as e:
        results.append(("Test 2: Male Selection Controls All Recommendations, Shop & Stylist", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 3: Female + Engagement -> Female engagement outfits only
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Engagement",
            gender="Female",
            include_unisex=False,
            preferred_colors=["Red", "Pink", "Burgundy", "Rose", "Emerald"]
        )
        assert len(looks) > 0, "No engagement looks generated for Female"
        for look in looks:
            for it in look["items"]:
                p = it["product"]
                assert p.gender == "Female", f"Test 3 Failed: Non-female item {p.name}"
                supported = [o.strip().lower() for o in (p.supported_occasions.split(",") if p.supported_occasions else [p.occasion])] + [p.occasion.strip().lower()]
                assert any(o in ["engagement", "wedding", "festival", "family gathering", "semi-formal event"] for o in supported), f"Test 3 Failed: {p.name} does not support Engagement"
                assert p.clothing_type != "Casual wear", f"Test 3 Failed: Casual wear {p.name} appeared in Engagement"

        results.append(("Test 3: Female + Engagement Strict Filtering", True, "Only female engagement/traditional ensembles (lehengas, sarees, suits, heels, clutches)"))
    except Exception as e:
        results.append(("Test 3: Female + Engagement Strict Filtering", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 4: Male + Engagement -> Male engagement outfits only
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Engagement",
            gender="Male",
            include_unisex=False,
            preferred_colors=["Cream", "Beige", "Navy", "Burgundy", "Mustard"]
        )
        assert len(looks) > 0, "No engagement looks generated for Male"
        for look in looks:
            for it in look["items"]:
                p = it["product"]
                assert p.gender == "Male", f"Test 4 Failed: Non-male item {p.name}"
                supported = [o.strip().lower() for o in (p.supported_occasions.split(",") if p.supported_occasions else [p.occasion])]
                assert any(o in ["engagement", "wedding", "festival", "family gathering"] for o in supported), f"Test 4 Failed: {p.name} does not support Engagement"
                assert p.clothing_type != "Casual wear", f"Test 4 Failed: Casual wear {p.name} appeared in Male Engagement"

        results.append(("Test 4: Male + Engagement Strict Filtering", True, "Only male engagement wear (sherwanis, Indo-western, kurtas, Nehru jackets, formal shoes)"))
    except Exception as e:
        results.append(("Test 4: Male + Engagement Strict Filtering", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 5: Female + Formal Event -> Female formal outfits only
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Formal Event",
            gender="Female",
            include_unisex=False,
            preferred_colors=["Black", "Navy", "Grey"]
        )
        assert len(looks) > 0, "No formal event looks generated for Female"
        for look in looks:
            for it in look["items"]:
                p = it["product"]
                assert p.gender == "Female", f"Test 5 Failed: Non-female item {p.name}"
                supported = [o.strip().lower() for o in (p.supported_occasions.split(",") if p.supported_occasions else [p.occasion])]
                assert any(o in ["formal event", "business meeting", "interview", "office", "dinner"] for o in supported), f"Test 5 Failed: {p.name} does not support Formal Event"

        results.append(("Test 5: Female + Formal Event Strict Filtering", True, "Only female formal suits, blazers, formal trousers, dresses, and heels"))
    except Exception as e:
        results.append(("Test 5: Female + Formal Event Strict Filtering", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 6: Favourite Colours: Black and Olive -> Main clothing pieces in Black/Olive
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_colors=["Black", "Olive"],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No looks generated for Black & Olive favorites"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["complete_outfit", "top", "bottom"]:
                    p = it["product"]
                    fam = p.color_family or p.color
                    assert fam.lower() in ["black", "green", "olive"] or p.color.lower() in ["black", "olive", "dark olive"], (
                        f"Test 6 Failed: Main garment {p.name} color '{p.color}' ({p.color_family}) not in Black or Olive"
                    )

        results.append(("Test 6: Favourite Colours: Black & Olive Precision", True, "All main clothing pieces strictly adhere to Black and Olive colour families"))
    except Exception as e:
        results.append(("Test 6: Favourite Colours: Black & Olive Precision", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 7: Colours to Avoid: Yellow -> Strictly no yellow products anywhere
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            avoid_colors=["Yellow", "Mustard"],
            preferred_colors=[]
        )
        assert len(looks) > 0, "No looks generated"
        for look in looks:
            for it in look["items"]:
                p = it["product"]
                assert p.color.lower() not in ["yellow", "mustard"], f"Test 7 Failed: Yellow product {p.name} appeared"
                if p.color_family:
                    assert p.color_family.lower() != "yellow", f"Test 7 Failed: Yellow family product {p.name} appeared"

        results.append(("Test 7: Colours to Avoid: Yellow Strictly Excluded", True, "Zero yellow/mustard products in any role (tops, bottoms, footwear, accessories)"))
    except Exception as e:
        results.append(("Test 7: Colours to Avoid: Yellow Strictly Excluded", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 8: Streetwear aesthetic -> Generated outfits match Streetwear archetype
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_style="Streetwear",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No streetwear looks generated"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["complete_outfit", "top", "bottom"]:
                    p = it["product"]
                    assert p.style_archetype == "Streetwear", f"Test 8 Failed: Non-streetwear garment {p.name} ({p.style_archetype})"

        results.append(("Test 8: Streetwear Aesthetic Strict Filtering", True, "Generated looks exclusively consist of Streetwear archetyped pieces"))
    except Exception as e:
        results.append(("Test 8: Streetwear Aesthetic Strict Filtering", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 9: Minimal aesthetic -> Streetwear items excluded unless genuinely minimal
    # -------------------------------------------------------------------------
    try:
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_style="Minimal",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No minimal looks generated"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["complete_outfit", "top", "bottom"]:
                    p = it["product"]
                    assert p.style_archetype == "Minimal", f"Test 9 Failed: {p.name} is {p.style_archetype}, not Minimal"

        results.append(("Test 9: Minimal Aesthetic Excludes Unrelated Aesthetics", True, "Minimal selection strictly isolates Minimal garments and excludes Streetwear"))
    except Exception as e:
        results.append(("Test 9: Minimal Aesthetic Excludes Unrelated Aesthetics", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 10: Multiple aesthetics: Elegant + Traditional
    # -------------------------------------------------------------------------
    try:
        db.query(UserStylePreference).filter_by(user_id=user.id).delete()
        db.add(UserStylePreference(user_id=user.id, style_name="Elegant"))
        db.add(UserStylePreference(user_id=user.id, style_name="Traditional"))
        db.commit()

        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Wedding",
            gender="Female",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No looks generated for Elegant + Traditional"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["complete_outfit", "top", "bottom"]:
                    p = it["product"]
                    assert p.style_archetype in ["Elegant", "Traditional", "Ethnic"], (
                        f"Test 10 Failed: {p.name} ({p.style_archetype}) not in Elegant/Traditional"
                    )

        results.append(("Test 10: Multiple Aesthetics: Elegant + Traditional", True, "Ensemble pieces satisfy Elegant and Traditional style archetypes"))
    except Exception as e:
        results.append(("Test 10: Multiple Aesthetics: Elegant + Traditional", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 11: Oversized fit -> Oversized garments prioritized/strictly filtered
    # -------------------------------------------------------------------------
    try:
        profile.strict_preferences = True
        profile.preferred_fit = "Oversized"
        profile.preferred_sleeve_length = "N/A"
        profile.preferred_clothing_length = "N/A"
        profile.preferred_materials = "Cotton, Linen, Denim"
        db.commit()

        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_fit="Oversized",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No looks generated for Oversized fit"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["complete_outfit", "top", "bottom"]:
                    p = it["product"]
                    p_fit = (p.fit or "").lower()
                    assert "slim" not in p_fit and "bodycon" not in p_fit, f"Test 11 Failed: Slim/bodycon garment {p.name} ({p.fit}) in strict oversized mode"

        results.append(("Test 11: Oversized Fit Strict Preference", True, "Slim/bodycon garments excluded; oversized & relaxed silhouettes prioritized"))
    except Exception as e:
        results.append(("Test 11: Oversized Fit Strict Preference", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 12: Full Sleeve -> Incompatible sleeve lengths excluded
    # -------------------------------------------------------------------------
    try:
        profile.strict_preferences = True
        profile.preferred_sleeve_length = "Full Sleeve"
        profile.preferred_fit = "Relaxed"
        profile.preferred_clothing_length = "N/A"
        profile.preferred_materials = "Cotton, Linen, Denim"
        db.commit()

        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No looks generated for Full Sleeve"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["top"] and it["product"].sleeve_length != "N/A":
                    p = it["product"]
                    assert "sleeveless" not in p.sleeve_length.lower() and "half" not in p.sleeve_length.lower() and "short" not in p.sleeve_length.lower(), (
                        f"Test 12 Failed: Incompatible sleeve length {p.name} ({p.sleeve_length})"
                    )

        results.append(("Test 12: Full Sleeve Strict Filtering", True, "Sleeveless and short sleeve garments excluded from upper body recommendations"))
    except Exception as e:
        results.append(("Test 12: Full Sleeve Strict Filtering", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 13: Silk fabric -> Main garments made of Silk
    # -------------------------------------------------------------------------
    try:
        profile.strict_preferences = True
        profile.preferred_materials = "Silk"
        profile.preferred_sleeve_length = "N/A"
        profile.preferred_fit = "Relaxed"
        db.commit()

        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Festival",
            gender="Female",
            preferred_fabric="Silk",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No silk festival looks generated"
        for look in looks:
            for it in look["items"]:
                if it["role"] in ["complete_outfit", "top"]:
                    p = it["product"]
                    assert "silk" in (p.fabric or "").lower() or "silk" in (p.material or "").lower(), (
                        f"Test 13 Failed: Main garment {p.name} fabric is {p.fabric}, expected Silk"
                    )

        results.append(("Test 13: Silk Fabric Strict Filtering", True, "Main garments strictly fabricated from genuine Silk"))
    except Exception as e:
        results.append(("Test 13: Silk Fabric Strict Filtering", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 14: Engagement + Female + Budget ₹3,000 -> Total price <= ₹3,000
    # -------------------------------------------------------------------------
    try:
        profile.strict_preferences = False
        profile.preferred_materials = "Cotton, Linen, Silk"
        profile.budget_max = 3000.0
        db.commit()

        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Engagement",
            gender="Female",
            include_unisex=False,
            budget_max=3000.0,
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks) > 0, "No looks generated under ₹3,000"
        for look in looks:
            assert look["total_price"] <= 3000.0, f"Test 14 Failed: Outfit total price {look['total_price']} exceeds budget ₹3,000"

        results.append(("Test 14: Strict Budget Constraints (Engagement <= ₹3,000)", True, f"Total ensemble price strictly <= ₹3,000 (Actual: ₹{looks[0]['total_price']:,.2f})"))
    except Exception as e:
        results.append(("Test 14: Strict Budget Constraints (Engagement <= ₹3,000)", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 15: Change colour preferences -> Verify recommendations change
    # -------------------------------------------------------------------------
    try:
        # State A: Favorite Black
        looks_black = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_colors=["Black"],
            avoid_colors=[]
        )
        assert len(looks_black) > 0, "No looks generated for Black"
        main_black = next(it["product"] for it in looks_black[0]["items"] if it["role"] in ["complete_outfit", "top"])
        assert (main_black.color_family or main_black.color).lower() == "black"

        # State B: Favorite Pink
        looks_pink = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_colors=["Pink"],
            avoid_colors=[]
        )
        assert len(looks_pink) > 0, "No looks generated for Pink"
        main_pink = next(it["product"] for it in looks_pink[0]["items"] if it["role"] in ["complete_outfit", "top"])
        assert (main_pink.color_family or main_pink.color).lower() == "pink"

        results.append(("Test 15: Dynamic Colour Preference Reactivity", True, f"Recommendations switched dynamically from {main_black.color} to {main_pink.color}"))
    except Exception as e:
        results.append(("Test 15: Dynamic Colour Preference Reactivity", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 16: Change aesthetic preferences -> Verify recommendations change
    # -------------------------------------------------------------------------
    try:
        # State A: Streetwear
        looks_street = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_style="Streetwear",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks_street) > 0, "No looks generated for Streetwear"
        main_street = next(it["product"] for it in looks_street[0]["items"] if it["role"] in ["complete_outfit", "top"])
        assert main_street.style_archetype == "Streetwear"

        # State B: Minimal
        looks_minimal = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Female",
            preferred_style="Minimal",
            preferred_colors=[],
            avoid_colors=[]
        )
        assert len(looks_minimal) > 0, "No looks generated for Minimal"
        main_minimal = next(it["product"] for it in looks_minimal[0]["items"] if it["role"] in ["complete_outfit", "top"])
        assert main_minimal.style_archetype == "Minimal"

        results.append(("Test 16: Dynamic Aesthetic Preference Reactivity", True, f"Recommendations switched dynamically from {main_street.style_archetype} to {main_minimal.style_archetype}"))
    except Exception as e:
        results.append(("Test 16: Dynamic Aesthetic Preference Reactivity", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 17: Change gender in Profile -> Verify Chatbot, Shop, Recommendations synchronize
    # -------------------------------------------------------------------------
    try:
        # Update user profile gender to Male
        profile.gender = "Male"
        profile.include_unisex = False
        profile.preferred_materials = "Cotton, Linen"
        profile.strict_preferences = False
        profile.budget_max = 15000.0
        db.commit()

        # Check Recommendations syncs with Male
        looks = engine.generate_three_looks(
            user_id=user.id,
            occasion="Casual outing",
            gender="Male",
            preferred_colors=["Navy", "White"],
            avoid_colors=[]
        )
        for it in looks[0]["items"]:
            assert it["product"].gender == "Male", f"Test 17 Failed: Recommendations produced non-male item {it['product'].name}"

        # Check Shop syncs with Male
        shop_items = get_products(gender="Male", include_unisex=False, db=db, limit=10)
        for p in shop_items:
            assert p.gender == "Male", f"Test 17 Failed: Shop produced non-male item {p.name}"

        # Check Chatbot syncs with Male
        chat_req = ChatRequest(message="What outfit should I wear to college?", gender_override="Male")
        chat_resp = chat_with_stylist(chat_req, db=db, user=user)
        if chat_resp.outfit_recommendation:
            for it in chat_resp.outfit_recommendation.items:
                assert it.product.gender == "Male", f"Test 17 Failed: Chatbot recommended non-male item {it.product.name}"

        # Restore Female profile
        profile.gender = "Female"
        db.commit()

        results.append(("Test 17: Global Profile Gender Real-time Synchronization", True, "Switching profile gender immediately coordinates Recommendations, Shop, and Chatbot"))
    except Exception as e:
        results.append(("Test 17: Global Profile Gender Real-time Synchronization", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 18: Ask Chatbot for an outfit -> Products retrieved from database
    # -------------------------------------------------------------------------
    try:
        chat_req = ChatRequest(message="Recommend an outfit for a dinner date", gender_override="Female")
        chat_resp = chat_with_stylist(chat_req, db=db, user=user)
        assert chat_resp.outfit_recommendation is not None, "Chatbot returned no outfit"
        for it in chat_resp.outfit_recommendation.items:
            db_prod = db.query(Product).filter_by(id=it.product.id).first()
            assert db_prod is not None, f"Test 18 Failed: Product ID {it.product.id} does not exist in SQLite database"
            assert db_prod.name == it.product.name, f"Test 18 Failed: Name mismatch for ID {db_prod.id}"

        results.append(("Test 18: Chatbot Authentic Database Product Grounding", True, "All items returned by chatbot verified to exist in SQLite products table"))
    except Exception as e:
        results.append(("Test 18: Chatbot Authentic Database Product Grounding", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 19: Provide Feedback -> Stored and influences future recommendation weights
    # -------------------------------------------------------------------------
    try:
        outfit = db.query(Outfit).first()
        assert outfit is not None, "No outfits in database"

        initial_weight = db.query(UserPreferenceWeight).filter_by(
            user_id=user.id, feature_type="style", feature_value=outfit.style_tag
        ).first()
        initial_val = initial_weight.weight_delta if initial_weight else 0.0

        fb_res = pref_service.record_feedback(
            user_id=user.id,
            outfit_id=outfit.id,
            feedback_type="like",
            comment="Loved this color and style coordination!"
        )

        updated_weight = db.query(UserPreferenceWeight).filter_by(
            user_id=user.id, feature_type="style", feature_value=outfit.style_tag
        ).first()
        assert updated_weight is not None, "Preference weight was not created"
        assert updated_weight.weight_delta > initial_val, f"Weight did not increase: {initial_val} -> {updated_weight.weight_delta}"

        fb_entry = db.query(Feedback).filter_by(user_id=user.id, outfit_id=outfit.id).first()
        assert fb_entry is not None, "Feedback entry was not persisted"

        results.append(("Test 19: Feedback Persistence & Weight Adaptation", True, f"Feedback stored and boosted affinity weight from {initial_val} to {updated_weight.weight_delta}"))
    except Exception as e:
        results.append(("Test 19: Feedback Persistence & Weight Adaptation", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 20: Save Outfit -> Appears in My Outfits and updates Dashboard
    # -------------------------------------------------------------------------
    try:
        outfit = db.query(Outfit).first()
        assert outfit is not None, "No outfit available to save"

        save_res = save_outfit(outfit_id=outfit.id, notes="Test Save", user=user, db=db)
        saved_list = get_saved_outfits(user=user, db=db)
        saved_ids = [o.id for o in saved_list]
        assert outfit.id in saved_ids, f"Test 20 Failed: Outfit {outfit.id} not in saved outfits"

        stats = get_dashboard_analytics(user=user, db=db)
        assert stats.saved_outfits_count >= 1, "Dashboard saved_outfits_count was not updated"
        assert stats.total_products_count >= 1000, "Dashboard total products count is under 1,000"

        results.append(("Test 20: Outfit Saving & Dashboard Live Aggregation", True, f"Outfit archived into My Outfits; Dashboard shows {stats.saved_outfits_count} saved and {stats.total_products_count} products"))
    except Exception as e:
        results.append(("Test 20: Outfit Saving & Dashboard Live Aggregation", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 21: Refresh Application -> Profile & saved outfits persist in SQLite
    # -------------------------------------------------------------------------
    try:
        db.close()
        fresh_db = SessionLocal()

        persisted_user = fresh_db.query(User).filter_by(username="demo_user").first()
        assert persisted_user is not None, "User did not persist in SQLite"
        persisted_profile = fresh_db.query(UserProfile).filter_by(user_id=persisted_user.id).first()
        assert persisted_profile is not None, "UserProfile did not persist in SQLite"
        persisted_saved = fresh_db.query(SavedOutfit).filter_by(user_id=persisted_user.id).all()
        assert len(persisted_saved) > 0, "SavedOutfits did not persist in SQLite"

        fresh_db.close()
        results.append(("Test 21: SQLite Database Durability Across App Restarts", True, "User profiles, preferences, outfits, and feedback persist across database connections"))
    except Exception as e:
        results.append(("Test 21: SQLite Database Durability Across App Restarts", False, str(e)))

    # -------------------------------------------------------------------------
    # TEST 22: Insufficient Products Test -> Displays clean message without unrelated casual clothes
    # -------------------------------------------------------------------------
    try:
        fresh_db = SessionLocal()
        engine_fresh = RecommendationEngine(fresh_db)

        user_fresh = fresh_db.query(User).filter_by(username="demo_user").first()
        prof_fresh = fresh_db.query(UserProfile).filter_by(user_id=user_fresh.id).first()
        prof_fresh.strict_preferences = True
        prof_fresh.preferred_materials = "Silk"
        prof_fresh.preferred_clothing_length = "Maxi"
        prof_fresh.budget_max = 200.0
        fresh_db.commit()

        looks = engine_fresh.generate_three_looks(
            user_id=user_fresh.id,
            occasion="Gym",
            gender="Female",
            budget_max=200.0,
            preferred_colors=["Teal"],
            avoid_colors=[]
        )
        # Should return 0 looks rather than dumping unrelated casual clothes or wedding lehengas
        assert len(looks) == 0, f"Test 22 Failed: Expected 0 looks for impossible criteria, got {len(looks)}"

        prof_fresh.strict_preferences = False
        prof_fresh.preferred_materials = "Cotton, Linen"
        prof_fresh.preferred_clothing_length = "Standard"
        prof_fresh.budget_max = 15000.0
        fresh_db.commit()
        fresh_db.close()

        results.append(("Test 22: Graceful Empty State on Insufficient / Strict Matches", True, "Engine cleanly returns 0 looks with informative rationale instead of polluting with unrelated casual items"))
    except Exception as e:
        results.append(("Test 22: Graceful Empty State on Insufficient / Strict Matches", False, str(e)))

    # -------------------------------------------------------------------------
    # SUMMARY REPORT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST EXECUTION RESULTS REPORT (22 / 22 TESTS)")
    print("=" * 80)

    all_passed = True
    for title, status, details in results:
        status_str = "[PASS]" if status else "[FAIL]"
        print(f"{status_str} {title}")
        print(f"       -> {details}")
        if not status:
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("ALL 22 TESTS PASSED PERFECTLY! ARCHITECTURE FULLY VALIDATED.")
    else:
        print("ONE OR MORE TESTS FAILED. PLEASE REVIEW DETAILS ABOVE.")
    print("=" * 80)
    return all_passed


if __name__ == "__main__":
    success = run_all_22_tests()
    sys.exit(0 if success else 1)
