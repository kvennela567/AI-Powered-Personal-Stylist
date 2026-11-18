import io
import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.database import Base
from backend.models.entities import User, UserProfile, Product
from backend.services.photo_analysis_service import PhotoAnalysisService


def create_test_image_bytes(format="JPEG", size=(200, 320), color=(30, 60, 110)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_validate_valid_jpeg():
    raw_bytes = create_test_image_bytes(format="JPEG")
    img = PhotoAnalysisService.validate_and_load(raw_bytes)
    assert img is not None
    assert img.size == (200, 320)
    assert img.mode == "RGB"


def test_validate_valid_png():
    raw_bytes = create_test_image_bytes(format="PNG")
    img = PhotoAnalysisService.validate_and_load(raw_bytes)
    assert img is not None
    assert img.mode == "RGB"


def test_validate_valid_webp():
    raw_bytes = create_test_image_bytes(format="WEBP")
    img = PhotoAnalysisService.validate_and_load(raw_bytes)
    assert img is not None
    assert img.mode == "RGB"


def test_validate_rgba_png_conversion():
    buf = io.BytesIO()
    img = Image.new("RGBA", (200, 300), color=(120, 160, 200, 200))
    img.save(buf, format="PNG")
    res_img = PhotoAnalysisService.validate_and_load(buf.getvalue())
    assert res_img.mode == "RGB"


def test_validate_empty_image():
    with pytest.raises(ValueError, match="No image file was provided"):
        PhotoAnalysisService.validate_and_load(b"")


def test_validate_corrupted_image():
    with pytest.raises(ValueError, match="Invalid or corrupted image format"):
        PhotoAnalysisService.validate_and_load(b"not an image definitely corrupted")


def test_validate_oversized_image():
    fake_huge_bytes = b"0" * (11 * 1024 * 1024)
    with pytest.raises(ValueError, match="too large"):
        PhotoAnalysisService.validate_and_load(fake_huge_bytes)


def test_lighting_assessment():
    # Dim image
    dim_img = Image.new("RGB", (100, 100), color=(20, 20, 20))
    lighting_dim = PhotoAnalysisService.assess_lighting(dim_img)
    assert lighting_dim["is_suitable"] is False
    assert "Under-exposed" in lighting_dim["quality"]

    # Balanced image
    balanced_img = Image.new("RGB", (100, 100), color=(140, 150, 160))
    # Add contrast
    for x in range(50):
        for y in range(100):
            balanced_img.putpixel((x, y), (80, 90, 100))
    lighting_bal = PhotoAnalysisService.assess_lighting(balanced_img)
    assert lighting_bal["is_suitable"] is True


def test_dominant_color_extraction():
    img = Image.new("RGB", (200, 300), color=(0, 31, 63))  # Navy
    colors = PhotoAnalysisService.extract_dominant_colors(img)
    assert "dominant_colors" in colors
    assert len(colors["dominant_colors"]) > 0
    top_color = colors["dominant_colors"][0]
    assert top_color["name"] == "Navy"
    assert "complementary_colors" in colors
    assert len(colors["complementary_colors"]) > 0


def test_skin_tone_unsuitable_lighting_guard():
    # Under bad lighting, skin tone detection must be marked unavailable
    dim_img = Image.new("RGB", (100, 100), color=(15, 15, 15))
    lighting = PhotoAnalysisService.assess_lighting(dim_img)
    res = PhotoAnalysisService.detect_skin_tone_family(dim_img, lighting)
    assert res["available"] is False
    assert "lighting" in res["note"].lower()


def test_silhouette_aspect_ratio_guard():
    # Horizontal/square photo cannot determine full-body silhouette
    square_img = Image.new("RGB", (300, 300), color=(120, 120, 120))
    res = PhotoAnalysisService.estimate_body_shape_silhouette(square_img)
    assert res["available"] is False
    assert "full-body" in res["note"].lower()


def test_complete_analyze_photo_pipeline():
    raw_bytes = create_test_image_bytes()
    analysis = PhotoAnalysisService.analyze_photo(raw_bytes)
    assert analysis["status"] == "success"
    assert "colors" in analysis
    assert "dominant_colors" in analysis["colors"]
    assert "complementary_colors" in analysis["colors"]
    assert "skin_tone" in analysis
    assert "silhouette" in analysis
    assert "clothing" in analysis
    assert "engine_used" in analysis
    assert "disclaimer" in analysis
