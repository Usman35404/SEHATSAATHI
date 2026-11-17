"""
SehatSaathi AI — Flask Web Application & API Server.

Provides bilingual (English / Urdu) public-health literacy explanations and
comprehension checks grounded in curated public facts from content/topics.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

import ai_service
from ai_service import AIServiceError, SUPPORTED_LANGUAGES


BASE_DIR = Path(__file__).resolve().parent
TOPICS_FILE = BASE_DIR / "content" / "topics.json"


def load_topics_catalog(path: Path = TOPICS_FILE) -> list[dict[str, Any]]:
    """Load and validate the curated public-health topics catalog from disk."""
    if not path.exists():
        raise RuntimeError("Curated topics catalog is missing.")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Topics catalog must be a list with at least two topics.")

    required_keys = {
        "id",
        "title_en",
        "title_ur",
        "summary_en",
        "source_title",
        "source_url",
        "last_reviewed",
        "facts",
    }
    for item in data:
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            raise ValueError("Invalid topic entry in topics catalog.")
        if not isinstance(item["facts"], list) or len(item["facts"]) == 0:
            raise ValueError(f"Topic '{item.get('id')}' must include non-empty facts.")
        if not str(item["source_url"]).startswith("https://"):
            raise ValueError(f"Topic '{item.get('id')}' must have an HTTPS source_url.")

    return data


def get_topic_by_id(topic_id: str, catalog: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    """Look up an allowlisted topic strictly by its ID."""
    if not isinstance(topic_id, str) or not topic_id.strip():
        return None
    topics = catalog if catalog is not None else load_topics_catalog()
    normalized = topic_id.strip().lower()
    for topic in topics:
        if topic.get("id") == normalized:
            return topic
    return None


def summarize_topic_for_client(topic: dict[str, Any]) -> dict[str, Any]:
    """Return safe public summary metadata for a topic card."""
    return {
        "id": topic["id"],
        "title_en": topic["title_en"],
        "title_ur": topic["title_ur"],
        "summary_en": topic["summary_en"],
        "summary_ur": topic.get("summary_ur", ""),
        "source_title": topic["source_title"],
        "source_url": topic["source_url"],
        "last_reviewed": topic["last_reviewed"],
        "scope_boundary": topic.get("scope_boundary", "General health education only."),
    }


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Application factory for SehatSaathi AI."""
    # Anchor configuration to the checkout, including BOM-prefixed Windows files.
    # Exported variables take precedence; tests can disable dotenv entirely.
    load_dotenv(BASE_DIR / ".env", encoding="utf-8-sig", override=False)
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    if test_config:
        app.config.update(test_config)

    @app.cli.command("list-gemini-models")
    def list_gemini_models():
        """List current generateContent model IDs from the official Gemini API."""
        try:
            for name in ai_service.list_generation_models():
                click.echo(name)
        except AIServiceError as exc:
            raise click.ClickException(f"{exc.code}: {exc.message}") from None

    def _error_response(code: str, message: str, status: int):
        return jsonify({"error": {"code": code, "message": message}, "live_ai": False}), status

    @app.route("/", methods=["GET"])
    def index():
        try:
            topics = [summarize_topic_for_client(t) for t in load_topics_catalog()]
        except Exception:
            topics = []
        return render_template("index.html", initial_topics=topics)

    @app.route("/api/health", methods=["GET"])
    def api_health():
        """Safe readiness check that never exposes keys, paths, or private config."""
        return jsonify(
            {
                "app": "ok",
                "ai_configured": ai_service.is_ai_configured(),
            }
        ), 200

    @app.route("/api/topics", methods=["GET"])
    def api_topics():
        """Return the allowlisted public-health educational topics."""
        try:
            topics = [summarize_topic_for_client(t) for t in load_topics_catalog()]
            return jsonify({"topics": topics}), 200
        except Exception:
            return _error_response(
                "TOPICS_LOAD_ERROR",
                "Unable to load educational topics right now.",
                500,
            )

    @app.route("/api/explain", methods=["POST"])
    def api_explain():
        """Generate a live, source-grounded AI explanation and quiz for an approved topic."""
        if not request.is_json:
            return _error_response(
                "INVALID_JSON",
                "Request body must be valid JSON.",
                400,
            )

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error_response(
                "INVALID_JSON",
                "Request body must be a JSON object with 'topic_id' and 'language'.",
                400,
            )

        topic_id = payload.get("topic_id")
        language = payload.get("language")

        if not isinstance(topic_id, str) or not topic_id.strip():
            return _error_response(
                "MISSING_TOPIC",
                "Please select an approved health-literacy topic.",
                400,
            )

        if not isinstance(language, str) or language.strip() not in SUPPORTED_LANGUAGES:
            return _error_response(
                "INVALID_LANGUAGE",
                "Please choose a supported language: 'en' (English) or 'ur' (Urdu).",
                400,
            )

        try:
            topic = get_topic_by_id(topic_id)
        except Exception:
            return _error_response(
                "TOPICS_LOAD_ERROR",
                "Unable to read the curated topics catalog.",
                500,
            )

        if topic is None:
            return _error_response(
                "UNKNOWN_TOPIC",
                "Selected topic is not in the approved public-health catalog.",
                400,
            )

        try:
            result = ai_service.generate_topic_explanation(
                topic=topic,
                language=language.strip(),
            )
            return jsonify(result), 200
        except AIServiceError as exc:
            return _error_response(exc.code, exc.message, exc.status_code)
        except Exception:
            return _error_response(
                "AI_UNAVAILABLE",
                "Live AI couldn't respond right now. Please try again.",
                503,
            )

    @app.route("/api/ask", methods=["POST"])
    def api_ask():
        """Answer a constrained follow-up educational question grounded in the selected topic's facts."""
        if not request.is_json:
            return _error_response(
                "INVALID_JSON",
                "Request body must be valid JSON.",
                400,
            )

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error_response(
                "INVALID_JSON",
                "Request body must be a JSON object.",
                400,
            )

        topic_id = payload.get("topic_id")
        language = payload.get("language")
        question = payload.get("question")

        if not isinstance(topic_id, str) or not topic_id.strip():
            return _error_response(
                "MISSING_TOPIC",
                "Please select an approved health-literacy topic first.",
                400,
            )

        if not isinstance(language, str) or language.strip() not in SUPPORTED_LANGUAGES:
            return _error_response(
                "INVALID_LANGUAGE",
                "Please choose a supported language: 'en' (English) or 'ur' (Urdu).",
                400,
            )

        if not isinstance(question, str) or not question.strip():
            return _error_response(
                "INVALID_QUESTION",
                "Please enter a question about the selected topic.",
                400,
            )

        topic = get_topic_by_id(topic_id)
        if topic is None:
            return _error_response(
                "UNKNOWN_TOPIC",
                "Selected topic is not in the approved public-health catalog.",
                400,
            )

        try:
            result = ai_service.answer_topic_followup(
                topic=topic,
                language=language.strip(),
                question=question,
            )
            return jsonify(result), 200
        except AIServiceError as exc:
            return _error_response(exc.code, exc.message, exc.status_code)
        except Exception:
            return _error_response(
                "AI_UNAVAILABLE",
                "Live AI couldn't answer right now. Please try again.",
                503,
            )

    return app


app = create_app()

if __name__ == "__main__":
    debug_flag = os.environ.get("FLASK_DEBUG", "false").strip().lower() == "true"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=debug_flag)
