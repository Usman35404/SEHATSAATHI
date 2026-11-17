"""
SehatSaathi AI — Gemini AI Service Layer (Server-Side Only).

Grounds educational explanations and comprehension quizzes strictly in curated
public-health facts from content/topics.json using the official google-genai SDK.
Never fabricates or simulates live AI responses.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from google import genai
from google.genai import errors, types


SUPPORTED_LANGUAGES = {"en": "English", "ur": "Urdu (اردو)"}
MAX_QUESTION_LENGTH = 280
MAX_AUDIO_BYTES = 2 * 1024 * 1024
ALLOWED_AUDIO_MIMES = {"audio/webm", "audio/ogg", "audio/wav", "audio/mp4", "audio/mpeg"}
DEFAULT_TIMEOUT_MS = 30000
# Provider statuses where trying another *real* configured model is reasonable.
_FALLBACK_STATUSES = {500, 502, 503, 504}


def _request_timeout_ms() -> int:
    """Per-request timeout so a slow provider never leaves the UI spinning forever."""
    raw = os.environ.get("GEMINI_TIMEOUT_MS", "").strip()
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_MS
    return min(max(value, 5000), 120000)


def get_fallback_model_names() -> list[str]:
    """Optional comma-separated GEMINI_FALLBACK_MODELS; empty by default (no fallback)."""
    raw = os.environ.get("GEMINI_FALLBACK_MODELS", "")
    return [name.strip() for name in raw.split(",") if name.strip()]


class AIServiceError(Exception):
    """Structured exception for safe client-facing error reporting."""

    def __init__(self, code: str, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


# Patterns indicating emergency, personal diagnosis, prescription/dosage, or private records
_EMERGENCY_PATTERNS = re.compile(
    r"\b(chest pain|can'?t breathe|difficulty breathing|unconscious|stroke|heart attack|"
    r"severe bleeding|suicide|self[- ]harm|overdose|poisoning|seizure|emergency)\b|"
    r"(سانس نہیں|شدید درد|بے ہوش|ہارٹ اٹیک|خودکشی|ایمرجنسی)",
    re.IGNORECASE,
)

_CLINICAL_BOUNDARY_PATTERNS = re.compile(
    r"\b(diagnos(e|is)|prescri(be|ption)|dosage|what medicine|which medicine|"
    r"what pill|antibiotic|sleeping pill|melatonin dose|mg\b|tablet|my lab report|"
    r"my blood test|my x-?ray|my mri|do i have|am i suffering from|cure my|treat my)\b|"
    r"(تشخیص|کون سی دوا|نسخہ|خوراک|میری رپورٹ|ٹیسٹ رپورٹ|علاج بتائیں)",
    re.IGNORECASE,
)

_PII_PATTERNS = re.compile(
    r"\b(\d{5}-\d{7}-\d|\+?\d{10,13}|patient id|mrn|cnic)\b",
    re.IGNORECASE,
)


def is_ai_configured() -> bool:
    """Return True if a plausible GEMINI_API_KEY is present in the environment."""
    raw_key = os.environ.get("GEMINI_API_KEY", "").strip()
    placeholder = raw_key.lower()
    if (not raw_key or placeholder.startswith(("replace_with_", "your_", "<"))
            or any(char.isspace() for char in raw_key)):
        return False
    return True


def get_configured_model_name() -> str:
    """Require an explicit model ID discovered for the configured account."""
    raw_model = os.environ.get("GEMINI_MODEL", "").strip()
    if not raw_model or raw_model.lower().startswith("replace_with_"):
        raise AIServiceError(
            "AI_MODEL_NOT_CONFIGURED",
            "Set GEMINI_MODEL to a generateContent model returned by "
            "'flask --app app list-gemini-models', then restart the server.",
        )
    return raw_model


def check_question_safety_boundary(question: str, language: str) -> dict[str, Any] | None:
    """
    Local safety gate for follow-up questions before calling the model.
    Returns a boundary response dict if the input asks for emergency care,
    personal diagnosis/prescriptions, or includes PII; otherwise returns None.
    """
    text = question.strip()
    if _EMERGENCY_PATTERNS.search(text):
        if language == "ur":
            msg = (
                "یہ ایک ہنگامی طبی صورتحال ہو سکتی ہے۔ صحت ساتھی اے آئی صرف عمومی تعلیمی معلومات فراہم کرتا ہے۔ "
                "براہِ کرم فوری طور پر قریبی ایمرجنسی طبی امداد (جیسے 1122) یا مستند ڈاکٹر سے رابطہ کریں۔"
            )
        else:
            msg = (
                "This sounds like a potential medical emergency. SehatSaathi AI provides general health education only "
                "and cannot handle emergencies. Please contact local emergency services (such as 1122) or seek immediate medical care."
            )
        return {"boundary_triggered": True, "boundary_type": "emergency", "answer": msg}

    if _PII_PATTERNS.search(text):
        if language == "ur":
            msg = (
                "براہِ کرم ذاتی شناختی معلومات، فون نمبر یا نجی طبی ریکارڈ شیئر نہ کریں۔ "
                "یہ ایپ صرف منتخب موضوع کے بارے میں عمومی تعلیمی سوالات کا جواب دیتی ہے۔"
            )
        else:
            msg = (
                "Please do not share personal identifiers, phone numbers, or private medical records. "
                "SehatSaathi AI only answers general educational questions about the selected topic."
            )
        return {"boundary_triggered": True, "boundary_type": "privacy", "answer": msg}

    if _CLINICAL_BOUNDARY_PATTERNS.search(text):
        if language == "ur":
            msg = (
                "صحت ساتھی اے آئی صرف عمومی صحت کی آگاہی اور تعلیم کے لیے ہے—یہ بیماری کی تشخیص، دوا یا نسخہ تجویز نہیں کرتا۔ "
                "ذاتی طبی مشورے یا علامات کے لیے براہِ کرم مستند ڈاکٹر سے رجوع کریں۔"
            )
        else:
            msg = (
                "SehatSaathi AI provides general health education only—it does not diagnose conditions, interpret test results, "
                "or recommend medications or dosages. Please consult a qualified healthcare professional for personal medical advice."
            )
        return {"boundary_triggered": True, "boundary_type": "clinical_scope", "answer": msg}

    return None


def _get_genai_client() -> genai.Client:
    """Initialize and return a Google GenAI client using server-side environment credentials."""
    if not is_ai_configured():
        raise AIServiceError(
            code="AI_NOT_CONFIGURED",
            message=(
                "Live AI is not configured on this server yet. Please set a valid GEMINI_API_KEY "
                "in your private local .env file or environment settings and restart the server."
            ),
            status_code=503,
        )
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    # This application uses the Gemini Developer API, not ambient Vertex settings.
    try:
        return genai.Client(
            api_key=api_key,
            vertexai=False,
            http_options=types.HttpOptions(timeout=_request_timeout_ms()),
        )
    except errors.APIError as exc:
        raise _provider_error(exc) from None
    except Exception:
        raise AIServiceError("AI_UNAVAILABLE", "Could not initialize the Gemini client. Check server configuration.") from None


def _provider_error(exc: errors.APIError) -> AIServiceError:
    """Map only status/reason codes; never expose provider messages or URLs."""
    details = exc.details if isinstance(exc.details, dict) else {}
    error = details.get("error", details)
    entries = error.get("details", []) if isinstance(error, dict) else []
    reasons = {item.get("reason") for item in entries if isinstance(item, dict)} if isinstance(entries, list) else set()
    if exc.code == 401 or reasons & {"API_KEY_INVALID", "API_KEY_EXPIRED"}:
        return AIServiceError("AI_AUTH_FAILED", "Gemini rejected the API key. Check the private key configuration and restart the server.")
    if exc.code == 403:
        return AIServiceError("AI_ACCESS_DENIED", "Gemini access was denied. Check API enablement, key restrictions, account permissions, and region availability.")
    if exc.code == 404:
        return AIServiceError("AI_MODEL_UNAVAILABLE", "The configured Gemini model is unavailable. Run 'flask --app app list-gemini-models' and update GEMINI_MODEL.")
    if exc.code == 429:
        return AIServiceError("AI_RATE_LIMITED", "Gemini rate limit or quota was exceeded. Check account quota and billing before retrying.")
    if exc.code == 400:
        return AIServiceError("AI_REQUEST_REJECTED", "Gemini rejected the request. Check the selected model supports JSON output and the requested generation settings.")
    return AIServiceError("AI_UNAVAILABLE", "Gemini is temporarily unavailable. Check connectivity and try again later.")


def _verify_generation_model(client: genai.Client, model_name: str) -> None:
    """Check current provider metadata instead of maintaining a model allowlist."""
    model = client.models.get(model=model_name)
    if "generateContent" not in (model.supported_actions or []):
        raise AIServiceError("AI_MODEL_UNSUPPORTED", "GEMINI_MODEL does not support generateContent. Choose a model from 'flask --app app list-gemini-models'.")


def _live_generate(contents: str, config: types.GenerateContentConfig, unavailable_message: str) -> tuple[Any, str]:
    """
    Make a genuine live Gemini call with the configured model. If the provider is
    overloaded or times out and GEMINI_FALLBACK_MODELS is set, try those real
    models next. Returns (response, model_used). Never fabricates output.
    """
    client = _get_genai_client()
    chain = [get_configured_model_name()]
    for name in get_fallback_model_names():
        if name not in chain:
            chain.append(name)

    for idx, model_name in enumerate(chain):
        has_next = idx < len(chain) - 1
        try:
            _verify_generation_model(client, model_name)
            response = client.models.generate_content(model=model_name, contents=contents, config=config)
            return response, model_name
        except AIServiceError:
            raise
        except errors.APIError as exc:
            print(f"[ai_service] model={model_name} provider_status={exc.code}")
            if has_next and exc.code in _FALLBACK_STATUSES:
                continue
            raise _provider_error(exc) from None
        except Exception as exc:  # network timeout etc.; log only a safe category
            print(f"[ai_service] model={model_name} failure={type(exc).__name__}")
            if has_next:
                continue
            raise AIServiceError("AI_UNAVAILABLE", unavailable_message, 503) from None
    raise AIServiceError("AI_UNAVAILABLE", unavailable_message, 503)


def list_generation_models() -> list[str]:
    """Use the official paginated Models API without requiring a selected model."""
    client = _get_genai_client()
    try:
        return [model.name for model in client.models.list()
                if model.name and "generateContent" in (model.supported_actions or [])]
    except errors.APIError as exc:
        raise _provider_error(exc) from None
    except Exception:
        raise AIServiceError("AI_UNAVAILABLE", "Could not list Gemini models. Check connectivity and try again.") from None


def _extract_json_object(raw_text: str) -> dict[str, Any]:
    """Safely parse a JSON object from model output, stripping markdown fences if present."""
    if not raw_text or not isinstance(raw_text, str):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI service returned an empty response. Please try again.",
            status_code=502,
        )
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI service returned a response in an unexpected format. Please try again.",
            status_code=502,
        ) from exc

    if not isinstance(parsed, dict):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI service output was not a structured object. Please try again.",
            status_code=502,
        )
    return parsed


def validate_explanation_payload(
    raw_data: dict[str, Any],
    topic: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    """
    Strictly validate the AI-generated explanation and quiz schema,
    and attach trusted source provenance directly from topics.json.
    """
    explanation = raw_data.get("explanation")
    if not isinstance(explanation, str) or len(explanation.strip()) < 20:
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI response did not contain a valid explanation. Please try again.",
            status_code=502,
        )

    key_points = raw_data.get("key_points")
    if isinstance(key_points, list) and len(key_points) > 3:
        # Keep the first three genuine model-generated points (no content is invented).
        key_points = key_points[:3]
    if (
        not isinstance(key_points, list)
        or len(key_points) != 3
        or not all(isinstance(pt, str) and len(pt.strip()) >= 5 for pt in key_points)
    ):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI response did not include exactly 3 valid key points. Please try again.",
            status_code=502,
        )

    quiz = raw_data.get("quiz")
    if not isinstance(quiz, dict):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI response did not include a valid comprehension quiz. Please try again.",
            status_code=502,
        )

    question = quiz.get("question")
    options = quiz.get("options")
    correct_index = quiz.get("correct_index")
    feedback = quiz.get("feedback")

    if not isinstance(question, str) or len(question.strip()) < 8:
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI quiz question was missing or invalid. Please try again.",
            status_code=502,
        )

    if (
        not isinstance(options, list)
        or len(options) != 3
        or not all(isinstance(opt, str) and len(opt.strip()) >= 1 for opt in options)
    ):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI quiz must include exactly 3 answer choices. Please try again.",
            status_code=502,
        )

    if isinstance(correct_index, bool) or not isinstance(correct_index, int) or correct_index not in (0, 1, 2):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI quiz correct answer index was invalid. Please try again.",
            status_code=502,
        )

    if not isinstance(feedback, str) or len(feedback.strip()) < 8:
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI quiz feedback was missing or invalid. Please try again.",
            status_code=502,
        )

    return {
        "topic_id": topic["id"],
        "topic_title": topic["title_ur"] if language == "ur" else topic["title_en"],
        "language": language,
        "explanation": explanation.strip(),
        "key_points": [pt.strip() for pt in key_points],
        "quiz": {
            "question": question.strip(),
            "options": [opt.strip() for opt in options],
            "correct_index": correct_index,
            "feedback": feedback.strip(),
        },
        "source": {
            "title": topic["source_title"],
            "url": topic["source_url"],
            "last_reviewed": topic.get("last_reviewed", "2026-11-17"),
        },
        "live_ai": True,
    }


def _explanation_schema() -> types.Schema:
    """Structured-output schema so Gemini returns exactly the shape we validate."""
    text = types.Schema(type=types.Type.STRING)
    return types.Schema(
        type=types.Type.OBJECT,
        required=["explanation", "key_points", "quiz"],
        properties={
            "explanation": text,
            "key_points": types.Schema(type=types.Type.ARRAY, items=text, min_items=3, max_items=3),
            "quiz": types.Schema(
                type=types.Type.OBJECT,
                required=["question", "options", "correct_index", "feedback"],
                properties={
                    "question": text,
                    "options": types.Schema(type=types.Type.ARRAY, items=text, min_items=3, max_items=3),
                    "correct_index": types.Schema(type=types.Type.INTEGER),
                    "feedback": text,
                },
            ),
        },
    )


def generate_topic_explanation(topic: dict[str, Any], language: str) -> dict[str, Any]:
    """
    Call Gemini live to produce a plain-language educational explanation and 3-option
    comprehension quiz grounded exclusively in the curated topic facts.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise AIServiceError(
            code="INVALID_LANGUAGE",
            message="Unsupported language requested. Choose 'en' (English) or 'ur' (Urdu).",
            status_code=400,
        )

    facts_bulleted = "\n".join(f"- {fact}" for fact in topic.get("facts", []))
    lang_label = SUPPORTED_LANGUAGES[language]
    lang_instruction = (
        "Write all user-facing strings (explanation, key_points, quiz question, quiz options, and quiz feedback) "
        "in clear, natural, easy-to-understand Urdu script (اردو) suitable for everyday readers. Avoid overly dense clinical jargon."
        if language == "ur"
        else "Write all user-facing strings (explanation, key_points, quiz question, quiz options, and quiz feedback) "
        "in clear, friendly, plain English suitable for everyday readers. Avoid unnecessary medical jargon."
    )

    system_instruction = (
        "You are the educational content engine for SehatSaathi AI, a public-health literacy web tool. "
        "STRICT RULES:\n"
        "1. Use ONLY the provided curated public-health facts. Do not invent statistics, clinical claims, medications, or external URLs.\n"
        "2. Do NOT diagnose illness, recommend treatments/prescriptions, or give personalized medical advice.\n"
        "3. Do NOT include raw HTML tags, markdown links, or external URLs inside your text.\n"
        "4. Return ONLY valid JSON matching the requested schema:\n"
        "{\n"
        '  "explanation": "2 to 4 clear, warm educational sentences summarizing the topic",\n'
        '  "key_points": ["point 1", "point 2", "point 3"]  (EXACTLY three short points),\n'
        '  "quiz": {\n'
        '    "question": "one comprehension question testing understanding of the explanation",\n'
        '    "options": ["option A", "option B", "option C"],\n'
        '    "correct_index": 0,\n'
        '    "feedback": "1 to 2 sentences explaining why the correct answer is right based on the facts"\n'
        "  }\n"
        "}"
    )

    user_prompt = (
        f"Topic ID: {topic['id']}\n"
        f"Topic Title (English): {topic['title_en']}\n"
        f"Topic Title (Urdu): {topic['title_ur']}\n"
        f"Target Output Language: {lang_label}\n"
        f"Language Requirement: {lang_instruction}\n"
        f"Scope Boundary: {topic.get('scope_boundary', 'General health education only.')}\n\n"
        f"Approved Source Facts (use ONLY these facts):\n{facts_bulleted}\n"
    )

    try:
        response, model_used = _live_generate(
            user_prompt,
            types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=_explanation_schema(),
                temperature=0.2,
                max_output_tokens=4096,
            ),
            "Gemini is busy or didn't respond in time. Please press Try Again in a few seconds.",
        )
    except AIServiceError:
        raise
    except Exception as exc:
        raise AIServiceError(
            code="AI_UNAVAILABLE",
            message="Live AI couldn't respond right now. Please check your connection or API quota and try again.",
            status_code=503,
        ) from exc

    raw_text = getattr(response, "text", None)
    parsed = _extract_json_object(raw_text)
    result = validate_explanation_payload(parsed, topic=topic, language=language)
    result["model"] = model_used
    return result


def answer_topic_followup(
    topic: dict[str, Any],
    language: str,
    question: str,
    catalog: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Answer a single constrained educational question strictly grounded
    in the selected topic's curated facts (or across the curated catalog if provided).
    """
    if language not in SUPPORTED_LANGUAGES:
        raise AIServiceError(
            code="INVALID_LANGUAGE",
            message="Unsupported language requested. Choose 'en' (English) or 'ur' (Urdu).",
            status_code=400,
        )

    cleaned_q = (question or "").strip()
    if not cleaned_q:
        raise AIServiceError(
            code="INVALID_QUESTION",
            message="Please enter a short question about the selected topic.",
            status_code=400,
        )
    if len(cleaned_q) > MAX_QUESTION_LENGTH:
        raise AIServiceError(
            code="QUESTION_TOO_LONG",
            message=f"Please keep your question under {MAX_QUESTION_LENGTH} characters.",
            status_code=400,
        )

    # Check local clinical/emergency/privacy safety boundary first without sending sensitive text to AI
    boundary = check_question_safety_boundary(cleaned_q, language=language)
    if boundary is not None:
        return {
            "topic_id": topic["id"],
            "language": language,
            "question": cleaned_q,
            "answer": boundary["answer"],
            "supported_by_source": False,
            "boundary_triggered": True,
            "boundary_type": boundary["boundary_type"],
            "source": {
                "title": topic["source_title"],
                "url": topic["source_url"],
            },
            "live_ai": False,
        }

    topics_for_context = catalog if catalog else [topic]
    context_blocks = []
    for item in topics_for_context:
        item_facts = "\n".join(f"  - {fact}" for fact in item.get("facts", []))
        context_blocks.append(
            f"[Topic ID: {item['id']} | {item['title_en']} ({item['title_ur']}) | Source: {item['source_title']}]\n{item_facts}"
        )
    facts_bulleted = "\n\n".join(context_blocks)
    lang_label = SUPPORTED_LANGUAGES[language]

    system_instruction = (
        "You are the bilingual educational health-literacy assistant for SehatSaathi AI (UN SDG 3). "
        "Your goal is to explain everyday health concepts in clear, simple, plain language (English or Urdu).\n"
        "STRICT RULES:\n"
        "1. If the user's question is covered by the Approved Source Facts below, answer it directly using those facts and set supported_by_source to true.\n"
        "2. If the user asks a general educational health-literacy question outside those facts (for example: 'What is blood pressure / بلڈ پریشر کیا ہے؟', 'What is balanced nutrition?', 'Why is fever a body response?'), provide a helpful, accurate, plain-language 2-3 sentence general educational explanation suitable for everyday learners, and set supported_by_source to false.\n"
        "3. NEVER diagnose personal symptoms, NEVER prescribe or recommend specific medications or dosages, and NEVER interpret personal lab reports. For personal medical concerns, gently remind the user that SehatSaathi AI is for general health education and they should consult a qualified doctor.\n"
        "4. Never invent statistics or external URLs.\n"
        "5. Return ONLY valid JSON with keys: {\"answer\": string, \"supported_by_source\": boolean}."
    )

    user_prompt = (
        f"Selected Topic: {topic['title_en']} ({topic['title_ur']})\n"
        f"Target Language: {lang_label}\n"
        f"Approved Source Facts:\n{facts_bulleted}\n\n"
        f"User Question: {cleaned_q}\n"
    )

    try:
        response, model_used = _live_generate(
            user_prompt,
            types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=2048,
            ),
            "Gemini is busy or didn't respond in time. Please try your question again in a few seconds.",
        )
    except AIServiceError:
        raise
    except Exception as exc:
        raise AIServiceError(
            code="AI_UNAVAILABLE",
            message="Live AI couldn't answer right now. Please try again in a moment.",
            status_code=503,
        ) from exc

    parsed = _extract_json_object(getattr(response, "text", None))
    answer_text = parsed.get("answer")
    supported = parsed.get("supported_by_source")

    if not isinstance(answer_text, str) or len(answer_text.strip()) < 5 or not isinstance(supported, bool):
        raise AIServiceError(
            code="AI_INVALID_OUTPUT",
            message="The AI service returned an incomplete follow-up answer. Please try again.",
            status_code=502,
        )

    return {
        "topic_id": topic["id"],
        "language": language,
        "question": cleaned_q,
        "answer": answer_text.strip(),
        "supported_by_source": supported,
        "boundary_triggered": False,
        "source": {
            "title": topic["source_title"],
            "url": topic["source_url"],
        },
        "model": model_used,
        "live_ai": True,
    }


def transcribe_audio_question(audio_bytes: bytes, mime_type: str, language: str) -> dict[str, Any]:
    """
    Transcribe short spoken question audio in-memory using Gemini when the browser's
    native SpeechRecognition service fails (e.g., 'network' error in Urdu mode).
    Audio is never written to disk or logged.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise AIServiceError(
            code="INVALID_LANGUAGE",
            message="Unsupported language requested. Choose 'en' (English) or 'ur' (Urdu).",
            status_code=400,
        )
    if not audio_bytes or len(audio_bytes) < 100:
        raise AIServiceError(
            code="INVALID_AUDIO",
            message="No speech audio was captured. Please hold/click the microphone and speak clearly.",
            status_code=400,
        )
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise AIServiceError(
            code="AUDIO_TOO_LARGE",
            message="Audio clip is too long. Please keep spoken questions under 15 seconds.",
            status_code=400,
        )

    base_mime = (mime_type or "audio/webm").split(";")[0].strip().lower()
    if base_mime not in ALLOWED_AUDIO_MIMES:
        base_mime = "audio/webm"

    lang_hint = (
        "Transcribe the spoken audio into Urdu script (اردو). If the speaker used English words, you may keep or transliterate them naturally."
        if language == "ur"
        else "Transcribe the spoken audio into plain English."
    )
    prompt = (
        f"{lang_hint} Return ONLY valid JSON with a single key {{\"transcript\": \"...\"}} "
        "containing the exact spoken question (or empty string if only silence/noise)."
    )

    client = _get_genai_client()
    model_name = get_configured_model_name()
    try:
        _verify_generation_model(client, model_name)
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=base_mime),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
                max_output_tokens=256,
            ),
        )
    except AIServiceError:
        raise
    except errors.APIError as exc:
        raise _provider_error(exc) from None
    except Exception as exc:
        raise AIServiceError(
            code="AI_UNAVAILABLE",
            message="Could not transcribe audio right now. Please try again or type your question.",
            status_code=503,
        ) from exc

    parsed = _extract_json_object(getattr(response, "text", None))
    transcript = str(parsed.get("transcript", "")).strip()[:MAX_QUESTION_LENGTH]
    return {"transcript": transcript, "language": language, "live_ai": True}
