import io
import base64
import pytest
from PIL import Image

from backend.services.virtual_tryon_service import VirtualTryOnService


def create_test_image_bytes(format="JPEG", size=(200, 300), color=(180, 150, 120)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_validate_valid_jpeg():
    raw_bytes = create_test_image_bytes(format="JPEG")
    img = VirtualTryOnService.validate_user_image(raw_bytes)
    assert img is not None
    assert img.size == (200, 300)


def test_validate_valid_png():
    raw_bytes = create_test_image_bytes(format="PNG")
    img = VirtualTryOnService.validate_user_image(raw_bytes)
    assert img is not None


def test_validate_empty_image():
    with pytest.raises(ValueError, match="No image file was uploaded"):
        VirtualTryOnService.validate_user_image(b"")


def test_validate_corrupted_image():
    with pytest.raises(ValueError, match="Invalid or corrupted image format"):
        VirtualTryOnService.validate_user_image(b"not an image definitely corrupted")


def test_validate_oversized_image():
    fake_huge_bytes = b"0" * (11 * 1024 * 1024)
    with pytest.raises(ValueError, match="too large"):
        VirtualTryOnService.validate_user_image(fake_huge_bytes)


def test_virtual_tryon_demo_mode_generation():
    raw_bytes = create_test_image_bytes()
    items = [
        {"role": "top", "name": "Black Oversized Cotton Tee", "color": "Black", "price": 899, "material": "Cotton", "style": "Streetwear"},
        {"role": "bottom", "name": "Blue Straight-Fit Jeans", "color": "Blue", "price": 999, "material": "Denim", "style": "Casual"},
        {"role": "footwear", "name": "White Classic Leather Sneakers", "color": "White", "price": 1199, "material": "Leather", "style": "Minimal"},
        {"role": "accessory", "name": "Minimalist Canvas Tote", "color": "Beige", "price": 499, "material": "Canvas", "style": "Casual"}
    ]

    res = VirtualTryOnService.generate_virtual_tryon(
        image_bytes=raw_bytes,
        outfit_title="College Casual Streetwear",
        items=items,
        style_tag="Streetwear",
        occasion="College"
    )

    assert res["status"] == "success"
    assert "data:image/" in res["tryon_image_url"]
    assert len(res["items_summary"]) == 4
    assert "disclaimer" in res
    assert "Visual approximation" in res["disclaimer"]
    assert res["mode"] in ("gemini_ai", "demo_mode")
    assert "processing_time_sec" in res


def test_virtual_tryon_with_rgba_png():
    """Verify that PNGs with RGBA alpha channel (common with web downloads) work without JPEG save error."""
    buf = io.BytesIO()
    img = Image.new("RGBA", (250, 350), color=(120, 160, 200, 180))
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    res = VirtualTryOnService.generate_virtual_tryon(
        image_bytes=raw_bytes,
        outfit_title="Relaxed College",
        items=[{"role": "top", "name": "Cashmere Sweater", "price": 2799}]
    )
    assert res["status"] == "success"
    assert "data:image/jpeg;base64," in res["tryon_image_url"]


def test_virtual_tryon_with_webp():
    """Verify that WEBP images (default format from Google Images search) work seamlessly."""
    buf = io.BytesIO()
    img = Image.new("RGBA", (200, 300), color=(220, 180, 140, 255))
    img.save(buf, format="WEBP")
    raw_bytes = buf.getvalue()

    res = VirtualTryOnService.generate_virtual_tryon(
        image_bytes=raw_bytes,
        outfit_title="Smart Casual",
        items=[{"role": "top", "name": "Oxford Shirt", "price": 1999}]
    )
    assert res["status"] == "success"
    assert "data:image/jpeg;base64," in res["tryon_image_url"]

