"""
Unit tests for ai_service.py (validation, safety boundaries, and provider error paths).
Mocks are used strictly inside unit tests and never in production routes.
"""

import json
import pytest
from types import SimpleNamespace

import ai_service
from ai_service import (
    AIServiceError,
    answer_topic_followup,
    check_question_safety_boundary,
    generate_topic_explanation,
    validate_explanation_payload,
)
from app import get_topic_by_id


@pytest.fixture(autouse=True)
def configured_model(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "test-text-model")


class _FakeResponse:
    def __init__(self, text: str):
        self.text = text


class _FakeModels:
    def __init__(self, response_text: str | None = None, exc: Exception | None = None):
        self._text = response_text
        self._exc = exc

    def get(self, **kwargs):
        return SimpleNamespace(supported_actions=["generateContent"])

    def generate_content(self, **kwargs):
        if self._exc:
            raise self._exc
        return _FakeResponse(self._text)


class _FakeClient:
    def __init__(self, response_text: str | None = None, exc: Exception | None = None):
        self.models = _FakeModels(response_text=response_text, exc=exc)


def test_missing_api_key_raises_safe_503(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    topic = get_topic_by_id("handwashing")
    with pytest.raises(AIServiceError) as exc_info:
        generate_topic_explanation(topic, "en")
    assert exc_info.value.code == "AI_NOT_CONFIGURED"
    assert exc_info.value.status_code == 503


def test_placeholder_api_key_treated_as_unconfigured(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "replace_with_your_own_key_locally")
    assert ai_service.is_ai_configured() is False


def test_valid_explanation_response_parsed_and_source_attached_from_local_catalog(monkeypatch):
    valid_model_json = json.dumps(
        {
            "explanation": "Washing hands with soap and clean running water for at least 20 seconds removes germs effectively.",
            "key_points": [
                "Wet hands with clean water and apply soap.",
                "Lather and scrub for at least 20 seconds.",
                "Rinse well and dry with a clean towel.",
            ],
            "quiz": {
                "question": "How long should you scrub your hands with soap?",
                "options": [
                    "At least 5 seconds",
                    "At least 20 seconds",
                    "Only when visibly dirty",
                ],
                "correct_index": 1,
                "feedback": "CDC guidance recommends scrubbing hands with soap for at least 20 seconds.",
            },
            "source": {
                "title": "Hallucinated AI Source",
                "url": "https://hallucinated.example.com",
            },
        }
    )

    monkeypatch.setattr(ai_service, "_get_genai_client", lambda: _FakeClient(response_text=valid_model_json))
    topic = get_topic_by_id("handwashing")
    result = generate_topic_explanation(topic, "en")

    assert result["live_ai"] is True
    assert result["topic_id"] == "handwashing"
    assert result["language"] == "en"
    assert len(result["key_points"]) == 3
    assert result["quiz"]["correct_index"] == 1
    # Verify source URL comes strictly from curated local catalog, ignoring model's source field
    assert result["source"]["url"] == "https://www.cdc.gov/clean-hands/about/"
    assert result["source"]["title"] == "CDC — About Handwashing"


def test_malformed_json_from_provider_raises_502(monkeypatch):
    monkeypatch.setattr(ai_service, "_get_genai_client", lambda: _FakeClient(response_text="NOT VALID JSON"))
    topic = get_topic_by_id("sleep")
    with pytest.raises(AIServiceError) as exc_info:
        generate_topic_explanation(topic, "ur")
    assert exc_info.value.code == "AI_INVALID_OUTPUT"
    assert exc_info.value.status_code == 502


def test_invalid_quiz_schema_rejected():
    topic = get_topic_by_id("handwashing")
    bad_payload = {
        "explanation": "This is a sufficiently long explanation about washing hands properly.",
        "key_points": ["Point one is valid", "Point two is valid", "Point three is valid"],
        "quiz": {
            "question": "Valid question text?",
            "options": ["Only two options", "Option B"],
            "correct_index": 5,
            "feedback": "Valid feedback string.",
        },
    }
    with pytest.raises(AIServiceError) as exc_info:
        validate_explanation_payload(bad_payload, topic, "en")
    assert exc_info.value.code == "AI_INVALID_OUTPUT"


def test_provider_exception_raises_safe_503(monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "_get_genai_client",
        lambda: _FakeClient(exc=RuntimeError("Upstream timeout")),
    )
    topic = get_topic_by_id("sleep")
    with pytest.raises(AIServiceError) as exc_info:
        generate_topic_explanation(topic, "en")
    assert exc_info.value.code == "AI_UNAVAILABLE"
    assert exc_info.value.status_code == 503


def test_safety_boundary_blocks_diagnosis_and_emergency_without_calling_ai(monkeypatch):
    # Even if AI is unconfigured, local boundary should intercept clinical/emergency queries safely
    monkeypatch.setenv("GEMINI_API_KEY", "")
    topic = get_topic_by_id("sleep")

    diag_res = answer_topic_followup(topic, "en", "Can you diagnose my insomnia and prescribe sleeping pills?")
    assert diag_res["boundary_triggered"] is True
    assert diag_res["boundary_type"] == "clinical_scope"
    assert diag_res["live_ai"] is False

    emerg_res = answer_topic_followup(topic, "ur", "مجھے شدید سینے میں درد اور سانس نہیں آ رہا")
    assert emerg_res["boundary_triggered"] is True
    assert emerg_res["boundary_type"] == "emergency"
    assert emerg_res["live_ai"] is False

    assert check_question_safety_boundary("How many hours of sleep do adults need?", "en") is None
