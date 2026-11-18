import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.database import Base
from backend.models.entities import Product
from backend.seed_data import seed_database
from backend.services.product_search_service import ProductSearchService


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield db
    db.close()


def test_flexible_search_black_oversized_tshirt(test_db):
    results = ProductSearchService.search_catalogue(
        db=test_db,
        query_text="black oversized t-shirt"
    )
    assert len(results) > 0, "Expected matching products for 'black oversized t-shirt'"
    top_result = results[0]
    assert "black" in (top_result.color.lower() + top_result.name.lower())
    assert "tee" in top_result.name.lower() or "t-shirt" in top_result.name.lower() or "t-shirts" in top_result.subcategory.lower()


def test_flexible_search_blue_jeans(test_db):
    results = ProductSearchService.search_catalogue(
        db=test_db,
        query_text="blue jeans"
    )
    assert len(results) > 0, "Expected matching products for 'blue jeans'"
    names = [r.name.lower() for r in results]
    colors = [r.color.lower() for r in results]
    assert any("blue" in c for c in colors)
    assert any("denim" in n or "jeans" in n for n in names)


def test_search_by_color_category_style(test_db):
    results = ProductSearchService.search_catalogue(
        db=test_db,
        category="Footwear",
        color="White"
    )
    assert len(results) > 0
    for r in results:
        assert r.category == "Footwear"
        assert "white" in r.color.lower()


def test_match_outfit_items(test_db):
    top_match = ProductSearchService.match_outfit_item(
        db=test_db,
        role="top",
        query_text="Black oversized cotton T-shirt"
    )
    assert top_match["matched_product"] is not None
    assert top_match["confidence_score"] >= 60.0

    bottom_match = ProductSearchService.match_outfit_item(
        db=test_db,
        role="bottom",
        query_text="Blue straight-fit jeans"
    )
    assert bottom_match["matched_product"] is not None

    shoe_match = ProductSearchService.match_outfit_item(
        db=test_db,
        role="footwear",
        query_text="White sneakers"
    )
    assert shoe_match["matched_product"] is not None
    assert shoe_match["matched_product"].category == "Footwear"


def test_empty_search_results(test_db):
    results = ProductSearchService.search_catalogue(
        db=test_db,
        query_text="nonexistentastronautspacesuithologramxyz123"
    )
    assert len(results) == 0
