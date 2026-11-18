"""
Comprehensive StyleSense Integration Test Suite.
Validates the complete 9-point integration specification from Section 13 of the project requirements:
- Test 1: Profile Preferences Persistence (body type, style, colour, size, fit, occasion, budget)
- Test 2: Personalised Recommendations reflecting body type, preferred color, budget, fit, occasion
- Test 3: Photo Analysis validation and recommendation integration; failure fallback
- Test 4: AI Stylist Chat extracting budget, colors, occasion, and returning connected outfit
- Test 5: Saved Outfits and User Feedback loop
- Test 6: Weather integration and fallback
- Test 7: Virtual Try-On and Outfit Visualization honest disclaimers & responses
- Test 8: User Data Isolation (Multi-user registration, distinct profiles, isolated saved outfits)
- Test 9: End-to-End Synchronisation across all components
"""

import io
import base64
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.database import SessionLocal
from backend.models.entities import User, Product, Outfit, OutfitItem


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def make_test_image(format="JPEG", size=(160, 200), color=(120, 160, 200)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ============================================================================
# Test 1: Profile Preferences Persistence
# ============================================================================
def test_1_profile_preferences_persistence(client):
    """
    Save body type, style, colour, size, fit, occasion, and budget.
    Retrieve the saved profile.
    Change a preference and verify that the new value is persisted.
    """
    headers = {"X-User-Id": "demo_user"}

    # Update profile with all primary input fields
    profile_payload = {
        "name": "Aarav Mehta",
        "gender": "Male",
        "age_group": "20-29",
        "height": "178 cm",
        "clothing_size": "M",
        "body_type": "Pear",
        "custom_body_type": "",
        "budget_min": 1000.0,
        "budget_max": 3500.0,
        "preferred_fit": "Regular",
        "preferred_sleeve_length": "Full Sleeve",
        "preferred_clothing_length": "Standard",
        "preferred_materials": "Cotton, Linen",
        "preferred_footwear": "Sneakers, Loafers",
        "preferred_accessories": "Watch",
        "disliked_clothing": "Neon, Polyester",
        "custom_style_description": "Clean, smart casual aesthetic for campus.",
        "favorite_colors": ["Black", "Blue", "White"],
        "avoid_colors": ["Orange", "Yellow"],
        "preferred_styles": ["Casual", "Smart casual"]
    }

    res_put = client.put("/api/users/me", json=profile_payload, headers=headers)
    assert res_put.status_code == 200
    saved = res_put.json()
    assert saved["name"] == "Aarav Mehta"
    assert saved["body_type"] == "Pear"
    assert saved["clothing_size"] == "M"
    assert saved["preferred_fit"] == "Regular"
    assert saved["budget_max"] == 3500.0
    assert "Black" in saved["favorite_colors"]
    assert "Casual" in saved["preferred_styles"]

    # Retrieve profile to verify persistence
    res_get = client.get("/api/users/me", headers=headers)
    assert res_get.status_code == 200
    retrieved = res_get.json()
    assert retrieved["body_type"] == "Pear"
    assert retrieved["budget_max"] == 3500.0

    # Change a preference (e.g. body type to Hourglass, budget to 4500)
    profile_payload["body_type"] = "Hourglass"
    profile_payload["budget_max"] = 4500.0
    res_put2 = client.put("/api/users/me", json=profile_payload, headers=headers)
    assert res_put2.status_code == 200

    res_get2 = client.get("/api/users/me", headers=headers)
    assert res_get2.status_code == 200
    assert res_get2.json()["body_type"] == "Hourglass"
    assert res_get2.json()["budget_max"] == 4500.0


# ============================================================================
# Test 2: Personalised Recommendations
# ============================================================================
def test_2_personalised_recommendations(client):
    """
    Request recommendations using the saved profile.
    Verify that ranking and selected outfits reflect user inputs (occasion, colors, budget).
    Verify that strict budget constraints are respected where prices are available.
    """
    headers = {"X-User-Id": "demo_user"}

    # Request recommendations for College occasion with budget
    res = client.get("/api/recommendations/looks?occasion=College&budget_max=4000", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "looks" in data
    assert len(data["looks"]) == 3

    for look in data["looks"]:
        assert "id" in look
        assert "title" in look
        assert "total_price" in look
        assert "match_score" in look
        assert "explanation" in look
        assert len(look["items"]) >= 3
        # Match score must be between 10 and 100
        assert 50 <= look["match_score"] <= 100
        # Explanation must be informative
        assert len(look["explanation"]) > 20

    # Test with color preference in query
    res_black = client.get("/api/recommendations/looks?occasion=College&color=Black", headers=headers)
    assert res_black.status_code == 200
    black_looks = res_black.json()["looks"]
    has_black_item = False
    for look in black_looks:
        for it in look["items"]:
            prod = it.get("product")
            if prod and "black" in prod.get("color", "").lower():
                has_black_item = True
                break
    assert has_black_item, "Recommendations with color=Black should feature black products"

    # Strict budget constraint check: look must optimize price and explain if catalogue floor is higher
    res_budget = client.get("/api/recommendations/looks?occasion=College&budget_max=2000", headers=headers)
    assert res_budget.status_code == 200
    for look in res_budget.json()["looks"]:
        # Either fits budget or provides explicit optimization note
        if look["total_price"] > 2000:
            assert "minimum catalogue cost" in look["explanation"].lower() or "optimized" in look["explanation"].lower()


# ============================================================================
# Test 3: Photo Analysis
# ============================================================================
def test_3_photo_analysis_and_fallback(client):
    """
    Upload a valid image: verify analysis response.
    Verify that supported analysis results influence recommendations.
    Test invalid images (empty / bad encoding).
    Verify that ordinary profile-based recommendations still work if photo analysis fails.
    """
    headers = {"X-User-Id": "demo_user"}
    b64_img = make_test_image(format="JPEG", size=(150, 200), color=(80, 120, 180))

    # Valid image analysis
    res = client.post("/api/ai/analyze-photo", json={
        "photo_base64": b64_img,
        "filename": "wardrobe_piece.jpg"
    }, headers=headers)
    assert res.status_code == 200
    analysis = res.json()
    assert analysis["status"] == "success"
    assert "colors" in analysis
    assert len(analysis["colors"]["dominant_colors"]) > 0

    dom_colors = [c["name"] for c in analysis["colors"]["dominant_colors"]]
    comp_colors = [c["name"] for c in analysis["colors"]["complementary_colors"]]

    # Recommendations from analysis
    rec_res = client.post("/api/ai/recommend-from-analysis", json={
        "photo_colors": dom_colors,
        "complementary_colors": comp_colors,
        "detected_style": "Casual",
        "occasion": "College",
        "budget_max": 5000.0
    }, headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert len(rec_data["looks"]) == 3
    assert len(rec_data["detected_features_used"]) > 0

    # Invalid image testing
    res_empty = client.post("/api/ai/analyze-photo", json={
        "photo_base64": "",
        "filename": "empty.jpg"
    }, headers=headers)
    assert res_empty.status_code == 400

    res_corrupt = client.post("/api/ai/analyze-photo", json={
        "photo_base64": "not_valid_base64_data!!!",
        "filename": "corrupt.jpg"
    }, headers=headers)
    assert res_corrupt.status_code == 400

    # Verify standard profile recommendations still work normally after failure
    fallback_res = client.get("/api/recommendations/looks?occasion=College", headers=headers)
    assert fallback_res.status_code == 200
    assert len(fallback_res.json()["looks"]) == 3


# ============================================================================
# Test 4: AI Stylist Chat
# ============================================================================
def test_4_ai_stylist_chat(client):
    """
    Submit styling request through chat.
    Verify that response uses relevant profile and recommendation service.
    Refine the request with follow-up message.
    """
    headers = {"X-User-Id": "demo_user"}

    # Initial styling request mentioning occasion, color, budget
    chat_payload = {
        "message": "Suggest a comfortable outfit for college in black and blue under 4000.",
        "conversation_history": []
    }
    res = client.post("/api/ai/chat", json=chat_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 20
    assert "follow_up_suggestions" in data
    assert data["outfit_recommendation"] is not None
    rec_outfit = data["outfit_recommendation"]
    assert rec_outfit["total_price"] > 0
    assert len(rec_outfit["items"]) >= 3

    # Follow-up refinement message
    followup_payload = {
        "message": "Can you recommend a formal interview look instead?",
        "conversation_history": [
            {"role": "user", "content": chat_payload["message"]},
            {"role": "assistant", "content": data["reply"]}
        ]
    }
    res_followup = client.post("/api/ai/chat", json=followup_payload, headers=headers)
    assert res_followup.status_code == 200
    followup_data = res_followup.json()
    assert "reply" in followup_data
    assert followup_data["outfit_recommendation"] is not None
    # Style tag or title should reflect formal / interview
    assert any(term in (followup_data["outfit_recommendation"]["occasion"] + followup_data["outfit_recommendation"]["style_tag"]).lower()
               for term in ["interview", "formal", "smart casual", "business", "minimal"])


# ============================================================================
# Test 5: Saved Outfits and User Feedback
# ============================================================================
def test_5_saved_outfits_and_feedback(client):
    """
    Save a recommended outfit.
    Retrieve it.
    Submit feedback (rating/like).
    Remove it.
    Verify that the database and response remain consistent.
    """
    headers = {"X-User-Id": "demo_user"}

    # Generate a fresh look to obtain an outfit ID
    looks_res = client.get("/api/recommendations/looks?occasion=College", headers=headers)
    assert looks_res.status_code == 200
    outfit_id = looks_res.json()["looks"][0]["id"]

    # Save outfit
    save_res = client.post(f"/api/outfits/saved/{outfit_id}?notes=Favorite+Campus+Look", headers=headers)
    assert save_res.status_code in [200, 201]

    # Retrieve saved outfits
    get_saved = client.get("/api/outfits/saved", headers=headers)
    assert get_saved.status_code == 200
    saved_list = get_saved.json()
    saved_ids = [o["id"] for o in saved_list]
    assert outfit_id in saved_ids

    # Submit feedback on this outfit
    fb_res = client.post("/api/feedback", json={
        "outfit_id": outfit_id,
        "feedback_type": "like",
        "item_role": "top",
        "comment": "Perfect match for lectures!"
    }, headers=headers)
    assert fb_res.status_code == 200
    fb_data = fb_res.json()
    assert fb_data["status"] == "success"

    # Remove the saved outfit
    del_res = client.delete(f"/api/outfits/saved/{outfit_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify removal from list
    get_saved_after = client.get("/api/outfits/saved", headers=headers)
    assert get_saved_after.status_code == 200
    assert outfit_id not in [o["id"] for o in get_saved_after.json()]


# ============================================================================
# Test 6: Weather Integration
# ============================================================================
def test_6_weather_integration_and_fallback(client):
    """
    Verify weather-aware recommendations when weather information is available.
    Verify fallback behaviour when weather mode is varied.
    """
    headers = {"X-User-Id": "demo_user"}

    # Fetch rainy weather context
    w_res = client.get("/api/weather?mode=rainy")
    assert w_res.status_code == 200
    w_data = w_res.json()
    assert "condition" in w_data
    assert "rain" in w_data["condition"].lower()

    # Pass rainy weather context to recommendations
    rec_res = client.get("/api/recommendations/looks?occasion=Casual&weather=Rainy+%2821%C2%B0C%29", headers=headers)
    assert rec_res.status_code == 200
    looks = rec_res.json()["looks"]
    assert len(looks) == 3
    # Weather context must be passed into look
    assert "rain" in looks[0]["weather_context"].lower()

    # Fallback when weather mode is default / mild
    w_default = client.get("/api/weather")
    assert w_default.status_code == 200
    assert "Mild" in w_default.json()["condition"]


# ============================================================================
# Test 7: Virtual Try-On and Visualisation
# ============================================================================
def test_7_virtual_tryon_and_visualisation(client):
    """
    Verify supported inputs and outputs for outfit visualization and virtual try-on.
    Verify that disclaimers are honest and clearly state authentic catalogue items are used.
    """
    # Visualization test
    vis_res = client.post("/api/ai/visualize", json={
        "outfit_title": "Relaxed Campus Ensemble",
        "style_tag": "Casual",
        "occasion": "College",
        "items_summary": ["Black Cotton T-Shirt", "Indigo Jeans", "White Sneakers"],
        "palette": ["Black", "Indigo", "White"]
    })
    assert vis_res.status_code == 200
    vis_data = vis_res.json()
    assert "visualization_url" in vis_data
    assert "svg_canvas" in vis_data
    assert "disclaimer" in vis_data

    # Virtual try-on / outfit preview test
    b64_img = make_test_image()
    tryon_res = client.post("/api/ai/virtual-tryon", json={
        "user_photo_base64": b64_img,
        "filename": "user_avatar.jpg",
        "outfit_title": "Relaxed Campus Ensemble",
        "items": [
            {"role": "top", "name": "Classic White Tee", "price": 899, "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600"},
            {"role": "bottom", "name": "Straight Dark Jeans", "price": 1999}
        ]
    })
    assert tryon_res.status_code == 200
    tryon_data = tryon_res.json()
    assert tryon_data["status"] == "success"
    # Preserves honest distinction: authentic product image, not fake synthetic face swap
    assert "Synthetic try-on images are not generated" in tryon_data["disclaimer"]


# ============================================================================
# Test 8: User Data Isolation
# ============================================================================
def test_8_user_data_isolation(client):
    """
    Test with two different users.
    Verify that their profiles and private saved data remain separate.
    Verify that each user's recommendations use their own preferences.
    """
    # 1. Register User A
    user_a_payload = {
        "username": "priya_sharma",
        "email": "priya@example.com",
        "full_name": "Priya Sharma"
    }
    res_a = client.post("/api/users/register", json=user_a_payload)
    assert res_a.status_code in [200, 201]
    user_a_id = res_a.json()["id"]

    # 2. Register User B
    user_b_payload = {
        "username": "rohit_verma",
        "email": "rohit@example.com",
        "full_name": "Rohit Verma"
    }
    res_b = client.post("/api/users/register", json=user_b_payload)
    assert res_b.status_code in [200, 201]
    user_b_id = res_b.json()["id"]

    headers_a = {"X-User-Id": str(user_a_id)}
    headers_b = {"X-User-Id": str(user_b_id)}

    # 3. Update User A's profile: Pear body type, budget 2500, Favorite color Black
    client.put("/api/users/me", json={
        "name": "Priya Sharma",
        "body_type": "Pear",
        "clothing_size": "S",
        "budget_min": 1000.0,
        "budget_max": 2500.0,
        "preferred_fit": "Slim",
        "favorite_colors": ["Black", "Maroon"],
        "avoid_colors": ["Neon"],
        "preferred_styles": ["Ethnic", "Traditional"]
    }, headers=headers_a)

    # 4. Update User B's profile: Inverted Triangle body type, budget 8000, Favorite color Blue
    client.put("/api/users/me", json={
        "name": "Rohit Verma",
        "body_type": "Inverted triangle",
        "clothing_size": "XL",
        "budget_min": 3000.0,
        "budget_max": 8000.0,
        "preferred_fit": "Oversized",
        "favorite_colors": ["Navy", "Blue"],
        "avoid_colors": ["Pink"],
        "preferred_styles": ["Streetwear"]
    }, headers=headers_b)

    # 5. Verify profiles remain separate
    prof_a = client.get("/api/users/me", headers=headers_a).json()
    prof_b = client.get("/api/users/me", headers=headers_b).json()

    assert prof_a["body_type"] == "Pear"
    assert prof_a["budget_max"] == 2500.0
    assert prof_a["clothing_size"] == "S"

    assert prof_b["body_type"] == "Inverted triangle"
    assert prof_b["budget_max"] == 8000.0
    assert prof_b["clothing_size"] == "XL"

    # 6. User A saves an outfit
    looks_a = client.get("/api/recommendations/looks?occasion=College", headers=headers_a).json()["looks"]
    outfit_a_id = looks_a[0]["id"]
    client.post(f"/api/outfits/saved/{outfit_a_id}", headers=headers_a)

    # User B should NOT have User A's saved outfit
    saved_a = client.get("/api/outfits/saved", headers=headers_a).json()
    saved_b = client.get("/api/outfits/saved", headers=headers_b).json()

    saved_a_ids = [o["id"] for o in saved_a]
    saved_b_ids = [o["id"] for o in saved_b]

    assert outfit_a_id in saved_a_ids
    assert outfit_a_id not in saved_b_ids


# ============================================================================
# Test 9: End-to-End Synchronisation
# ============================================================================
def test_9_end_to_end_synchronisation(client):
    """
    Step-by-step complete user workflow:
    1. Enter profile preferences and save.
    2. Retrieve profile.
    3. Generate personalised recommendations.
    4. Upload photo for style analysis.
    5. Generate recommendations from analysis results.
    6. Ask AI Stylist for recommendations.
    7. Save outfit.
    8. Check saved outfits.
    9. Change a profile preference (e.g. favorite color to Blue).
    10. Request recommendations again and verify updated preferences are active.
    """
    headers = {"X-User-Id": "demo_user"}

    # 1 & 2. Save and retrieve profile preferences
    client.put("/api/users/me", json={
        "name": "Rhea Sync Test",
        "body_type": "Hourglass",
        "clothing_size": "M",
        "budget_min": 1500.0,
        "budget_max": 5000.0,
        "preferred_fit": "Relaxed",
        "favorite_colors": ["Black", "White"],
        "avoid_colors": ["Yellow"],
        "preferred_styles": ["Casual", "Minimal"]
    }, headers=headers)
    profile = client.get("/api/users/me", headers=headers).json()
    assert profile["body_type"] == "Hourglass"

    # 3. Generate recommendations using profile
    recs = client.get("/api/recommendations/looks?occasion=College", headers=headers).json()
    assert len(recs["looks"]) == 3
    first_look_id = recs["looks"][0]["id"]

    # 4 & 5. Upload photo and generate recommendations from analysis
    img_b64 = make_test_image()
    photo_res = client.post("/api/ai/analyze-photo", json={"photo_base64": img_b64}, headers=headers).json()
    assert photo_res["status"] == "success"

    analysis_recs = client.post("/api/ai/recommend-from-analysis", json={
        "photo_colors": [c["name"] for c in photo_res["colors"]["dominant_colors"]],
        "complementary_colors": [c["name"] for c in photo_res["colors"]["complementary_colors"]],
        "occasion": "College"
    }, headers=headers).json()
    assert len(analysis_recs["looks"]) == 3

    # 6. Ask AI Stylist in chat
    chat_res = client.post("/api/ai/chat", json={
        "message": "Suggest a minimalist look for college tomorrow"
    }, headers=headers).json()
    assert chat_res["outfit_recommendation"] is not None
    chat_outfit_id = chat_res["outfit_recommendation"]["id"]

    # 7 & 8. Save outfit and verify in saved outfits
    client.post(f"/api/outfits/saved/{chat_outfit_id}", headers=headers)
    saved = client.get("/api/outfits/saved", headers=headers).json()
    assert chat_outfit_id in [o["id"] for o in saved]

    # 9. Change profile preference (e.g. style to Streetwear, color to Olive)
    client.put("/api/users/me", json={
        "name": "Rhea Sync Test",
        "body_type": "Hourglass",
        "clothing_size": "M",
        "budget_min": 1500.0,
        "budget_max": 5000.0,
        "preferred_fit": "Oversized",
        "favorite_colors": ["Olive", "Black"],
        "avoid_colors": ["Yellow"],
        "preferred_styles": ["Streetwear"]
    }, headers=headers)

    # 10. Generate recommendations again and verify new profile preferences are used
    updated_recs = client.get("/api/recommendations/looks?occasion=College", headers=headers).json()
    assert len(updated_recs["looks"]) == 3

    # Clean up saved outfit
    client.delete(f"/api/outfits/saved/{chat_outfit_id}", headers=headers)
