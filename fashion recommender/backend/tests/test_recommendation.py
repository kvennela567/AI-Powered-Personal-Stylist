import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.database import Base
from backend.models.entities import Product, User, UserProfile
from backend.seed_data import seed_database
from backend.services.recommendation_service import RecommendationEngine
from backend.services.preference_service import PreferenceService


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield db
    db.close()


def test_seed_database_populated(test_db):
    product_count = test_db.query(Product).count()
    assert product_count >= 30, f"Expected at least 30 products, got {product_count}"

    user = test_db.query(User).filter_by(username="demo_user").first()
    assert user is not None
    assert user.profile is not None
    assert user.profile.name == "Rhea Sharma"


def test_generate_three_looks(test_db):
    engine = RecommendationEngine(test_db)
    user = test_db.query(User).filter_by(username="demo_user").first()

    looks = engine.generate_three_looks(
        user_id=user.id,
        occasion="College",
        budget_min=1000.0,
        budget_max=6000.0,
        weather="Mild (24°C)"
    )

    assert len(looks) == 3, f"Expected 3 looks, got {len(looks)}"
    for look in looks:
        assert len(look["items"]) in [3, 4], "Each outfit must have 3 or 4 items (complete outfit or separates + footwear + accessory)"
        roles = {it["role"] for it in look["items"]}
        assert roles in [{"top", "bottom", "footwear", "accessory"}, {"complete_outfit", "footwear", "accessory"}]
        assert look["total_price"] > 0
        assert "explanation" in look and len(look["explanation"]) > 20
        assert 0 <= look["match_score"] <= 100


def test_mix_and_match_alternatives(test_db):
    engine = RecommendationEngine(test_db)
    user = test_db.query(User).filter_by(username="demo_user").first()

    # Get sample products
    products = test_db.query(Product).limit(3).all()
    accepted_ids = [p.id for p in products]

    alternatives = engine.get_mix_match_alternatives(
        user_id=user.id,
        accepted_product_ids=accepted_ids,
        role_to_replace="bottom",
        occasion="College",
        budget_max=6000.0
    )

    assert len(alternatives) > 0
    for alt in alternatives:
        assert alt["replacement_product"].category == "Clothing"
        assert alt["replacement_product"].id not in accepted_ids
        assert alt["new_total_price"] > 0


def test_preference_learning_feedback(test_db):
    pref_service = PreferenceService(test_db)
    user = test_db.query(User).filter_by(username="demo_user").first()

    result = pref_service.record_feedback(
        user_id=user.id,
        outfit_id=1,
        feedback_type="like",
        comment="Love natural cotton and linen"
    )

    assert result["status"] == "success"
    assert "preference_update" in result
