"""
AI Stylist Conversational Service.
Integrates Google Gemini API using google-genai SDK when GEMINI_API_KEY is available.
Includes a rich, context-aware Intelligent Demo Mode that mimics a master luxury personal stylist
so the application functions 100% out of the box without requiring external credentials.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


class GeminiStylistService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = None
        self.is_live = False

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self.is_live = True
                print("Gemini API Client initialized successfully.")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini Client ({e}). Falling back to Intelligent Demo Mode.")
                self.is_live = False
        else:
            print("No GEMINI_API_KEY detected. Running in Intelligent Demo Mode.")

    def chat_with_stylist(
        self,
        message: str,
        user_ctx: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        recommended_outfit: Optional[Dict[str, Any]] = None,
        weather_context: str = "Mild (24°C)"
    ) -> Dict[str, Any]:
        """
        Processes conversation with virtual personal stylist.
        Returns conversational reply, follow-up suggestions, and active engine identifier.
        """
        if self.is_live and self.client:
            try:
                return self._call_gemini_api(
                    message, user_ctx, conversation_history, recommended_outfit, weather_context
                )
            except Exception as e:
                print(f"Gemini API request error ({e}), switching to Intelligent Demo Mode fallback.")
                return self._intelligent_demo_response(
                    message, user_ctx, recommended_outfit, weather_context
                )
        else:
            return self._intelligent_demo_response(
                message, user_ctx, recommended_outfit, weather_context
            )

    def _call_gemini_api(
        self,
        message: str,
        user_ctx: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]],
        recommended_outfit: Optional[Dict[str, Any]],
        weather_context: str
    ) -> Dict[str, Any]:
        """Calls Google Gemini using the google-genai SDK."""
        from google.genai import types

        system_instruction = (
            "You are 'Aura', a world-class luxury personal fashion stylist for a premier e-commerce platform. "
            "You provide highly tailored, warm, confident, and sophisticated fashion advice. "
            f"User Profile: Name: {user_ctx.get('name')}, Body Type: {user_ctx.get('body_type')}, "
            f"Preferred Styles: {', '.join(user_ctx.get('preferred_styles', []))}, "
            f"Favorite Colors: {', '.join(user_ctx.get('favorite_colors', []))}, "
            f"Avoided Colors: {', '.join(user_ctx.get('avoid_colors', []))}, "
            f"Budget Range: ₹{user_ctx.get('budget_min')} - ₹{user_ctx.get('budget_max')}, "
            f"Preferred Fit: {user_ctx.get('preferred_fit')}, Disliked: {user_ctx.get('disliked_clothing')}. "
            f"Current Weather: {weather_context}. "
            "Always tailor your advice strictly around these preferences without asking questions the user already answered in their profile. "
            "Be encouraging, concise (2-3 short paragraphs max), and give concrete styling tips (e.g. how to cuff trousers, layering, jewelry pairing). "
            "Always end with 2-3 quick follow-up prompt suggestions."
        )

        prompt_text = f"User says: {message}\n"
        if recommended_outfit:
            items_str = ", ".join([f"{it['role'].title()}: {it['product'].name} (₹{it['product'].price})" for it in recommended_outfit.get("items", [])])
            prompt_text += f"\nRecommended Outfit: {recommended_outfit.get('title')} (Total: ₹{recommended_outfit.get('total_price')})\nPieces: {items_str}\n"

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                max_output_tokens=600
            )
        )

        reply_text = response.text if response.text else "I'd be thrilled to help curate your look!"
        suggestions = self._extract_follow_ups(message, recommended_outfit)

        return {
            "reply": reply_text,
            "follow_up_suggestions": suggestions,
            "engine_used": "Google Gemini 2.5 Flash"
        }

    def _intelligent_demo_response(
        self,
        message: str,
        user_ctx: Dict[str, Any],
        recommended_outfit: Optional[Dict[str, Any]],
        weather_context: str
    ) -> Dict[str, Any]:
        """
        Sophisticated rule & template-based intelligent stylist that parses context,
        budget, occasion, fit, and aesthetic tags to simulate a luxury AI stylist seamlessly.
        """
        msg_lower = message.lower()
        name = user_ctx.get("name", "there")
        fav_colors = ", ".join(user_ctx.get("favorite_colors", ["Navy", "White", "Beige"])[:3])
        budget_max = int(user_ctx.get("budget_max", 5000))
        fit = user_ctx.get("preferred_fit", "Relaxed")

        # Detect intent
        if any(w in msg_lower for w in ["college", "university", "campus"]):
            reply = (
                f"Hello {name}! For campus days, comfort and effortless coolness are everything. "
                f"Based on your {fit.lower()} fit preference, I've curated a relaxed aesthetic featuring your favorite {fav_colors} palette. "
                f"A breathable heavyweight cotton top paired with durable selvedge denim keeps you comfortable through lectures and library sessions, "
                f"while staying comfortably within your ₹{budget_max:,} budget."
            )
        elif any(w in msg_lower for w in ["office", "interview", "formal", "work", "meeting"]):
            reply = (
                f"Hi {name}, for your professional engagements, a tailored yet modern silhouette commands respect without feeling stiff. "
                f"I've balanced your preference for {fav_colors} with a clean structured blazer and crisp shirting. "
                f"Notice how the tailored trousers flatter your {user_ctx.get('body_type', 'profile')} silhouette while remaining flexible for day-long meetings."
            )
        elif any(w in msg_lower for w in ["date", "dinner", "evening", "night"]):
            reply = (
                f"Date night styling is all about understated elegance and tactile textures! "
                f"I've selected rich tones complementary to your {fav_colors} palette. "
                f"The combination of subtle sheen with minimalist leather accents strikes the perfect balance between relaxed confidence and alluring charm."
            )
        elif any(w in msg_lower for w in ["wedding", "reception", "party", "festival"]):
            reply = (
                f"For celebratory events, festive craftsmanship takes center stage. "
                f"I've highlighted refined artisanal handloom pieces accented with warm metallic touches. "
                f"The look honors occasion traditions while staying true to your contemporary {fit.lower()} aesthetic."
            )
        elif any(w in msg_lower for w in ["rain", "monsoon", "cold", "winter", "weather"]):
            reply = (
                f"Considering the {weather_context.lower()} forecast, smart fabric engineering is key. "
                f"I've prioritized moisture-wicking and protective layers, paired with sturdy lug-sole footwear so you stay polished and protected against the elements."
            )
        else:
            reply = (
                f"Wonderful to style you today, {name}! "
                f"Keeping your {user_ctx.get('body_type', 'silhouette')} proportions and love for {fav_colors} in focus, "
                f"I've put together a versatile outfit designed for maximum wearability under ₹{budget_max:,}. "
                f"Each piece can be effortlessly mixed and matched across your existing wardrobe."
            )

        # Append outfit-specific commentary if an outfit was passed
        if recommended_outfit:
            title = recommended_outfit.get("title", "Curated Look")
            total = int(recommended_outfit.get("total_price", 0))
            reply += f"\n\nTake a look at **{title}** below (Total: ₹{total:,}). You can customize any item using Mix & Match or visualize it on our AI canvas!"

        suggestions = self._extract_follow_ups(message, recommended_outfit)

        return {
            "reply": reply,
            "follow_up_suggestions": suggestions,
            "engine_used": "Intelligent Demo Engine (AI Stylist)"
        }

    def _extract_follow_ups(self, message: str, recommended_outfit: Optional[Dict[str, Any]]) -> List[str]:
        """Provides interactive one-click follow-up prompt pills."""
        return [
            "Can you reduce the total price?",
            "Show me a more formal alternative",
            "What footwear would elevate this look?",
            "Adapt this for rainy weather"
        ]
