"""
Modular AI Virtual Try-On Service.

Provides AI outfit visualization for recommended clothing items onto user-uploaded photos.
Supports:
1. Google Gemini / Imagen generation when live API keys and models are available.
2. Intelligent, high-fidelity Demo Mode that produces clearly labelled aesthetic visualizations
   without requiring live external credentials.
3. Strict validation: size checks, format checks, corrupted image handling.
4. Privacy-preserving handling: in-memory / temporary processing without permanent image retention.
5. Explicit visual approximation disclaimers per safety and accuracy guidelines.
"""

import os
import io
import time
import base64
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP", "MPO", "BMP", "GIF"}


class VirtualTryOnService:
    @classmethod
    def to_rgb_image(cls, image: Image.Image) -> Image.Image:
        """
        Safely converts any PIL image (RGBA, LA, P, CMYK, etc.) to a standard 3-channel RGB image
        so that JPEG saving will never raise 'OSError: cannot write mode RGBA as JPEG'.
        """
        if image.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", image.size, (255, 255, 255))
            rgba = image.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
            return bg
        elif image.mode == "P":
            rgba = image.convert("RGBA")
            bg = Image.new("RGB", image.size, (255, 255, 255))
            bg.paste(rgba, mask=rgba.split()[-1])
            return bg
        elif image.mode != "RGB":
            return image.convert("RGB")
        return image

    @classmethod
    def validate_user_image(cls, image_bytes: bytes, filename: Optional[str] = None) -> Image.Image:
        """
        Validates user photo: ensures non-empty, checks file size, validates format,
        and verifies image integrity using PIL.
        """
        if not image_bytes or len(image_bytes) == 0:
            raise ValueError("No image file was uploaded. Please upload a clear photo.")

        if len(image_bytes) > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Uploaded image is too large ({round(len(image_bytes)/(1024*1024), 1)} MB). Maximum allowed size is 10 MB.")

        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()  # Verify integrity
            # Reopen after verify
            img = Image.open(io.BytesIO(image_bytes))
            img.load()  # Force decode to ensure image is complete
        except Exception:
            raise ValueError("Invalid or corrupted image format. Please upload a valid PNG, JPG, or WEBP image.")

        img_format = (img.format or "").upper()
        if img_format not in ALLOWED_FORMATS:
            raise ValueError(f"Unsupported image format: {img_format}. Allowed formats are PNG, JPG, and WEBP.")

        # Safely handle EXIF orientation if present (common with smartphone cameras)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        return img

    @classmethod
    def generate_virtual_tryon(
        cls,
        image_bytes: bytes,
        outfit_title: str,
        items: List[Dict[str, Any]],
        style_tag: str = "Casual",
        occasion: str = "Casual outing",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes AI Virtual Try-On request with user photo and selected outfit items.
        Returns try-on visualization, items summary, status, disclaimer, and operating mode.
        """
        start_time = time.time()

        # Step 1: Validate User Photo
        pil_img = cls.validate_user_image(image_bytes, filename)

        items_summary = [
            f"{it.get('role', 'item').title()}: {it.get('name', 'Garment')} ({it.get('color', '')} {it.get('material', '')} {it.get('style', '')})".strip()
            for it in (items or [])
        ]

        # Step 2: Check whether to call live Gemini Imagen or use Demo Mode
        use_live_api = (not DEMO_MODE) and bool(GEMINI_API_KEY)

        if use_live_api:
            try:
                result = cls._call_gemini_imagen_tryon(
                    pil_img=pil_img,
                    outfit_title=outfit_title,
                    items_summary=items_summary,
                    style_tag=style_tag,
                    occasion=occasion
                )
                processing_time = round(time.time() - start_time, 2)
                result["processing_time_sec"] = processing_time
                return result
            except Exception as e:
                print(f"Notice: Gemini Image API request failed ({e}). Gracefully falling back to Demo Mode.")
                # Fall through to Demo Mode fallback

        # Demo Mode (or fallback on API failure)
        result = cls._generate_demo_tryon_visualization(
            pil_img=pil_img,
            outfit_title=outfit_title,
            items=items,
            style_tag=style_tag,
            occasion=occasion
        )
        processing_time = round(time.time() - start_time, 2)
        result["processing_time_sec"] = processing_time
        return result

    @classmethod
    def _call_gemini_imagen_tryon(
        cls,
        pil_img: Image.Image,
        outfit_title: str,
        items_summary: List[str],
        style_tag: str,
        occasion: str
    ) -> Dict[str, Any]:
        """
        Calls gemini-3.1-flash-image with the person's actual photo + outfit description.
        The model edits the photo to dress the person in the selected outfit (image editing / text-and-image-to-image).
        """
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        # Convert user image to RGB JPEG for the API
        rgb_img = cls.to_rgb_image(pil_img)

        # Build a precise clothing-swap prompt
        outfit_desc = ", ".join(items_summary) if items_summary else f"a {style_tag} outfit"
        prompt = (
            f"Edit this photo: dress the person in a complete {style_tag} outfit suitable for {occasion}. "
            f"The outfit consists of: {outfit_desc}. "
            f"Keep the person's face, hairstyle, body pose, skin tone, and background EXACTLY the same. "
            f"Only change the clothing — replace whatever the person is currently wearing with the described outfit pieces. "
            f"Ensure realistic fabric drape, natural lighting consistent with the original photo, and high-fashion editorial quality. "
            f"Do NOT add or remove any person. Do NOT alter the background. Do NOT change the face."
        )

        # Pass PIL image directly — the SDK handles encoding automatically
        response = client.models.generate_content(
            model="gemini-3.1-flash-image",
            contents=[prompt, rgb_img],
        )

        # Extract the generated image from the response
        for part in response.parts:
            if part.inline_data is not None:
                mime_type = part.inline_data.mime_type or "image/jpeg"
                img_bytes = part.inline_data.data
                b64_str = base64.b64encode(img_bytes).decode("utf-8")
                data_url = f"data:{mime_type};base64,{b64_str}"
                return {
                    "status": "success",
                    "tryon_image_url": data_url,
                    "outfit_title": outfit_title,
                    "items_summary": items_summary,
                    "disclaimer": (
                        "AI Virtual Try-On: Outfit visualization generated by Gemini AI image editing. "
                        "Visual approximation only — not an exact physical garment simulation or brand fitting photograph."
                    ),
                    "mode": "gemini_ai"
                }

        raise RuntimeError("Gemini image model returned no image in the response.")

    @classmethod
    def _fetch_product_image(cls, url: str, size: tuple) -> Optional[Image.Image]:
        """
        Fetches a product image from a URL and returns it as a PIL Image resized to `size`.
        Returns None on any failure so the canvas can fall back to a placeholder.
        """
        if not url:
            return None
        try:
            import urllib.request
            headers = {"User-Agent": "Mozilla/5.0 (fashion-recommender-tryon/1.0)"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                img_data = resp.read()
            img = Image.open(io.BytesIO(img_data))
            img.load()
            img = cls.to_rgb_image(img)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return img
        except Exception:
            return None

    @classmethod
    def _draw_placeholder(cls, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, label: str) -> None:
        """Draws a styled placeholder box when a product image cannot be fetched."""
        draw.rectangle([x, y, x + w, y + h], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.text((x + 6, y + h // 2 - 6), label[:20], fill=(100, 116, 139), font=ImageFont.load_default())

    @classmethod
    def _generate_demo_tryon_visualization(
        cls,
        pil_img: Image.Image,
        outfit_title: str,
        items: List[Dict[str, Any]],
        style_tag: str,
        occasion: str
    ) -> Dict[str, Any]:
        """
        Generates a clearly labelled, high-aesthetic side-by-side collage for Demo Mode.
        LEFT half: user photo.  RIGHT half: actual product images fetched from item URLs.
        Does NOT falsely claim to be a real physical try-on.
        """
        import urllib.request

        # ── Canvas setup ─────────────────────────────────────────────────────────
        CANVAS_W, CANVAS_H = 900, 800
        HEADER_H = 80
        FOOTER_H = 48
        PADDING = 14
        COL_LEFT_W = 360           # user photo column width
        COL_RIGHT_W = CANVAS_W - COL_LEFT_W - PADDING * 3  # product grid column width

        canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (15, 23, 42))
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default()

        # ── Outer decorative borders ──────────────────────────────────────────────
        draw.rectangle([6, 6, CANVAS_W - 7, CANVAS_H - 7], outline=(212, 175, 55), width=2)
        draw.rectangle([11, 11, CANVAS_W - 12, CANVAS_H - 12], outline=(51, 65, 85), width=1)

        # ── Header ───────────────────────────────────────────────────────────────
        draw.text((PADDING + 6, 18), f"AI OUTFIT VISUALIZATION  |  {style_tag.upper()}", fill=(212, 175, 55), font=font)
        draw.text((PADDING + 6, 36), (outfit_title or "Selected Look")[:60], fill=(248, 250, 252), font=font)
        draw.text((PADDING + 6, 54), f"Curated for: {occasion}   •   Demo Mode", fill=(148, 163, 184), font=font)
        draw.line([(PADDING, HEADER_H), (CANVAS_W - PADDING, HEADER_H)], fill=(51, 65, 85), width=1)

        # ── LEFT: User photo ──────────────────────────────────────────────────────
        body_h = CANVAS_H - HEADER_H - FOOTER_H - PADDING * 2
        user_area_x = PADDING + 8
        user_area_y = HEADER_H + PADDING
        user_max_w = COL_LEFT_W - 16
        user_max_h = body_h

        rgb_user = cls.to_rgb_image(pil_img)
        user_copy = rgb_user.copy()
        user_copy.thumbnail((user_max_w, user_max_h), Image.Resampling.LANCZOS)
        uw, uh = user_copy.size
        ux = user_area_x + (user_max_w - uw) // 2
        uy = user_area_y + (user_max_h - uh) // 2

        draw.text((user_area_x + user_max_w // 2 - 25, user_area_y - 14), "YOUR PHOTO", fill=(100, 116, 139), font=font)
        draw.rectangle([ux - 3, uy - 3, ux + uw + 2, uy + uh + 2], outline=(51, 65, 85), width=1)
        canvas.paste(user_copy, (ux, uy))

        # ── Vertical divider ─────────────────────────────────────────────────────
        div_x = PADDING + COL_LEFT_W + PADDING
        draw.line([(div_x, HEADER_H + PADDING), (div_x, CANVAS_H - FOOTER_H - PADDING)], fill=(51, 65, 85), width=1)

        # ── RIGHT: Product image grid ─────────────────────────────────────────────
        right_x = div_x + PADDING
        right_y = HEADER_H + PADDING
        role_labels = {
            "top": "TOP",
            "bottom": "BOTTOM",
            "footwear": "FOOTWEAR",
            "accessory": "ACCESSORY",
        }
        role_colors = {
            "top":       (99, 179, 237),   # blue
            "bottom":    (154, 215, 160),  # green
            "footwear":  (246, 173, 85),   # amber
            "accessory": (183, 148, 244),  # purple
        }

        active_items = (items or [])[:4]
        n_items = len(active_items)
        item_h = (body_h - (n_items - 1) * 8) // max(n_items, 1) if n_items else body_h
        item_w = COL_RIGHT_W - PADDING

        draw.text((right_x, right_y - 14), "RECOMMENDED OUTFIT PIECES", fill=(212, 175, 55), font=font)

        for idx, it in enumerate(active_items):
            role = str(it.get("role", "item")).lower()
            name = str(it.get("name", "Piece"))
            price = it.get("price", 0)
            img_url = it.get("image_url", "")
            label_color = role_colors.get(role, (148, 163, 184))
            role_text = role_labels.get(role, role.upper())

            iy = right_y + idx * (item_h + 8)

            # Card background
            draw.rectangle([right_x, iy, right_x + item_w, iy + item_h],
                           fill=(22, 33, 52), outline=(51, 65, 85), width=1)

            # Try to fetch product image
            thumb_size = (item_h - 12, item_h - 12)
            product_img = cls._fetch_product_image(img_url, thumb_size)

            if product_img:
                pw, ph = product_img.size
                # Paste product image on the left of the card
                px = right_x + 6
                py = iy + (item_h - ph) // 2
                canvas.paste(product_img, (px, py))
                text_x = right_x + thumb_size[0] + 14
            else:
                # Draw placeholder square
                ph_size = min(item_h - 12, 60)
                draw.rectangle([right_x + 6, iy + 6, right_x + 6 + ph_size, iy + 6 + ph_size],
                               fill=(30, 41, 59), outline=(71, 85, 105), width=1)
                text_x = right_x + ph_size + 14

            # Role label (colored badge text)
            draw.text((text_x, iy + 10), role_text, fill=label_color, font=font)
            # Product name (truncated)
            max_chars = max(10, (item_w - (text_x - right_x) - 8) // 6)
            draw.text((text_x, iy + 24), name[:max_chars], fill=(226, 232, 240), font=font)
            # Price
            if price:
                draw.text((text_x, iy + 38), f"Rs. {price:,}", fill=(212, 175, 55), font=font)

        # ── Footer ────────────────────────────────────────────────────────────────
        footer_y = CANVAS_H - FOOTER_H + 10
        draw.line([(PADDING, footer_y - 10), (CANVAS_W - PADDING, footer_y - 10)], fill=(51, 65, 85), width=1)
        draw.text((PADDING + 6, footer_y), "Visual approximation only — not an exact physical garment simulation.", fill=(100, 116, 139), font=font)

        # ── Encode and return ─────────────────────────────────────────────────────
        buffer = io.BytesIO()
        canvas.save(buffer, format="JPEG", quality=90)
        composite_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        composite_data_url = f"data:image/jpeg;base64,{composite_b64}"

        items_summary = [
            f"{it.get('role', 'item').title()}: {it.get('name', 'Piece')} (₹{it.get('price', 0)})"
            for it in (items or [])
        ]

        return {
            "status": "success",
            "tryon_image_url": composite_data_url,
            "outfit_title": outfit_title,
            "items_summary": items_summary,
            "disclaimer": (
                "Demo Outfit Visualization: This is a styled preview collage showing your photo alongside "
                "the recommended outfit pieces. Connect an AI image-generation model for full virtual try-on. "
                "Visual approximation only, not a physical garment simulation."
            ),
            "mode": "demo_mode"
        }
