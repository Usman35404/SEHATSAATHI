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
from google.genai import types


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
SUPPORTED_LANGUAGES = {"en": "English", "ur": "Urdu (اردو)"}
MAX_QUESTION_LENGTH = 280


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
    if not raw_key or raw_key.startswith("replace_with_"):
        return False
    return True


def get_configured_model_name() -> str:
    """Return the configured Gemini model ID or a sensible default."""
    raw_model = os.environ.get("GEMINI_MODEL", "").strip()
    if not raw_model or raw_model.startswith("replace_with_"):
        return DEFAULT_GEMINI_MODEL
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
                "in your private local .env file and restart or retry."
            ),
            status_code=503,
        )
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    return genai.Client(api_key=api_key)


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

    client = _get_genai_client()
    model_name = get_configured_model_name()

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
        '  "key_points": ["point 1", "point 2", "point 3"],\n'
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
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=900,
            ),
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
    return validate_explanation_payload(parsed, topic=topic, language=language)


def answer_topic_followup(topic: dict[str, Any], language: str, question: str) -> dict[str, Any]:
    """
    Answer a single constrained follow-up educational question strictly grounded
    in the selected topic's curated facts.
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

    client = _get_genai_client()
    model_name = get_configured_model_name()

    facts_bulleted = "\n".join(f"- {fact}" for fact in topic.get("facts", []))
    lang_label = SUPPORTED_LANGUAGES[language]

    system_instruction = (
        "You are a constrained educational assistant for SehatSaathi AI. "
        "You may ONLY answer using the provided Approved Source Facts for the selected topic.\n"
        "STRICT RULES:\n"
        "1. If the user's question is answered by the Approved Source Facts, provide a concise, plain-language answer (2-3 sentences) in the requested language and set supported_by_source to true.\n"
        "2. If the user's question is NOT covered by the Approved Source Facts, or asks for personal medical advice, diagnosis, medications, or unrelated topics, politely state that the current learning material for this topic does not cover that question and remind them that SehatSaathi AI provides general education only (set supported_by_source to false).\n"
        "3. Never invent facts, statistics, clinical advice, or URLs.\n"
        "4. Return ONLY valid JSON with keys: {\"answer\": string, \"supported_by_source\": boolean}."
    )

    user_prompt = (
        f"Topic: {topic['title_en']} ({topic['title_ur']})\n"
        f"Target Language: {lang_label}\n"
        f"Approved Source Facts:\n{facts_bulleted}\n\n"
        f"User Question: {cleaned_q}\n"
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=450,
            ),
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
        "live_ai": True,
    }
