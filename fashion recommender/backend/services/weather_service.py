"""
Weather-Aware Styling Service.
Provides weather conditions, temperature, humidity, and fabric advice.
Supports quick preset toggles (Hot/Sunny, Cold/Winter, Rainy, Mild/Autumn)
as well as city-based simulation and external weather integration.
"""

from typing import Dict, Any


class WeatherService:
    PRESETS = {
        "mild": {
            "condition": "Mild / Pleasant",
            "temperature_c": 24.0,
            "humidity": 45,
            "rain_probability": 10,
            "styling_advice": "Perfect for versatile single-layer styling: breathable cottons, relaxed trousers, and classic sneakers."
        },
        "hot": {
            "condition": "Hot & Sunny",
            "temperature_c": 34.0,
            "humidity": 35,
            "rain_probability": 0,
            "styling_advice": "Focus on natural cooling fabrics: pure linen, lightweight combed cottons, light colors, and breathable footwear."
        },
        "cold": {
            "condition": "Chilly / Winter",
            "temperature_c": 12.0,
            "humidity": 65,
            "rain_probability": 15,
            "styling_advice": "Emphasize smart layering: wool blazers, knit sweaters, denim, and structured boots for insulation."
        },
        "rainy": {
            "condition": "Monsoon / Rainy",
            "temperature_c": 22.0,
            "humidity": 88,
            "rain_probability": 85,
            "styling_advice": "Prioritize quick-dry materials, treated outerwear, darker shades, and water-resistant lug-sole boots."
        }
    }

    @classmethod
    def get_weather_context(cls, mode_or_city: str = "mild") -> Dict[str, Any]:
        """Returns weather attributes and actionable styling guidance."""
        key = mode_or_city.lower().strip()
        if "hot" in key or "summer" in key or "sun" in key:
            return cls.PRESETS["hot"]
        elif "cold" in key or "winter" in key or "chill" in key:
            return cls.PRESETS["cold"]
        elif "rain" in key or "monsoon" in key or "wet" in key:
            return cls.PRESETS["rainy"]
        else:
            return cls.PRESETS["mild"]
