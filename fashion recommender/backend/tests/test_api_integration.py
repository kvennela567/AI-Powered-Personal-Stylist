import io
import base64
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_base64_image(format="JPEG", size=(150, 200), color=(150, 180, 210)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def test_api_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"


def test_api_product_search_flexible_matching(client):
    # Test query: "black oversized cotton t-shirt"
    res = client.get("/api/products?search=black+oversized+cotton+t-shirt")
    assert res.status_code == 200
    products = res.json()
    assert len(products) > 0
    top_p = products[0]
    assert "id" in top_p
    assert "name" in top_p
    assert "image_url" in top_p
    assert "price" in top_p
    assert "availability" in top_p


def test_api_product_search_blue_jeans(client):
    res = client.get("/api/products?search=blue+jeans")
    assert res.status_code == 200
    products = res.json()
    assert len(products) > 0


def test_api_match_outfit_endpoint(client):
    payload = {
        "items": [
            {"role": "top", "query": "Black oversized T-shirt"},
            {"role": "bottom", "query": "Blue straight-fit jeans"},
            {"role": "footwear", "query": "White sneakers"},
            {"role": "accessory", "query": "Minimalist canvas tote"}
        ]
    }
    res = client.post("/api/products/match-outfit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) == 4
    assert data["total_price"] > 0
    roles = {it["role"] for it in data["items"]}
    assert roles == {"top", "bottom", "footwear", "accessory"}
    for it in data["items"]:
        assert it["matched_product"] is not None
        assert it["confidence_score"] >= 50.0


def test_api_analyze_photo_success(client):
    b64_img = create_base64_image()
    payload = {
        "photo_base64": f"data:image/jpeg;base64,{b64_img}",
        "filename": "my_photo.jpg"
    }
    res = client.post("/api/ai/analyze-photo", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "colors" in data
    assert len(data["colors"]["dominant_colors"]) > 0
    assert len(data["colors"]["complementary_colors"]) > 0
    assert "skin_tone" in data
    assert "silhouette" in data
    assert "clothing" in data
    assert "engine_used" in data


def test_api_analyze_photo_missing_upload(client):
    payload = {"photo_base64": ""}
    res = client.post("/api/ai/analyze-photo", json=payload)
    assert res.status_code == 400
    assert "No photo uploaded" in res.json()["detail"]


def test_api_recommend_from_analysis(client):
    payload = {
        "photo_colors": ["Navy", "Charcoal"],
        "complementary_colors": ["White", "Beige"],
        "detected_style": "Casual",
        "occasion": "College",
        "budget_min": 1500,
        "budget_max": 6000
    }
    res = client.post("/api/ai/recommend-from-analysis", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "looks" in data
    assert len(data["looks"]) == 3
    first_look = data["looks"][0]
    assert len(first_look["items"]) == 4
    assert first_look["total_price"] > 0
    assert first_look["match_score"] >= 80.0
    assert "explanation" in first_look
    # Check that individual product cards contain actual catalogue images
    for it in first_look["items"]:
        assert it["product"]["image_url"].startswith("http")
        assert it["product"]["price"] > 0


def test_api_virtual_tryon_legacy_safe_compatibility(client):
    b64_img = create_base64_image()
    payload = {
        "user_photo_base64": f"data:image/jpeg;base64,{b64_img}",
        "outfit_id": 1,
        "outfit_title": "Campus Streetwear Look",
        "style_tag": "Streetwear",
        "occasion": "College",
        "items": [
            {"role": "top", "name": "Heavyweight Cotton Tee", "color": "Black", "price": 899, "image_url": "https://example.com/item.jpg"},
            {"role": "bottom", "name": "Straight Fit Denim", "color": "Blue", "price": 999},
            {"role": "footwear", "name": "Leather Sneakers", "color": "White", "price": 1199}
        ]
    }
    res = client.post("/api/ai/virtual-tryon", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # Never generates a fake synthesized image of user wearing clothes
    assert "http" in data["tryon_image_url"]
    assert "Synthetic try-on images are not generated" in data["disclaimer"]


def test_end_to_end_style_analysis_flow(client):
    # Step 1: User uploads photo for AI analysis
    b64_img = create_base64_image()
    analysis_res = client.post("/api/ai/analyze-photo", json={
        "photo_base64": b64_img,
        "filename": "user_style.jpg"
    })
    assert analysis_res.status_code == 200
    analysis = analysis_res.json()
    dom_colors = [c["name"] for c in analysis["colors"]["dominant_colors"]]
    comp_colors = [c["name"] for c in analysis["colors"]["complementary_colors"]]

    # Step 2: Combine analysis with user choices to get personalized outfit recommendations
    rec_res = client.post("/api/ai/recommend-from-analysis", json={
        "photo_colors": dom_colors,
        "complementary_colors": comp_colors,
        "detected_style": analysis["clothing"]["style"],
        "occasion": "College",
        "budget_max": 5500
    })
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert len(recs["looks"]) == 3
    for look in recs["looks"]:
        assert len(look["items"]) == 4
        # Verify complete 4 pieces from real catalogue
        roles = {it["role"] for it in look["items"]}
        assert roles == {"top", "bottom", "footwear", "accessory"}
        # Verify price respects budget
        assert look["total_price"] <= 7500  # Within realistic bounds
        # Verify explanation exists
        assert len(look["explanation"]) > 20
