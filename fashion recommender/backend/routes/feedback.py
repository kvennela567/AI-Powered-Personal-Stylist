from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.entities import User
from ..models.schemas import FeedbackRequest, FeedbackResponse
from ..services.preference_service import PreferenceService
from .users import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    payload: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record user feedback on recommendations (likes, dislikes, item swaps, or comments)
    and adapt continuous preference learning weights.
    """

    pref_service = PreferenceService(db)
    result = pref_service.record_feedback(
        user_id=user.id,
        outfit_id=payload.outfit_id,
        feedback_type=payload.feedback_type,
        item_role=payload.item_role,
        comment=payload.comment
    )

    return FeedbackResponse(
        status=result["status"],
        message=result["message"],
        preference_update=result.get("preference_update")
    )
