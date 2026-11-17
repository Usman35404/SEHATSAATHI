"""
Flask route and contract tests for SehatSaathi AI.
"""

import ai_service
from ai_service import AIServiceError
from app import create_app


def _make_client():
    app = create_app({"TESTING": True})
    return app.test_client()


def test_home_page_renders_200_and_contains_required_elements():
    client = _make_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "SehatSaathi AI" in html
    assert "General health education — not diagnosis or treatment." in html
    assert "Proper Handwashing" in html
    assert "Healthy Sleep Basics" in html
    assert "Physical Activity Basics" in html
    assert "Water &amp; Healthy Hydration" in html or "Water & Healthy Hydration" in html
    assert "ہاتھ دھونے کا درست طریقہ" in html
    assert 'id="mic-btn"' in html
    assert 'id="followup-input"' in html


def test_health_endpoint_never_leaks_secrets(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "super_secret_do_not_expose_12345")
    client = _make_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "super_secret_do_not_expose_12345" not in body
    data = resp.get_json()
    assert data == {"app": "ok", "ai_configured": True}


def test_api_topics_returns_two_approved_topics():
    client = _make_client()
    resp = client.get("/api/topics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "topics" in data
    assert len(data["topics"]) >= 2
    ids = [t["id"] for t in data["topics"]]
    assert "handwashing" in ids
    assert "sleep" in ids


def test_api_explain_rejects_bad_inputs():
    client = _make_client()

    # Non-JSON
    resp = client.post("/api/explain", data="not json", content_type="text/plain")
    assert resp.status_code == 400
    assert resp.get_json()["live_ai"] is False

    # Unknown topic_id
    resp = client.post("/api/explain", json={"topic_id": "unknown", "language": "en"})
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "UNKNOWN_TOPIC"

    # Invalid language
    resp = client.post("/api/explain", json={"topic_id": "handwashing", "language": "fr"})
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "INVALID_LANGUAGE"


def test_api_explain_returns_validated_response_when_ai_succeeds(monkeypatch):
    def _mock_generate(topic, language):
        return {
            "topic_id": topic["id"],
            "topic_title": topic["title_ur"] if language == "ur" else topic["title_en"],
            "language": language,
            "explanation": "صابن اور صاف پانی سے کم از کم 20 سیکنڈ تک ہاتھ دھونا جراثیم سے بچاؤ کا بہترین طریقہ ہے۔",
            "key_points": ["پانی سے ہاتھ گیلے کریں", "20 سیکنڈ تک صابن ملیں", "صاف پانی سے دھو کر خشک کریں"],
            "quiz": {
                "question": "ہاتھوں کو کم از کم کتنے سیکنڈ تک صابن سے ملنا چاہیے؟",
                "options": ["5 سیکنڈ", "20 سیکنڈ", "60 سیکنڈ"],
                "correct_index": 1,
                "feedback": "سی ڈی سی کے مطابق کم از کم 20 سیکنڈ تک ہاتھ ملنا ضروری ہے۔",
            },
            "source": {
                "title": topic["source_title"],
                "url": topic["source_url"],
                "last_reviewed": topic["last_reviewed"],
            },
            "live_ai": True,
        }

    monkeypatch.setattr(ai_service, "generate_topic_explanation", _mock_generate)
    client = _make_client()
    resp = client.post("/api/explain", json={"topic_id": "handwashing", "language": "ur"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["live_ai"] is True
    assert data["language"] == "ur"
    assert data["source"]["url"] == "https://www.cdc.gov/clean-hands/about/"


def test_api_explain_returns_503_when_ai_unavailable(monkeypatch):
    def _mock_fail(topic, language):
        raise AIServiceError("AI_UNAVAILABLE", "Live AI is temporarily unavailable.", 503)

    monkeypatch.setattr(ai_service, "generate_topic_explanation", _mock_fail)
    client = _make_client()
    resp = client.post("/api/explain", json={"topic_id": "sleep", "language": "en"})
    assert resp.status_code == 503
    data = resp.get_json()
    assert data["live_ai"] is False
    assert data["error"]["code"] == "AI_UNAVAILABLE"


def test_api_ask_validation_and_clinical_boundary():
    client = _make_client()

    # Oversized question
    resp = client.post(
        "/api/ask",
        json={"topic_id": "handwashing", "language": "en", "question": "x" * 350},
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "QUESTION_TOO_LONG"

    # Clinical boundary intercepted safely
    resp = client.post(
        "/api/ask",
        json={
            "topic_id": "sleep",
            "language": "en",
            "question": "Please diagnose my sleep disorder and tell me what sleeping pill dosage to take.",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["boundary_triggered"] is True
    assert data["live_ai"] is False
