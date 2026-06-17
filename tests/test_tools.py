"""
tests/test_tools.py
 
"""
 
import pytest
from unittest.mock import patch, MagicMock
 
from tools import search_listings, suggest_outfit, create_fit_card
 
  
SAMPLE_ITEM = {
    "id": "lst_006",
    "title": "Graphic Tee — 2003 Tour Bootleg Style",
    "description": "Vintage-style bootleg tee with faded graphic.",
    "category": "tops",
    "style_tags": ["graphic tee", "vintage", "grunge", "streetwear", "band tee"],
    "size": "L",
    "condition": "good",
    "price": 24.00,
    "colors": ["black"],
    "brand": None,
    "platform": "depop",
}
 
EXAMPLE_WARDROBE = {
    "items": [
        {
            "id": "w_001",
            "name": "Baggy straight-leg jeans, dark wash",
            "category": "bottoms",
            "colors": ["dark blue", "indigo"],
            "style_tags": ["denim", "streetwear", "baggy"],
            "notes": "High-waisted, sits above the hip",
        },
        {
            "id": "w_007",
            "name": "Chunky white sneakers",
            "category": "shoes",
            "colors": ["white"],
            "style_tags": ["sneakers", "chunky", "streetwear"],
            "notes": None,
        },
        {
            "id": "w_006",
            "name": "Vintage black denim jacket",
            "category": "outerwear",
            "colors": ["black"],
            "style_tags": ["denim", "vintage", "classic"],
            "notes": "Slightly cropped",
        },
    ]
}
 
EMPTY_WARDROBE = {"items": []}
 
  
def test_search_returns_results():
    """Basic search returns a non-empty list of dicts."""
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, dict) for r in results)
 
 
def test_search_empty_results():
    """Impossible query returns [] without raising an exception."""
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []
 
 
def test_search_price_filter():
    """All returned listings respect the max_price ceiling."""
    results = search_listings("jacket", size=None, max_price=30)
    assert all(item["price"] <= 30 for item in results)
 
 
def test_search_size_filter():
    """Size filter is applied (case-insensitive, loose match)."""
    results = search_listings("tee", size="M", max_price=None)
    # Every result should contain "m" somewhere in its size string
    assert all("m" in item["size"].lower() for item in results)
 
 
def test_search_no_size_or_price():
    """Search with no filters returns results based on keywords alone."""
    results = search_listings("vintage", size=None, max_price=None)
    assert isinstance(results, list)
    assert len(results) > 0
 
 
def test_search_max_five_results():
    """Never returns more than 5 results."""
    results = search_listings("vintage", size=None, max_price=None)
    assert len(results) <= 5
 
 
def test_search_result_has_required_fields():
    """Each result includes all expected listing fields."""
    results = search_listings("tee", size=None, max_price=50)
    required = {"id", "title", "description", "category", "style_tags",
                "size", "condition", "price", "colors", "brand", "platform"}
    for item in results:
        assert required.issubset(item.keys())
 
 
#for suggestions 
def _mock_groq_response(text: str):
    """Return a mock Groq client whose .chat.completions.create() returns text."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = text
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client
 
 
@patch("tools._get_groq_client")
def test_suggest_outfit_with_wardrobe(mock_get_client):
    """suggest_outfit returns a non-empty string when wardrobe has items."""
    mock_get_client.return_value = _mock_groq_response(
        "Pair the tee with your baggy jeans and chunky white sneakers."
    )
    result = suggest_outfit(SAMPLE_ITEM, EXAMPLE_WARDROBE)
    assert isinstance(result, str)
    assert len(result) > 0
 
 
@patch("tools._get_groq_client")
def test_suggest_outfit_empty_wardrobe(mock_get_client):
    """suggest_outfit returns general styling advice when wardrobe is empty."""
    mock_get_client.return_value = _mock_groq_response(
        "This tee pairs well with baggy jeans and chunky sneakers for a 90s grunge look."
    )
    result = suggest_outfit(SAMPLE_ITEM, EMPTY_WARDROBE)
    assert isinstance(result, str)
    assert len(result) > 0
 
 
@patch("tools._get_groq_client")
def test_suggest_outfit_empty_wardrobe_uses_general_prompt(mock_get_client):
    """When wardrobe is empty, the LLM is still called (not skipped)."""
    mock_client = _mock_groq_response("General styling advice here.")
    mock_get_client.return_value = mock_client
    suggest_outfit(SAMPLE_ITEM, EMPTY_WARDROBE)
    assert mock_client.chat.completions.create.called
 
 
# ── create_fit_card tests ─────────────────────────────────────────────────────
 
@patch("tools._get_groq_client")
def test_create_fit_card_returns_string(mock_get_client):
    """create_fit_card returns a non-empty string given valid inputs."""
    mock_get_client.return_value = _mock_groq_response(
        "Thrifted this bootleg tee off depop for $24 and it was made for my baggy jeans."
    )
    outfit = "Wear the tee with baggy jeans and chunky white sneakers."
    result = create_fit_card(outfit, SAMPLE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0
 
 
def test_create_fit_card_empty_outfit():
    """create_fit_card returns an error string (not an exception) for empty outfit."""
    result = create_fit_card("", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower()
 
 
def test_create_fit_card_whitespace_outfit():
    """create_fit_card treats whitespace-only outfit as empty."""
    result = create_fit_card("   ", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower()
 
 
@patch("tools._get_groq_client")
def test_create_fit_card_does_not_raise(mock_get_client):
    """create_fit_card never raises an exception under normal conditions."""
    mock_get_client.return_value = _mock_groq_response("Great caption here.")
    try:
        create_fit_card("Some outfit description.", SAMPLE_ITEM)
    except Exception as e:
        pytest.fail(f"create_fit_card raised unexpectedly: {e}")
 