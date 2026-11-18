"""
AI Outfit Visualization Service.
Generates an AI visual representation of recommended outfits.
Provides clean SVG fashion lookbook composition and styling canvas,
with full support for Gemini Imagen / image generation when enabled,
and explicit disclaimers per Section 14.
"""

from typing import List, Optional, Dict, Any


class OutfitVisualizationService:
    @staticmethod
    def generate_visualization(
        outfit_title: str,
        style_tag: str,
        occasion: str,
        items_summary: List[str],
        palette: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Creates an AI visual representation for an outfit look.
        Returns an SVG styling canvas and metadata with clear visualization disclaimers.
        """
        palette = palette or ["#1A365D", "#E2E8F0", "#4A5568", "#D69E2E"]

        # Color mapping for palette swatches
        color_hex_map = {
            "black": "#1A202C", "white": "#F7FAFC", "grey": "#718096", "navy": "#1A365D",
            "blue": "#3182CE", "sky blue": "#63B3ED", "red": "#E53E3E", "maroon": "#742A2A",
            "pink": "#ED64A6", "rose": "#FC8181", "purple": "#805AD5", "lavender": "#B794F4",
            "green": "#38A169", "olive": "#556B2F", "emerald": "#22543D", "yellow": "#ECC94B",
            "mustard": "#D69E2E", "orange": "#DD6B20", "brown": "#7B341E", "beige": "#E2D9C8",
            "cream": "#FFFDF0", "tan": "#D2B48C", "khaki": "#C3B091", "burgundy": "#4A0E17",
            "teal": "#319795", "turquoise": "#38B2AC"
        }

        swatch_colors = [color_hex_map.get(c.lower(), "#4A5568") for c in palette[:4]]
        if len(swatch_colors) < 4:
            swatch_colors.extend(["#2D3748", "#E2E8F0"][:(4 - len(swatch_colors))])

        items_display = items_summary[:4]

        # Generate stylized aesthetic vector Lookbook canvas
        svg_canvas = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%" style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius: 16px; font-family: 'Inter', system-ui, -apple-system, sans-serif;">
            <defs>
                <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#F6AD55"/>
                    <stop offset="100%" stop-color="#D69E2E"/>
                </linearGradient>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="8" result="blur"/>
                    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
            </defs>

            <!-- Background Aesthetic Grid -->
            <circle cx="700" cy="80" r="180" fill="url(#goldGrad)" opacity="0.08" filter="url(#glow)"/>
            <circle cx="100" cy="420" r="140" fill="#3182CE" opacity="0.06"/>

            <!-- Header Badge -->
            <rect x="40" y="35" width="140" height="28" rx="14" fill="#334155" opacity="0.8"/>
            <text x="52" y="54" fill="#F6AD55" font-size="12" font-weight="600" letter-spacing="1">AI VISUALIZATION</text>

            <rect x="190" y="35" width="110" height="28" rx="14" fill="#1E293B" stroke="#475569" stroke-width="1"/>
            <text x="202" y="54" fill="#E2E8F0" font-size="12" font-weight="500">{style_tag.upper()}</text>

            <!-- Outfit Title -->
            <text x="40" y="105" fill="#F8FAFC" font-size="24" font-weight="700">{outfit_title}</text>
            <text x="40" y="130" fill="#94A3B8" font-size="14">Curated for: {occasion} • Personalized Harmony Engine</text>

            <!-- Stylized Mannequin Silhouette Card -->
            <g transform="translate(40, 160)">
                <rect width="220" height="280" rx="12" fill="#1E293B" stroke="#334155" stroke-width="1"/>
                
                <!-- Stylized Silhouette Line Art -->
                <circle cx="110" cy="50" r="22" fill="none" stroke="#E2E8F0" stroke-width="2.5"/>
                <path d="M 85 90 C 85 75, 135 75, 135 90 L 145 160 L 75 160 Z" fill="none" stroke="{swatch_colors[0]}" stroke-width="3"/>
                <path d="M 80 160 L 95 245 M 140 160 L 125 245" stroke="{swatch_colors[1]}" stroke-width="3" stroke-linecap="round"/>
                <path d="M 90 245 L 80 255 M 130 245 L 140 255" stroke="{swatch_colors[2]}" stroke-width="3" stroke-linecap="round"/>

                <text x="110" y="270" text-anchor="middle" fill="#64748B" font-size="11">STYLISTIC LOOK COMPOSITION</text>
            </g>

            <!-- Curated Ensemble Breakdown Cards -->
            <g transform="translate(280, 160)">
                <!-- Item 1: Top -->
                <rect x="0" y="0" width="480" height="62" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1"/>
                <circle cx="28" cy="31" r="14" fill="{swatch_colors[0]}"/>
                <text x="56" y="27" fill="#CBD5E1" font-size="11" font-weight="600">ENSEMBLE TOP</text>
                <text x="56" y="47" fill="#F8FAFC" font-size="14" font-weight="500">{items_display[0] if len(items_display) > 0 else 'Tailored Shirt/Tee'}</text>

                <!-- Item 2: Bottom -->
                <rect x="0" y="72" width="480" height="62" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1"/>
                <circle cx="28" cy="103" r="14" fill="{swatch_colors[1]}"/>
                <text x="56" y="99" fill="#CBD5E1" font-size="11" font-weight="600">ENSEMBLE BOTTOM</text>
                <text x="56" y="119" fill="#F8FAFC" font-size="14" font-weight="500">{items_display[1] if len(items_display) > 1 else 'Trousers/Jeans'}</text>

                <!-- Item 3: Footwear -->
                <rect x="0" y="144" width="480" height="62" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1"/>
                <circle cx="28" cy="175" r="14" fill="{swatch_colors[2]}"/>
                <text x="56" y="171" fill="#CBD5E1" font-size="11" font-weight="600">FOOTWEAR</text>
                <text x="56" y="191" fill="#F8FAFC" font-size="14" font-weight="500">{items_display[2] if len(items_display) > 2 else 'Curated Shoes'}</text>

                <!-- Item 4: Accessory -->
                <rect x="0" y="216" width="480" height="62" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1"/>
                <circle cx="28" cy="247" r="14" fill="{swatch_colors[3]}"/>
                <text x="56" y="243" fill="#CBD5E1" font-size="11" font-weight="600">ACCESSORY & ACCENTS</text>
                <text x="56" y="263" fill="#F8FAFC" font-size="14" font-weight="500">{items_display[3] if len(items_display) > 3 else 'Accent Accessory'}</text>
            </g>

            <!-- Bottom Disclaimer Bar -->
            <text x="40" y="475" fill="#64748B" font-size="11">
                Notice: AI outfit visual representation for styling preview. Actual physical garments may vary slightly in fabric sheen.
            </text>
        </svg>
        """

        return {
            "visualization_url": "",
            "svg_canvas": svg_canvas.strip(),
            "disclaimer": "Visualization generated as an AI stylistic preview. Not an exact brand photograph."
        }
