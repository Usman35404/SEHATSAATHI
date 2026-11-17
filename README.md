# SehatSaathi AI (`صحت ساتھی اے آئی`)

**Understand health information in your own language.**

> **Educational Scope & Safety Disclaimer:** SehatSaathi AI is a general public-health literacy web prototype built for the **STCS AI Hackathon & Startup Pitch (Student Week 2026, Minhaj University Lahore — UN SDG 3: Good Health and Well-Being)**. It does **not** diagnose illnesses, recommend treatments or medications, interpret private lab tests, or replace professional medical care. No clinical validation, regulatory approval, or patient data collection is claimed or performed.

---

## 1. Problem Statement & Target Audience (UN SDG 3 Alignment)

### The Barrier
Trusted everyday public-health guidance is often published in dense, technical English. Individuals who prefer reading in **Urdu (`اردو`)** or who are unfamiliar with medical terminology face a practical barrier when trying to understand essential preventive health information.

As framed by the **World Health Organization (WHO)**, health literacy involves the ability to access, understand, evaluate, and use health information to promote and maintain good health. SehatSaathi AI focuses specifically on **understanding educational public-health information across language and reading-level differences**.

### Target Users
- **Urdu-speaking individuals and families** looking for clear, everyday preventive health explanations.
- **Students and community learners** studying foundational hygiene and well-being habits.
- **Caregivers and community educators/NGOs** seeking accessible, source-attributed educational summaries with comprehension checks.

---

## 2. What Works in This Prototype

1. **Curated Public-Health Topic Selection:**
   - **Proper Handwashing (`ہاتھ دھونے کا درست طریقہ`)** grounded in CDC's *About Handwashing*.
   - **Healthy Sleep Basics (`صحت مند نیند کے بنیادی اصول`)** grounded in CDC's *About Sleep*.
2. **Bilingual Language Selector (`English` / `اردو`):**
   - Full Unicode Urdu rendering with dynamic `lang="ur"` and `dir="rtl"` on localized explanation, key takeaway, quiz, and follow-up blocks while preserving clean LTR rendering for URLs and controls.
3. **Live Server-Side Gemini AI Integration (`POST /api/explain`):**
   - Uses the official **`google-genai`** Python SDK server-side.
   - Grounded strictly in the selected topic's human-reviewed public-health facts (`content/topics.json`).
   - Generates a plain-language explanation, **3 key takeaways**, and a **3-option multiple-choice comprehension quiz** with explanatory feedback.
   - Validates the structured JSON schema on the server before returning `live_ai: true`.
4. **Transparent, Non-Hallucinated Source Attribution:**
   - The server attaches the authoritative source title and URL directly from the curated local dataset (`content/topics.json`), never from an AI-improvised citation string.
5. **Interactive Comprehension Quiz:**
   - Tests user understanding of the generated explanation and reveals immediate explanatory feedback upon submission.
6. **Optional Constrained Follow-Up Question (`POST /api/ask`):**
   - Answers short educational questions strictly within the selected topic's approved CDC facts, with a local clinical/emergency/privacy safety boundary gate.
7. **Accessibility & Graceful Voice Read-Aloud:**
   - Keyboard focus states, skip link, ARIA live regions, `Aa+` large-text toggle, and optional browser `speechSynthesis` read-aloud (gracefully disabled when a matching device voice is unavailable).
8. **Truthful Error Handling:**
   - Never substitutes prewritten/mocked text as fake live AI output when the API key is unconfigured or the network is unavailable.

---

## 3. Architecture & Data Flow

```text
User Browser (HTML5 / Accessible CSS3 / Vanilla JS)
  ├─ Selects Vetted Topic (handwashing | sleep) + Language (en | ur)
  ├─ Renders Live Explanation, 3 Key Points, Trusted Source URL & Quiz
  └─ Optional Browser speechSynthesis (client-side when voice exists)
                │
                │ GET  /api/health
                │ GET  /api/topics
                │ POST /api/explain  {"topic_id": "...", "language": "en|ur"}
                │ POST /api/ask      {"topic_id": "...", "language": "en|ur", "question": "..."}
                ▼
Flask Application Server (app.py)
  ├─ Input allowlist validation (topic_id & language)
  ├─ Retrieves human-reviewed facts from content/topics.json
  ├─ Attaches verified source_title & source_url from local catalog
  └─ Returns safe error codes (400 / 502 / 503) without leaking secrets
                │
                ▼
Gemini AI Service Layer (ai_service.py)
  ├─ Local safety boundary gate (blocks emergency, diagnosis/dosage & PII)
  ├─ Calls Google Gemini via official google-genai SDK (server-side API key)
  └─ Enforces structured JSON output & strict schema validation
```

### Technology Stack
- **Backend:** Python 3, Flask (`3.1.3`), `python-dotenv` (`1.2.4`)
- **AI SDK:** Official Google Gen AI Python SDK (`google-genai==3.4.0`), default model `gemini-2.5-flash` (configurable via `GEMINI_MODEL`)
- **Frontend:** Semantic Jinja2 HTML5, accessible responsive CSS3, vanilla JavaScript (zero frontend framework bloat, `textContent`-only DOM rendering to prevent XSS)
- **Testing:** `pytest` (`9.2.0`) with unit and route tests covering content integrity, AI schema validation, safety gates, and error states

---

## 4. Curated Public-Health Sources

All educational explanations are grounded exclusively in concise, paraphrased public facts from the following non-sensitive public sources (last reviewed **2026-11-17**):

1. **Centers for Disease Control and Prevention (CDC) — About Handwashing**
   - URL: https://www.cdc.gov/clean-hands/about/
2. **Centers for Disease Control and Prevention (CDC) — About Sleep**
   - URL: https://www.cdc.gov/sleep/about/
3. **World Health Organization (WHO) — Health Literacy & Plain Language Communication Principles**
   - URL: https://www.who.int/news-room/fact-sheets/detail/health-literacy
   - URL: https://www.who.int/about/communications/understandable/plain-language

*Note: Citation of public CDC/WHO educational material is for source attribution only and does not imply endorsement of this prototype by CDC, WHO, or Google.*

---

## 5. Local Setup & Run Instructions

### Prerequisites
- Python 3.10+ installed locally
- A valid Google Gemini API key configured privately in `.env`

### Step-by-Step Setup (Windows PowerShell)

1. **Create a virtual environment (if not already created) and install dependencies:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. **Configure your private environment variables:**
   Copy `.env.example` to `.env` (which is git-ignored) and set your real API key privately:
   ```dotenv
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   FLASK_DEBUG=false
   ```
   *Never commit `.env` or share your raw API key.*

3. **Run the automated test suite:**
   ```powershell
   .\.venv\Scripts\python.exe -m pytest -v
   ```

4. **Start the local web application:**
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```
   Open **http://127.0.0.1:5000** in your browser.

---

## 6. Safety, Privacy & Clinical Boundaries

- **Education Only:** SehatSaathi AI does not diagnose diseases, interpret lab results/scans, or recommend medications or dosages.
- **Zero Patient Data Collection:** No user accounts, login forms, names, phone numbers, CNICs, or medical records are requested or stored.
- **Local Safety Gate:** Follow-up questions requesting emergency help, personal diagnosis, prescriptions, or containing personal identifiers are intercepted locally with a safe educational boundary notice before reaching the model.
- **Secret Hygiene:** The Gemini API key remains strictly server-side in environment variables and is never exposed in HTML, JavaScript, `/api/health`, or error payloads.

---

## 7. Startup Pilot & Sustainability Proposal *(Unvalidated Hypothesis)*

> *Transparency Note: The following is our proposed post-hackathon startup and pilot model, not a claim of existing revenue or signed institutional partnerships.*

- **Mission:** Help schools, community centers, and public-health NGOs distribute clear, bilingual (Urdu/English) preventive health lessons with built-in comprehension checks.
- **Proposed First Pilot:** Partner with a university student-health program or local community education NGO to test comprehension improvements across 5–10 vetted preventive health modules.
- **Sustainability Hypothesis:** Keep core public-health literacy modules free for individuals while offering institutional licensing for schools, NGOs, and workplace wellness programs needing custom reviewed topic libraries and aggregated (non-personal) comprehension insights.
- **Known Limitations & Next Validation Steps:**
  - Currently supports 2 curated topics (`handwashing` and `sleep`); expanding requires human subject-matter review of each new source file.
  - Browser voice synthesis (`speechSynthesis`) depends on whether an Urdu TTS voice is installed on the user's operating system.
  - Requires formal readability testing with native Urdu speakers and review by public-health educators before real-world pilot deployment.
