# SehatSaathi AI

**Understand health information in your own language.**

> **Educational Disclaimer:** SehatSaathi AI is a general public-health education prototype built for the STCS AI Hackathon & Startup Pitch (Student Week 2026, Minhaj University Lahore — UN SDG 3: Good Health and Well-Being). It does **not** provide medical diagnosis, clinical treatment advice, prescription guidance, or personalized medical care.

---

## Project Overview

SehatSaathi AI helps make trusted everyday public-health information easier to understand by turning curated, authoritative public-health facts into clear, bilingual **Urdu (`اردو`)** and **English** explanations and interactive comprehension questions.

- **Event:** STCS AI Hackathon & Startup Pitch, Student Week 2026, Minhaj University Lahore
- **Theme:** UN Sustainable Development Goal 3 — Good Health and Well-Being
- **Official Niche:** AI for Accessible Healthcare & Well-Being
- **Repository:** `https://github.com/Usman35404/SEHATSAATHI`

---

## Planned Architecture & Tech Stack

- **Backend:** Python 3 + Flask
- **Frontend:** Semantic HTML5, accessible CSS3 (with Urdu RTL support), and vanilla JavaScript
- **AI Integration:** Official Google Gen AI Python SDK (`google-genai`) running server-side with curated source grounding
- **Curated Sources:** Public, non-sensitive educational facts from CDC (*About Handwashing* and *About Sleep*) and WHO health-literacy principles
- **Testing:** `pytest`

---

## Local Setup (Placeholder — Phase 0)

1. Create and activate the virtual environment:
   ```powershell
   python -m venv .venv
   ```
2. Copy `.env.example` to `.env` locally (never commit `.env`) and configure your private credentials:
   ```dotenv
   GEMINI_API_KEY=replace_with_your_own_key_locally
   GEMINI_MODEL=replace_with_a_model_verified_for_your_account
   FLASK_DEBUG=false
   ```
3. Install dependencies and run the app (to be added in Phase 1):
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe app.py
   ```
