"""
Preference Learning & Feedback Service.
Records user likes, dislikes, item swaps, and natural-language feedback.
Updates dynamic affinity weights so future recommendations automatically adapt.
Prepares telemetry and interaction logs for future ML training models.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.entities import Feedback, UserPreferenceWeight, Outfit, OutfitItem, Product, UserProfile


class PreferenceService:
    def __init__(self, db: Session):
        self.db = db

    def record_feedback(
        self,
        user_id: int,
        outfit_id: int,
        feedback_type: str,
        item_role: Optional[str] = "",
        comment: Optional[str] = ""
    ) -> Dict[str, Any]:
        """
        Stores user feedback and adjusts preference learning weights.
        """
        # 1. Record raw feedback log
        fb = Feedback(
            user_id=user_id,
            outfit_id=outfit_id,
            feedback_type=feedback_type,
            item_role=item_role or "",
            comment=comment or ""
        )
        self.db.add(fb)

        # 2. Retrieve outfit and its items to learn from
        outfit = self.db.query(Outfit).filter_by(id=outfit_id).first()
        update_summary = []

        if outfit:
            # If outfit was LIKED or SAVED:
            if feedback_type in ["like", "save"]:
                self._boost_feature_weight(user_id, "style", outfit.style_tag, delta=+8.0)
                update_summary.append(f"Boosted style affinity for '{outfit.style_tag}'")

                # Boost colors of constituent items
                for it in outfit.items:
                    if it.product:
                        self._boost_feature_weight(user_id, "color", it.product.color, delta=+4.0)

            # If outfit was DISLIKED:
            elif feedback_type == "dislike":
                self._boost_feature_weight(user_id, "style", outfit.style_tag, delta=-8.0)
                update_summary.append(f"Reduced style affinity for '{outfit.style_tag}'")
                for it in outfit.items:
                    if it.product:
                        self._boost_feature_weight(user_id, "color", it.product.color, delta=-3.0)

            # Free-text feedback parsing (e.g. "don't want jeans", "hate neon", "prefer cotton")
            if comment:
                c_lower = comment.lower()
                profile = self.db.query(UserProfile).filter_by(user_id=user_id).first()

                if "don't want" in c_lower or "no " in c_lower or "dislike" in c_lower:
                    if "jeans" in c_lower:
                        self._boost_feature_weight(user_id, "subcategory", "Jeans", delta=-15.0)
                        update_summary.append("Noted avoidance of jeans based on feedback")
                    if "polyester" in c_lower:
                        self._boost_feature_weight(user_id, "material", "Polyester", delta=-15.0)
                        update_summary.append("Reduced preference for synthetic polyester")

                if "love" in c_lower or "prefer" in c_lower or "like" in c_lower:
                    if "cotton" in c_lower:
                        self._boost_feature_weight(user_id, "material", "Cotton", delta=+10.0)
                        update_summary.append("Increased affinity for natural cotton")
                    if "linen" in c_lower:
                        self._boost_feature_weight(user_id, "material", "Linen", delta=+10.0)
                        update_summary.append("Increased affinity for linen")

        self.db.commit()

        return {
            "status": "success",
            "message": "Feedback recorded and preference learning model weights updated.",
            "preference_update": "; ".join(update_summary) if update_summary else "Learned from your feedback."
        }

    def _boost_feature_weight(self, user_id: int, feature_type: str, feature_value: str, delta: float):
        """Helper to create or increment continuous preference weight."""
        val_cleaned = feature_value.strip().capitalize()
        weight_row = (
            self.db.query(UserPreferenceWeight)
            .filter_by(user_id=user_id, feature_type=feature_type, feature_value=val_cleaned)
            .first()
        )
        if not weight_row:
            weight_row = UserPreferenceWeight(
                user_id=user_id,
                feature_type=feature_type,
                feature_value=val_cleaned,
                weight_delta=delta
            )
            self.db.add(weight_row)
        else:
            weight_row.weight_delta += delta
