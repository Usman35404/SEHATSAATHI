# SehatSaathi AI — Antigravity Master Build Playbook

**Project:** SehatSaathi AI — Understand health information in your own language  
**Event:** STCS AI Hackathon & Startup Pitch, Student Week 2026, Minhaj University Lahore  
**Theme:** UN Sustainable Development Goal 3 — Good Health and Well-Being  
**Official niche:** AI for Accessible Healthcare & Well-Being  
**Build date:** Tuesday, **17 November 2026**  
**Demo date:** Wednesday, **18 November 2026**  
**Status:** Build specification and step-by-step AI-agent instructions — **NOT prebuilt application code**

> **How to use this file:** Put a copy of this Markdown plan in your **new** hackathon repository created after the 10:00 AM kickoff. Open that repository in Google Antigravity, ask the agent to read this file, paste the **Master Guardrails** first, and then send the phase prompts **one at a time**. Review results between phases. This document describes a proposed implementation; only the official event PDFs define the competition rules.

---

## Table of contents

1. Non-negotiable official rules and deadlines
2. Product vision, users, problem and differentiation
3. Scope: must-have, stretch, and forbidden features
4. Architecture, stack and data flow
5. Repo structure and contracts
6. Data sources, content model and clinical-safety boundaries
7. UI/UX specification and accessibility
8. Security, privacy and agent permissions
9. Timeline and milestone gates
10. Master Antigravity guardrail prompt
11. Phase-by-phase Antigravity prompts (Phases 0–10)
12. Recovery prompts for common failures
13. Testing matrix and release acceptance criteria
14. README, startup case and judging strategy
15. Frozen-build demo script and judges' Q&A
16. Final checklist and reference links

---

# 1. NON-NEGOTIABLE OFFICIAL RULES AND DEADLINES

The source of truth is the organizer's **AI Hackathon STC Guidelines.pdf** (3-page participant rulebook) plus the later, more specific **AI Hackathon NICHE REVEAL STC.pdf** (2-page official challenge release). The challenge release names **TWO** mandatory GitHub collaborator accounts, updating the earlier generic reference to a designated organizer.

### Official event schedule

| When (Pakistan Standard Time) | Official requirement | Consequence / action |
|---|---|---|
| **Nov 17, 9:30 AM** | Participant reporting/check-in | Rulebook attendance requirement; already passed if reading later |
| **Nov 17, 10:00 AM** | Challenge revealed and development begins | Create a **new team repository after kickoff**; write competition code on-site only |
| **Nov 17, BEFORE 12:00 PM sharp** | Invite both official collaborators | **Immediate disqualification if either is missing** |
| **During build hours** | Build on the competition floor and commit/push regularly | Keep an auditable Git history; respect attendance rules |
| **Nov 17, 3:55 PM sharp** | Finish all edits and commits; **code freeze** | **No edits, new commits, or replacement builds after this time** |
| **Nov 18, 11:30 AM** | Report for demo | Rooms **6206–6209** |
| **Nov 18, 12:00–4:00 PM** | Present/demonstrate | Each team gets **5–7 minutes**, followed by Q&A; overrun can cause penalties |

**Both collaborator invitations must be issued before noon and retained for review:**

- **@httpsharis** — https://github.com/httpsharis
- **@anamta-JINX** — https://github.com/anamta-JINX

### GitHub collaborator action — DO THIS FIRST

1. Sign into GitHub and create one **new** repository, for example `SehatSaathi-AI-STCS-2026`, **after kickoff**. Never reuse an old project's code or Git history.
2. Open **Settings → Collaborators / Collaborators and teams → Add people**.
3. Invite `httpsharis` and confirm the invitation is displayed.
4. Invite `anamta-JINX` and confirm the invitation is displayed.
5. Retain **both invitations** until judging; do not delete pending invitations. If uncertain, show the collaboration/invitation page to an organizer before noon.
6. Record the repository URL in the README and in your team's records; never share account passwords or API keys.

> **Important distinction:** The official wording requires both **invitations to be issued** by noon and retained, not that the organizers must necessarily accept them by then. Do not remove a pending invitation yourself.

### Other mandatory rules

- Work on-site on the competition floor after kickoff. Respect restrictions on leaving the floor without authorization.
- Build an **original AI-enabled WEB application**, with a coherent, usable end-to-end user journey — not just slides or a mock interface.
- **Live AI** must actually run at demonstration time. Never present fabricated or hard-coded text as live AI output.
- AI APIs, AI coding assistants and modern web frameworks are **permitted**. The rulebook names Flask, FastAPI, React, etc. as examples; none is mandatory.
- Do **not** reuse a pre-built project, J.A.R.V.I.S. code, or ready-made commercial SaaS template. Build the competition application from scratch in its new repository.
- Use only **synthetic, public, or properly authorized non-sensitive data**. Do not use confidential patient information or private health records.
- Do not represent this prototype as a medical diagnostic tool or make unsupported clinical claims.
- Commit and push regularly. Keep a `README.md` explaining the problem, users, AI stack, startup model and local setup; keep `.env.example`; never commit `.env` or API credentials.
- On Wednesday, **demonstrate the identical frozen version from Tuesday 3:55 PM**. No after-freeze code or build changes, even to fix a bug.
- Bring a laptop, charger and reliable internet/hotspot. The official rulebook cautions against relying on the venue connection alone.
- The Google Developer $5 AI credit is **listed** in the rulebook, with a 12-hour validity period after activation; **availability and activation must be confirmed on-site**. Do not assume credit is active.

### Official judging weights

| Criterion | Weight | How we address it |
|---|---:|---|
| Problem Fit & Startup Potential | **25%** | Precise health-literacy barrier, target users, credible pilot and sustainability plan |
| Working Prototype & Reliability | **25%** | Fully working topic → language → AI explanation → quiz journey; tested failure states |
| AI Integration & Technical Depth | **20%** | Server-side Gemini integration grounded in curated source facts, structured output, validation and quiz generation |
| Design, Usability & Originality | **15%** | Accessible bilingual UX, Urdu right-to-left layout, readable mobile-friendly interface, optional voice |
| Live Demo Delivery & Q&A | **15%** | Rehearsed 5–7-minute demo; credible safety and business answers |

**Judging strategy:** Reliability and problem fit together represent **50%**. Do not sacrifice a successful live demo to chase every optional feature.

---

# 2. PRODUCT VISION, USERS, PROBLEM, DIFFERENTIATION

## Working name

**SehatSaathi AI** — *Understand health information in your own language.*

## One-sentence pitch

> SehatSaathi AI makes trusted everyday health information easier to understand by turning curated public-health facts into clear, bilingual Urdu/English explanations and comprehension questions, with optional browser-based read-aloud support.

## Clearly defined problem

Health information is often written in technical English. A person who is comfortable in Urdu or unfamiliar with medical vocabulary may struggle to understand essential general-health messages. The barrier addressed by this MVP is **understanding educational public-health information**, not diagnosing disease or replacing professional care.

**Evidence framing:** WHO explains that health literacy involves being able to access, understand, evaluate and use health information and services. We must not invent statistics about Pakistan or claim a measured local prevalence without supporting research.

## Target users

- Urdu-speaking individuals who prefer simple health information.
- Students and families learning practical preventive-wellbeing topics.
- Caregivers seeking **general**, non-personal educational explanations.
- Educators or NGOs creating accessible health-literacy experiences.

## The specific value proposition

1. Choose a vetted health-literacy topic.
2. Select Urdu or English.
3. Request a **live AI** explanation of the topic grounded in approved source facts.
4. See where the source information came from.
5. Optionally listen to the explanation if an appropriate browser voice exists.
6. Answer an AI-created comprehension question.

## What makes it meaningfully more than a chatbot?

- **Grounding**: The AI receives a curated, human-reviewed source excerpt rather than being asked to improvise health facts freely.
- **Adaptation**: The same core facts are presented in plain English or idiomatic Urdu for a defined reading level.
- **Structured output**: The agent returns an explanation, highlights and a quiz in a validated format.
- **Source transparency**: The app shows the approved source title and URL directly from the curated content data, not from an invented AI citation.
- **Comprehension check**: Users can test whether they understood the explanation.

**Never claim:** clinical validation, diagnostic accuracy, clinical treatment effectiveness, regulatory approval, proven health outcomes, or a completed local user study.

---

# 3. MVP SCOPE AND PRIORITIES

## P0 — Required for the working demo

- [ ] New GitHub repository created after kickoff; both organizers invited before noon.
- [ ] Original Flask app starts locally with a responsive web homepage.
- [ ] At least **two** vetted topics from public, non-sensitive sources.
- [ ] Topic selection is functional.
- [ ] English/Urdu selector is functional, including Unicode and RTL text handling.
- [ ] **Real server-side Gemini API** produces source-grounded explanations.
- [ ] AI outputs appear in the UI; validation and errors work.
- [ ] A source title and working URL are visible on each explanation.
- [ ] At least one AI-generated multiple-choice comprehension question is shown and can be answered.
- [ ] Safety disclaimer and out-of-scope response behavior are present.
- [ ] README, `.gitignore`, `.env.example`, requirements and local run instructions exist.
- [ ] Tests and manual smoke demo pass before freeze.

## P1 — Only after P0 works

- [ ] Voice/read-aloud button using browser speech synthesis.
- [ ] Follow-up question box limited to the currently selected educational topic.
- [ ] Friendly loading state and “try again” behavior.
- [ ] Large-text setting, high-contrast focus states, accessible control labels.
- [ ] Polished mobile layout and tasteful animation.

## P2 — Post-hackathon ideas ONLY (do not risk frozen MVP)

- Hospital/clinic referrals and provider directories.
- Persistent user accounts or patient profiles.
- Medication tracking or reminders.
- PDF upload, scanned prescription explanation or medical-image features.
- A clinical chatbot, personal risk score, symptom checker or medical decision support.
- Voice recognition, database-heavy analytics, complex multilingual expansion.

**Rule:** If the live AI + complete user journey does not yet work, stop work on all P1/P2 features.

---

# 4. ARCHITECTURE AND DATA FLOW

## Selected stack

- **Frontend:** Plain HTML, CSS and vanilla JavaScript (smallest reliable dependency footprint).
- **Backend:** Python 3 + Flask.
- **AI:** Google Gemini via the official `google-genai` Python SDK; configurable model ID via environment variable, confirmed through an actual live request.
- **Curated source data:** Local version-controlled JSON (`content/topics.json`) containing **public, non-sensitive facts**, titles and approved URLs.
- **Voice:** Browser `speechSynthesis`, only when supported and a usable voice is available.
- **Storage:** No production database; no user account; avoid collecting/storing user questions.
- **Testing:** `pytest` + Flask test client + manual browser smoke test.
- **Hosting for judging:** Local `http://127.0.0.1:5000` on the participant's laptop (plus active internet for Gemini).

## Logical diagram

```text
                          SEHATSAATHI AI

User's browser
  ├─ Topic cards, English/اردو selector
  ├─ Explain button, generated explanation and source
  ├─ Quiz selection and feedback
  └─ Optional speechSynthesis (client-side)
               |
               | GET /api/topics
               | POST /api/explain
               | POST /api/ask  [optional]
               v
       Flask app.py (server-side)
         ├─ Routes and input validation
         ├─ Out-of-scope / safety gate
         ├─ Approved topic lookup
         ├─ Output shape validation
         ├─ No-secret error responses
         └─ Health/readiness endpoint
               |
         ai_service.py
         ├─ System/developer guardrails
         ├─ Curated source context
         ├─ Language / simplicity instructions
         ├─ Structured JSON response request
         └─ Live Gemini API call (API key only server-side)
               |
               v
    Gemini service → generated educational response

content/topics.json = trusted facts + provenance, not a fabricated AI response
```

## Runtime sequence for main user journey

1. `GET /`: Flask renders the responsive page.
2. `GET /api/topics`: Flask lists approved topic IDs, titles and descriptions.
3. User selects a topic and `en` or `ur`, clicks **Explain with AI**.
4. Browser sends **only** `topic_id` and `language` (not full source data or a key) to `POST /api/explain`.
5. Flask checks the allowlist and retrieves the topic's reviewed source text from `topics.json`.
6. Flask calls Gemini live, instructing it to re-express **only** supplied topic facts in plain language and create one quiz question.
7. Server parses and validates the model response; attaches the **source URL from local data**, not model-generated metadata.
8. Browser displays explanation, key points, source and quiz. It labels the response as AI-generated only when a real call succeeded.
9. User selects an answer and receives explanatory quiz feedback.
10. If the service is down, display a transparent error. **Do not return canned text disguised as AI.**

## Minimum API contracts (proposed)

| Route | Method | Request | Success response | Failure |
|---|---|---|---|---|
| `/` | GET | None | HTML page | 500 on template issue |
| `/api/health` | GET | None | `{ "app": "ok", "ai_configured": true/false }` | Never expose key or sensitive configuration |
| `/api/topics` | GET | None | Array of topic summaries | 500 with safe error |
| `/api/explain` | POST | `{"topic_id":"handwashing","language":"ur"}` | Validated educational response | 400 bad input, 503 missing configuration/AI unavailable, 502 invalid provider output |
| `/api/ask` | POST | `{"topic_id":"handwashing","language":"en","question":"..."}` | Limited, source-grounded educational answer | 400/422/503/502; optional after core works |

**Candidate success shape** (contract, not fake API output):

```json
{
  "topic_id": "handwashing",
  "language": "ur",
  "explanation": "<real model-generated text in Urdu>",
  "key_points": ["<point A>", "<point B>", "<point C>"],
  "quiz": {
    "question": "<real model-generated question>",
    "options": ["<A>", "<B>", "<C>"],
    "correct_index": 0,
    "feedback": "<why the correct answer is correct>"
  },
  "source": {
    "title": "<exact curated source title>",
    "url": "<exact curated source URL>"
  },
  "live_ai": true
}
```

On failure use a **separate error schema** like `{"error":{"code":"AI_UNAVAILABLE","message":"Live AI is temporarily unavailable. Please try again."}}`; never set `live_ai:true` unless live inference returned and passed validation.

---

# 5. REPOSITORY LAYOUT, TOOLCHAIN AND CONTRACTS

## Expected repository tree

```text
SehatSaathi-AI-STCS-2026/
├── app.py                    # Flask routes, validation, HTTP errors
├── ai_service.py             # Gemini client and constrained prompt
├── content/
│   └── topics.json           # Approved public facts + citations
├── templates/
│   └── index.html            # Semantic, accessible HTML
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── tests/
│   ├── test_app.py
│   ├── test_content.py
│   └── test_ai_service.py
├── requirements.txt
├── .env.example               # PLACEHOLDERS ONLY
├── .gitignore
├── README.md
└── SEHATSAATHI_AI_ANTIGRAVITY_MASTER_PLAN.md
```

The implementation agent can adjust the exact names if there is a technical reason, but it must explain changes and preserve separation of concerns.

## Minimal `requirements.txt` package targets

- `Flask`
- `google-genai` (official maintained SDK, not deprecated `google-generativeai`)
- `python-dotenv` (for local environment loading)
- `pytest` (tests)

Use compatible pinned versions **after installation and testing** rather than inventing version numbers in the plan.

## `.env.example` — placeholder content, not credentials

```dotenv
GEMINI_API_KEY=replace_with_your_own_key_locally
GEMINI_MODEL=replace_with_a_model_verified_for_your_account
FLASK_DEBUG=false
```

The user sets the actual key **manually and privately** in an untracked `.env` file or environment variable. Agents should not open, read, display, log, transmit, validate by printing, or commit the secret. The model ID should be the one demonstrated to work in the current account; do not assume a name from an old project is available forever.

## `.gitignore` expectations

At minimum ignore `.env`, `.env.*` **except** `.env.example`, `.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, `.idea/`, `.DS_Store`, logs, Python caches and local build artifacts. Keep `requirements.txt` and the example environment file tracked.

## Optional local setup (Antigravity can do this with approval)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Use the Antigravity graphical UI for prompting and reviewing diffs. A terminal is needed only if the agent runs setup/test commands; you do **not** need to do everything in a CLI.

## Important integration rules

- Never embed the API key in JavaScript, HTML, query strings, Git history, markdown, screenshots or demo slides.
- Configure Flask for local demo; don't bind publicly to `0.0.0.0` without a deliberate need and security review.
- Production-style authentication is **out of scope** because there are no private accounts or records.
- Never accept arbitrary external source URLs as input to the model; source selection is from curated IDs only.
- Do not call a fake AI helper for demo routes. Unit-test mocks are allowed only inside tests and must be clearly distinguished from the live app.

---

# 6. CURATED CONTENT, SAFETY AND QUALITY

## Launch with TWO dependable topics

**Topic A — Proper Handwashing**

- Approved source: CDC, *About Handwashing*.
- URL: https://www.cdc.gov/clean-hands/about/
- Scope: Why washing hands matters, key times and simple general handwashing steps.
- Do not add disease diagnosis claims or unsupported medical benefits.

**Topic B — Healthy Sleep Basics**

- Approved source: CDC, *About Sleep*.
- URL: https://www.cdc.gov/sleep/about/
- Scope: General sleep-health information and age-specific recommendations where explicitly supported; do not give personalized sleep diagnosis or treatment.

**Context / communication framework:**

- WHO, *Health literacy*: https://www.who.int/news-room/fact-sheets/detail/health-literacy
- WHO, *Use plain language*: https://www.who.int/about/communications/understandable/plain-language

**Source integrity requirements:**

1. Agent must retrieve/inspect the official source before writing concise `facts` text. Record URLs and source titles in the JSON.
2. Do not copy large copyrighted passages. **Paraphrase in small, accurate summaries** and link to the source for details.
3. Keep a `last_reviewed` date for project maintenance; do not infer a page's publication date if none is visible.
4. `topics.json` is publicly sourced **knowledge context**, not a prewritten AI answer.
5. Any model-generated claims not supported by the selected topic's facts should be removed or the response rejected, particularly specific numbers, drug recommendations and clinical claims.
6. Never hallucinate a research citation or imply WHO/CDC endorsed SehatSaathi.

## Proposed topic JSON format

```json
[
  {
    "id": "handwashing",
    "title_en": "Proper Handwashing",
    "title_ur": "ہاتھ دھونے کا درست طریقہ",
    "summary_en": "Learn everyday hand hygiene basics.",
    "source_title": "CDC — About Handwashing",
    "source_url": "https://www.cdc.gov/clean-hands/about/",
    "last_reviewed": "2026-11-17",
    "facts": [
      "<short accurate paraphrase of an approved fact>",
      "<another approved fact>"
    ]
  }
]
```

These placeholders are **not** finished facts or output. Antigravity must populate them from public references in its content phase.

## Safety limits — enforce both in prompt and route validation

SehatSaathi is **general educational health literacy**, not individualized medical advice. The model must not:

- Diagnose a disease or infer a condition from symptoms.
- Recommend prescriptions, dosage, treatment plans or medication changes.
- Interpret private medical tests, scans or prescriptions.
- Request or retain names, phone numbers, addresses, patient IDs, dates of birth or medical records.
- Make promises of medical accuracy or outcomes.
- Invent source links or continue answering as though it has new facts when it doesn't.

If a user submits a personalized symptom question, private health data, or a request for diagnosis, give a brief, neutral boundary message: the app provides general education only; for personal medical concerns, ask an appropriate qualified healthcare professional. For potential emergencies, encourage contacting local emergency services or immediate professional help without trying to diagnose. Avoid exposing the text to AI if a simple local safety gate can handle it.

**Do not** use a stock phrase for all normal educational questions; the AI must still produce genuine useful content within permitted topics.

## A practical anti-hallucination design

- Restrict topic IDs to known entries in `topics.json`.
- Pass the **selected** topic's curated facts into the live prompt.
- Explicitly request: “Use only these facts; if not supported, say the provided material does not cover it.”
- Separate local source metadata from the AI-generated body; always source it from JSON, not a citation string the model made up.
- Validate schema, string lengths and quiz option count before returning success.
- Handle malformed model output as a visible error and log only a safe error category, not the request or secrets.
- Prefer deterministic-ish model settings where supported, but don't claim deterministic outputs; variation is fine.

---

# 7. UI / UX DESIGN SPECIFICATION

## Visual direction

- Brand: **SehatSaathi AI**.
- Tone: approachable, calm, trustworthy, not a hospital or diagnostic system.
- Palette recommendation: white/ivory background, dark slate text, teal/mint accents, accessible contrast. Use simple inline icons or CSS illustrations; don't rely on a giant pre-built UI theme.
- Responsive layout: desktop split into topic/sidebar + main educational response; mobile stacked cards.
- Display a visible subheading: **“General health education — not diagnosis or treatment.”**
- Avoid any fake “doctor certified,” “100% accurate,” or “clinically approved” badges.

## Main screen sections

1. Header: brand, tagline, compact language selector.
2. Hero area: what the app does in one line; explanation of educational-only scope.
3. Topic list: at least **Handwashing** and **Healthy Sleep**.
4. Central action: **Explain with AI**.
5. AI explanation region: loading, success and failure states.
6. Three key takeaway bullets.
7. Curated source link.
8. Single multiple-choice quiz and feedback.
9. **Listen** button only if the browser reports support / available voice.
10. Footer: educational disclaimer, public information sources, privacy note.

## Interaction details

- Language selection: `English` and `اردو` visibly available.
- Urdu content uses `lang="ur"` and `dir="rtl"` in its content section; the page may remain LTR outside those sections.
- **Do not auto-reverse** icons, URLs, numbers or buttons incorrectly; test Urdu text rendering.
- Focus outlines and keyboard navigation must remain visible.
- Loading state should prevent repeated clicks and indicate genuine request progress.
- User must be able to retry if a request times out.
- Error states must be truthful: “Live AI couldn't respond right now”; never silently substitute prewritten text while labeling it live.
- Quiz should not reveal the correct answer until user submits a choice.
- On a second request, clear stale response or explicitly label previous content so it cannot be mistaken for the new result.
- Speech feature may not have Urdu voices on every machine. Hide/disable gracefully; do not claim Urdu audio works until tested on the demo laptop.
- Keep browser support and internet constraints in mind for tomorrow.

## Nice-to-have polish, only after functional stability

- Small, subtle hover transitions and restrained animation.
- Icons for topics (hand, moon) and audio.
- Accessible font sizing toggle.
- 3-column stats are **not** needed; never invent user statistics.
- No fake doctor avatars or unverifiable accreditation.

---

# 8. AGENT PERMISSIONS, SECRETS AND REVIEW POLICY

Because Antigravity can act on files and run commands, set the working scope deliberately:

### Safe actions the agent may perform **with review**

- Create/edit files **inside the newly created hackathon repository**.
- Install ordinary project dependencies inside its dedicated `.venv`.
- Start/stop the local dev server and run tests.
- Use a browser to inspect the locally running app and take screenshots **without showing secrets**.
- Make Git commits **before freeze** only after the team inspects changes, approves the command and checks tracked files.
- Read public documentation for the selected SDK and source topics.

### Actions requiring direct user approval, or not allowed

- **Ask first:** creating/inviting GitHub collaborators, pushing, changing repository visibility, installing global software, and any deployment/upload operation.
- **Never:** open/copy/display actual `.env` values, API keys, tokens, password stores or credentials; copy secrets into logs; open unrelated home/other-project directories; copy J.A.R.V.I.S. source; run destructive clean/reset commands without approval; force-push; delete repository; create a medical data-collection workflow.
- **Never after 3:55 PM:** source edits, format changes, generated build changes, dependency changes, commits, deployment of a replacement build, or agent background tasks that can mutate the app.

**Important:** A written prompt is not a technical security boundary. Use Antigravity's permission/approval settings and inspect file diffs and tool requests. Prefer “ask for approval” over unattended shell or Git operations.

### Before every Git commit

Check changed files and staged paths; verify that `.env`, logs, token dumps, caches and secret files are absent. Run a secret scan of staged **file names and safe patterns only**, without printing sensitive matched values. Do not commit if uncertain.

### Before the deadline

Stop and terminate any unfinished agents; confirm no autonomous process will continue editing after 3:55 PM. Code-freeze compliance is more important than finishing a feature.

---

# 9. BUILD TIMELINE AND GATE CRITERIA

These are **suggested internal work blocks**, not official judging deadlines. Adapt to actual progress, but **never extend past the 3:55 PM official freeze**.

| Suggested time window | Goal | Exit condition |
|---|---|---|
| **10:00–10:35** | New repo; invite both organizers; setup workspace | Both invitations visibly issued; new repo ready |
| **10:35–11:10** | Basic Flask app + UI shell | App loads on browser with two topic cards |
| **11:10–11:45** | Curated topic JSON + basic API | `/api/topics` returns approved topics; sources recorded |
| **11:45–12:30** | Gemini integration | Genuine AI response in Flask from verified model and key |
| **12:30–1:20** | Frontend end-to-end connection | Explain action shows real bilingual response and source |
| **1:20–2:00** | Quiz, Urdu, responsive polish | Full journey works in both languages |
| **2:00–2:45** | Error states, tests and accessibility | No hard-coded fake AI; invalid inputs handled |
| **2:45–3:20** | README, startup story, local rehearsal | Demo works twice; docs accurate |
| **3:20–3:45** | Final tests, audit and push | Verified commit and dependency state |
| **3:45–3:55** | Stop agent activity and freeze safely | Final commit pushed; zero pending edits |

### Cut rules if the schedule slips

- **If no real Gemini response by 12:30:** stop visual polish. Fix the network/key/model and minimal backend path.
- **If no full user journey by 2:00:** skip voice and follow-up chat; make topic → live AI → visible result → quiz work.
- **If tests fail after 3:20:** fix only critical demo failures; do not add new features.
- **After 3:45:** do not start tasks that might outlast the 3:55 freeze.
- **At 3:55:** everything stops, even if unfinished.

If fewer people are on the team, use one agent with phase-by-phase oversight instead of uncontrolled parallel work. If 2–3 participants, split UI, backend/AI, and testing/pitch **but agree on API contracts before merging**.

---

# 10. MASTER ANTIGRAVITY GUARDRAIL PROMPT

**Paste this once at the start of the Antigravity conversation. For later sessions, paste again before a phase if necessary.**

```text
You are the implementation assistant for SehatSaathi AI, an original web application being built ON SITE at the STCS Minhaj University Lahore AI Hackathon on November 17, 2026.

First read the entire file SEHATSAATHI_AI_ANTIGRAVITY_MASTER_PLAN.md. Treat the official event rules in its Section 1 as hard constraints, and the rest as a proposed technical plan. We must implement the project from scratch in this newly created repository after the 10:00 AM kickoff; do not reuse or copy any old codebase, earlier projects, J.A.R.V.I.S. files, or commercial pre-built SaaS templates.

PRIMARY OUTCOME: Build a stable, demonstrable, bilingual Urdu/English health-literacy web app with real source-grounded AI and a coherent educational user journey. This is education only, not diagnosis, treatment or personalized medical advice.

SCOPE AND PERMISSIONS:
- Work only in the current repository. Never inspect unrelated directories or projects.
- Never read, print, transmit, stage, commit, log or display actual .env secrets, GEMINI_API_KEY values, tokens, browser credentials, private records or passwords. You may read .env.example placeholders. Ask the human to set the key locally and privately.
- For any destructive operation, global installation, remote Git/GitHub action or action outside the repo, ask explicit approval first.
- No force pushes, git reset --hard, repository deletion, credential exposure or unattended deployment.
- Do not generate a replacement build, edit files, or make commits after 3:55 PM Pakistan Standard Time, November 17, 2026. If the deadline is near, stop coding, describe remaining tasks and request the user to perform final review. Do not schedule any later automatic code mutations.
- Real AI calls are mandatory in the running application. Mocks only belong in tests; no simulated/hardcoded content may be represented as live AI.
- Use only public, non-sensitive approved source facts for health explanations. Never create or solicit patient data. Never claim clinical validation.

WORKFLOW:
1) Work on ONLY the named phase provided in my next message. Do not silently move to future phases.
2) Inspect repository structure and public docs relevant to the phase, but do not open .env secrets.
3) Briefly state the implementation plan and exact files to modify.
4) Implement smallest working change with sensible code quality.
5) Run focused tests and a smoke test when feasible.
6) Report actual results, changed files, errors, remaining limitations, and whether the phase's acceptance criteria passed.
7) Stop and await approval for the next phase. Do not claim tests passed unless you ran them.

Prefer Flask + vanilla HTML/CSS/JS + official google-genai SDK, with documented contract boundaries, meaningful errors, input validation and minimal dependencies. Favor reliability over shiny features.

ACKNOWLEDGE THESE RULES AND WAIT FOR THE PHASE 0 PROMPT.
```

---

# 11. PHASE-BY-PHASE PROMPTS FOR ANTIGRAVITY

**Operational instruction:** Copy one block at a time. Complete its acceptance checklist. Do not ask Antigravity to “build everything” in one pass; that wastes time on wrong assumptions and makes code diffs hard to review.

## PHASE 0 — Repo verification, deadline and tooling (HIGHEST PRIORITY)

**Goal:** Check that the repository is truly new, no old code was copied, and both organizer invitations are done before noon.

**Human-owned actions (do not delegate blindly):** Create repo, invite both named organizer accounts, confirm invitation status and organizer deadline.

**Antigravity prompt:**

```text
PHASE 0: SAFE REPOSITORY AND WORKSPACE READINESS. Do not implement app features yet.

Read our master playbook and inspect ONLY the current repository metadata and file names, not unrelated folders and never real .env secrets.

1. Confirm this is a newly created, dedicated SehatSaathi AI hackathon repository with no reused application code; if you cannot establish when the repository was created, report that you cannot verify it and ask me to confirm manually.
2. Check whether README.md, .gitignore and .env.example exist; create only safe placeholder versions if missing.
3. Display the two collaborator HANDLES and tell me the exact GitHub UI path to invite them: @httpsharis and @anamta-JINX. The organizer invitations must be issued BEFORE 12:00 PM on Nov 17, 2026. Do NOT assume that listing these handles means invitations were sent. Do not send invitations without explicit permission and authorization.
4. Inspect Python availability and the current project's dependency setup; use a dedicated .venv. Do not install global packages.
5. Propose minimal application paths and development commands.
6. Check Git ignore patterns; ensure secrets cannot be staged accidentally. Do not read .env.
7. Report a checklist: new repo verified or not verified; both invites human-confirmed or not confirmed; workspace ready; missing prerequisites.

STOP after Phase 0. Ask me to confirm invitation completion before Phase 1. Do not commit or push without my explicit approval.
```

**Acceptance:** [ ] Both invitations visibly sent before noon, [ ] new repo exists, [ ] correct folder open, [ ] no secret-tracking hazard.

---

## PHASE 1 — Flask skeleton and basic frontend

**Goal:** User can open the app locally and see brand, topic cards, language selector and educational disclaimer, even before live AI is connected.

**Antigravity prompt:**

```text
PHASE 1: BUILD THE MINIMAL FLASK APPLICATION AND RESPONSIVE UI SHELL.

Implement the original SehatSaathi AI application from scratch within this new repository. Do NOT implement any fake AI text or live Gemini integration yet.

Tech: Python/Flask backend, semantic Jinja2 HTML, vanilla CSS, vanilla JS. Avoid React, Vite, Node build complexity or unnecessary dependencies.

Create or update:
- app.py with GET / and GET /api/health.
- templates/index.html with semantic and accessible UI regions.
- static/css/style.css with responsive healthcare-literacy design.
- static/js/app.js for basic selector, topic-card state and loading placeholders.
- requirements.txt, .gitignore, .env.example and basic README.md.

Design requirements:
- Brand heading 'SehatSaathi AI' and tagline 'Understand health information in your own language.'
- Two topic cards: Proper Handwashing; Healthy Sleep Basics. Initially they may be static navigation labels ONLY, not fake AI content.
- English / اردو toggle.
- Disabled or clearly not-yet-connected 'Explain with AI' state until an actual endpoint exists. Do not show simulated answers.
- Visible text explaining that it is a general educational prototype, not a diagnosis/treatment service.
- Clean teal/ivory visual style, readable typography, mobile and desktop layout, keyboard focus states.
- Error-safe template/static file handling.

Verification:
- Install project dependencies inside .venv after asking approval if commands require it.
- Start the local Flask app. Verify GET / returns 200, page renders and static assets load; verify GET /api/health returns a safe 200 response without exposing configuration.
- Run one browser smoke check at desktop and mobile viewport if supported.
- Report the exact changed paths, run command and whether checks passed. Do not make unsupported claims.

IMPORTANT: Do not proceed to Phase 2 until approved. Do not read actual .env secrets. Do not push without permission.
```

**Acceptance:** [ ] `/` returns 200, [ ] mobile cards fit, [ ] topic/language controls visible, [ ] no fake AI response, [ ] secrets ignored.

---

## PHASE 2 — Curated public-health content and topic API

**Goal:** Source-backed public material is present, with a transparent citation trail.

**Antigravity prompt:**

```text
PHASE 2: IMPLEMENT A SMALL, CURATED, PUBLIC-HEALTH KNOWLEDGE BASE.

Use ONLY public, non-sensitive information from two authoritative primary sources:
1) CDC About Handwashing: https://www.cdc.gov/clean-hands/about/
2) CDC About Sleep: https://www.cdc.gov/sleep/about/

Read and inspect these sources first. If access is unavailable, tell me and do not invent content; ask me to supply verified excerpts or use only source facts already verified in our master plan. Do not paste long copyrighted text; write concise faithful paraphrases suitable as AI grounding context.

Create content/topics.json with exactly two MVP topics: handwashing and sleep. Each must include:
- stable id
- readable English and Urdu titles
- short English description
- authoritative source_title and exact source_url
- last_reviewed date
- short list of vetted, general educational facts
- scope boundaries if applicable

Implement GET /api/topics. It must return a safe list of topic summaries; don't leak unnecessary internal metadata or configuration. Add a backend helper to look up a topic only by allowlisted ID.

Add pytest unit tests for valid topics, valid URLs, missing topic IDs and invalid data schema. No patient data, no personal questions, no diagnoses, no drug recommendations.

Verify that API topic cards can be populated from the endpoint. Do not generate explanations with AI in this phase; do not substitute static content as an AI response.

Provide changed-file list, concise proof of source fidelity, tests executed and results. STOP for approval.
```

**Acceptance:** [ ] two trusted URLs, [ ] concise paraphrased source facts, [ ] `/api/topics` works, [ ] no claims beyond sources, [ ] tests run.

---

## PHASE 3 — LIVE Gemini AI integration (MISSION CRITICAL)

**Goal:** One real server-side API call generates a validated, source-grounded explanation and comprehension quiz. Never invent successful live AI output.

**Antigravity prompt:**

```text
PHASE 3: INTEGRATE REAL GEMINI FOR SOURCE-GROUNDED EDUCATIONAL EXPLANATIONS.

This phase is mission critical. Use the official maintained Python Google Gen AI SDK (`google-genai`). Check current SDK documentation first, not old google-generativeai patterns. Use configured GEMINI_MODEL; verify the model works for the currently authorized account with an actual call. Read the key from runtime environment only. NEVER OPEN OR PRINT ACTUAL .env CONTENTS OR KEY VALUES. If the key is missing, report a safe, specific setup error and ask the human to configure it privately.

Implement:
- ai_service.py: client initialization, prompt construction with approved topic facts, a real model invocation, timeout and error handling, structured output parsing/validation.
- POST /api/explain: JSON body topic_id + language only; validate values, reject unknown topics and unsupported languages, then call the live AI service.
- Clear error responses for missing configuration, provider timeout, provider failure and invalid model JSON. No internal stack traces in the UI or browser response.
- A maximum input/response size reasonable for a demo and single-topic context to limit cost and unexpected outputs.

Grounded AI requirements:
- Use selected topic's local, curated public facts as the ONLY subject-matter grounding.
- Explain in simple, respectful, understandable English or idiomatic Urdu, avoiding unnecessary jargon.
- Provide short explanation, three key points, one multiple-choice question with exactly three choices, correct_index in range 0..2 and a short reason/feedback.
- No diagnosis, personalized treatment, prescriptions, interpretation of private tests, or ungrounded claims.
- Do not generate source links in model text. Return source title and URL directly from trusted topics.json.
- Return `live_ai: true` only after an actual model response successfully passes validation.
- Invalid / unparseable model output is an error, NOT a fabricated success.

Schema expectation:
{
 topic_id: string, language: 'en'|'ur', explanation: string,
 key_points: string[3],
 quiz: {question:string, options:string[3], correct_index:integer, feedback:string},
 source: {title:string, url:string}, live_ai: true
}

Use the SDK's structured-output option if current documentation supports it; otherwise robustly parse and validate JSON, without silently filling missing content with fake AI text.

Testing:
- Mock the provider only inside unit tests to check valid/invalid outputs, input validation, unavailable API and error paths.
- Request explicit permission for one live, billable verification call to the model, using non-sensitive public handwashing data; report whether it truly succeeded, latency and response shape. NEVER print the raw key or any secret.
- Do not tell the user live AI is working unless a real call succeeded.

Report tests, exact changed files, model name (not credentials), any API limitation and sample non-sensitive topic flow status. STOP after this phase.
```

**Acceptance:** [ ] authentic live response, [ ] response validated, [ ] source URL not AI-fabricated, [ ] errors truthful, [ ] test mocks only in tests.

---

## PHASE 4 — Connect frontend to live explanation

**Goal:** Complete first real end-to-end user interaction in the browser.

**Antigravity prompt:**

```text
PHASE 4: CONNECT THE REAL WEB UI TO THE LIVE AI API.

Do not change the AI-service contract unless absolutely necessary; if needed, update tests and document why.

Make the browser flow work from start to finish:
1. Load topic summaries from GET /api/topics.
2. User selects a topic and English or Urdu.
3. Explain with AI sends POST /api/explain with only approved topic_id and language.
4. Show an accessible loading indicator; prevent duplicate submissions and stale-response races.
5. On live success, render the explanation, exactly three key points, and the original curated source title/URL.
6. Show an 'AI-generated' indicator only for confirmed live success. Never label static placeholder content as live.
7. On timeout/provider error, show a helpful retry message; never silently fall back to fabricated content.
8. Clear old quiz/result content when user changes topic or requests a new explanation.

Security/UI requirements:
- No model/API key in frontend code, DOM or requests.
- Render model text as TEXT, not unsanitized innerHTML; do not execute model-provided markup, scripts or links.
- Validate output shape on server; frontend should handle missing fields defensively.
- Keep source URLs from trusted server data only.

Test manually in browser in both language modes, including a real call using a public topic. Run app tests. Report changed files, browser evidence without credentials, and any known issues. STOP for approval.
```

**Acceptance:** [ ] Topic → language → real AI explanation → visible source, [ ] no fake output, [ ] Urdu text displays correctly, [ ] errors tested.

---

## PHASE 5 — Urdu RTL, comprehension quiz and optional voice

**Goal:** Turn a working explanation into an educational learning journey.

**Antigravity prompt:**

```text
PHASE 5: COMPLETE BILINGUAL ACCESSIBILITY AND THE EDUCATIONAL QUIZ.

Work only on the user experience and narrow supporting changes; the live AI path must remain operational.

1. Urdu: apply lang='ur' and dir='rtl' to generated Urdu content, quiz and key-point text. Verify common punctuation and mixed English URLs remain readable. Do not reverse the whole app blindly.
2. Quiz: show the generated question and three options returned by the REAL Gemini response. On user selection, reveal whether it matches correct_index and display the model's provided explanation/feedback. Do not show the answer before submission.
3. Reset quiz state on new topic/language/explanation.
4. Keyboard accessibility: radio/answer choices have labels; focus indicators; result announcements via an appropriate aria-live region; button states accessible.
5. Optional browser speechSynthesis: provide 'Listen' and 'Stop' controls only when supported. Choose an available matching voice when one exists. If no Urdu voice is installed or browser speech is unavailable, show a graceful 'voice not available on this device' state. Do not claim speech works on all devices.
6. Keep educational disclaimer and source visibility prominent.

DO NOT build speech recognition, audio uploads, text-to-speech cloud billing, user accounts, or any personal health profile.

Run checks for English, Urdu, quiz correct/incorrect, keyboard focus, and unavailable voice. Report real results and untested features honestly. STOP for approval.
```

**Acceptance:** [ ] quiz works, [ ] RTL verified, [ ] accessibility reasonable, [ ] unsupported audio handled safely.

---

## PHASE 6 — Optional constrained follow-up explanation (ONLY IF TIME)

**Goal:** Make AI integration deeper without turning the product into a general medical chatbot.

**Skip this phase automatically if** the core app is unstable, deadlines are near or user has not approved it.

**Antigravity prompt:**

```text
OPTIONAL PHASE 6: ADD A SINGLE CONSTRAINED FOLLOW-UP QUESTION ABOUT THE SELECTED EDUCATIONAL TOPIC.

Only proceed if the entire P0 user journey is working and the human explicitly approved this optional phase.

Implement POST /api/ask with: topic_id, language, question (short capped length). Accept only known topic IDs and plain text. Ground the answer strictly in the selected topic's curated source facts. Do not build an unrestricted symptom-checker or generic medical bot.

If the question is not answerable from those facts, politely say the current learning material does not cover it. If a question requests personalized diagnosis, drug instructions, private medical interpretation or emergency handling, respond with a brief educational-only boundary and encourage appropriate professional support. No specific patient details should be requested or stored.

Display question/answer clearly in the existing UI; never imply follow-up answers came from the CDC/WHO verbatim unless they are actually quotes and properly attributed. Model text must be escaped, rate/length limits and safe failures should work.

Write tests for normal topical educational follow-ups, unrelated questions, out-of-scope questions and provider failure. Perform one live verification call with non-sensitive educational input if authorized. STOP after reporting results.
```

**Acceptance:** [ ] source-grounded, [ ] no personal clinical advice, [ ] safety tests, [ ] not allowed to delay P0 completion.

---

## PHASE 7 — Reliability, privacy and security audit

**Goal:** Make the app survive the demo without privacy leaks, hidden fake fallbacks or avoidable crashes.

**Antigravity prompt:**

```text
PHASE 7: PERFORM A FOCUSED RELIABILITY, SAFETY AND SECRET-HYGIENE AUDIT.

Preserve working features. Do not add unrelated infrastructure.

Audit and fix these items in priority order:
A) Secret handling: .env and local credentials ignored; no API key in HTML/JS/README/logs; no output of actual key values; no hard-coded credentials.
B) Real-AI integrity: app never labels mocked, cached or canned content as a live Gemini answer. Unit-test mocks remain restricted to tests. Missing/failed AI yields truthful errors.
C) Input handling: unknown topic IDs, unsupported languages, malformed JSON, non-JSON POST, oversized input, missing fields and repeated clicks.
D) Output safety: validate structured AI response; strip/reject unexpected fields as appropriate; model text rendered safely (not raw HTML); source URL from curated allowlist.
E) Timeout and network: provider unavailable, rate limit, slow mobile hotspot and no internet. Retry messaging is honest; no infinite loading state.
F) Privacy: no data-collection fields for patient information; do not store health questions; no sensitive prompt logging.
G) Accessibility: mobile viewport, keyboard focus, English/Urdu typography, contrast, screen-reader labels and quiz feedback.
H) Health endpoints: never reveal model key, filesystem paths or other private configuration.

Add/maintain focused pytest tests and run them. Do not run secret-scanning commands that print matched secret values. Instead report whether risky files/patterns are present, redacting any findings before display.

Output a severity-ranked report (BLOCKER/HIGH/MEDIUM/LOW), tests actually run, exact changes, and remaining risk. Do not proceed to visual polish while blockers exist. STOP for approval.
```

**Acceptance:** [ ] no credentials leaked, [ ] safe error behavior, [ ] no fabricated AI, [ ] blocking bugs closed.

---

## PHASE 8 — Visual polish and 2-minute smoke journey

**Goal:** Demonstrate the app smoothly on the judging laptop. Only proceed if the core is reliable.

**Antigravity prompt:**

```text
PHASE 8: POLISH THE DEMO WITHOUT REGRESSING FUNCTIONALITY.

Apply small, original, accessible visual improvements to SehatSaathi AI. Favor clarity and perceived trust over decoration. Keep frontend dependency-free.

Improve spacing, responsive layout, topic cards, hover/focus states, readable Urdu, source attribution, loading and failure states. A tasteful teal/mint healthcare-literacy design is preferred. Do NOT invent awards, testimonials, doctors, hospital partners, certification badges, clinical stats or 'accuracy' claims.

With explicit permission, run the local app and use the browser tool for one end-to-end smoke sequence:
- Load home page;
- Select handwashing;
- Choose Urdu;
- Trigger a REAL Gemini explanation;
- Verify source URL appears;
- Answer the comprehension quiz;
- Switch to English;
- Test mobile viewport and one failure state.

Protect credentials in screenshots and logs. If speech capability is not available, show graceful degradation; do not block the demo.

Report screenshot/test observations, time-consuming failures, a short list of changed files and whether the exact demo story is now ready. STOP. Do not add extra features.
```

**Acceptance:** [ ] clean desktop and mobile, [ ] live AI worked twice, [ ] quiz worked, [ ] app still passes tests.

---

## PHASE 9 — README, startup pitch, final audit, version freeze

**Goal:** Submit compliant code with a credible project story, then **stop all mutations by 3:55 PM**.

**Antigravity prompt:**

```text
PHASE 9: FINAL SUBMISSION READINESS — SAFETY FIRST AND NO POST-FREEZE CHANGES.

Before doing anything, tell me the local Pakistan Standard Time if it is available reliably; otherwise ask me to read the clock. If we are already at or after 3:55 PM on November 17, 2026, make NO edits, commits, formatting changes or builds; report only what can be observed safely without changing the frozen artifact.

If time remains before 3:55 PM, do the following in this order:
1) Finish README.md with: problem, target audience, SDG 3 fit, features, original architecture, AI model/provider and server-side use, verified source links, safety/privacy boundaries, startup/pilot business model (label assumptions), how to install/run locally, how to configure key privately, test commands, and known limitations.
2) Confirm .env.example includes only placeholders; .gitignore excludes secrets, caches and logs.
3) Run automated tests and ONE final end-to-end real AI demo on approved public content with explicit billing approval. Note exact real test outcomes.
4) Review Git changes and check staged filenames for secret exposure without printing sensitive file values.
5) Check that the repository is new, created after kickoff, that two organizer invitations were issued before noon (human verifies this in GitHub), and that regular commits exist. Do not pretend you verified remote invitations if you cannot actually see them.
6) Provide the user with proposed safe commit message and exact changed-file summary. Ask for approval before commit and push; do not force-push.
7) Help the user finish all approved commits/pushes BEFORE 3:55 PM and confirm there are no pending source changes.
8) TERMINATE any running background agent processes capable of editing code; do not schedule tasks to mutate the repo later. No new build or edit after freeze.

Do NOT refactor working code, install new frameworks, introduce new features, or create a replacement build as the deadline approaches.

Report a final status table: compliant / needs human check / failed, and the verified commit hash if available. STOP all work after submission.
```

**Acceptance:** [ ] README complete, [ ] `.env.example` safe, [ ] tests real, [ ] user verified invites, [ ] commit pushed **before** freeze, [ ] no edit after deadline.

---

## PHASE 10 — Wednesday presentation rehearsal (NO CODE CHANGES)

**Goal:** Practice with the **frozen Tuesday codebase**. It is permitted to rehearse; the rule prohibits changing the build after freeze.

**Antigravity prompt:**

```text
PHASE 10: READ-ONLY FROZEN-BUILD DEMO PREPARATION FOR WEDNESDAY, NOVEMBER 18, 2026.

Critical: It is AFTER the official Tuesday 3:55 PM code freeze. Make NO modifications, builds, installation-induced dependency or lockfile changes, Git commits, formatting changes, fixes or remote updates. Read only the existing README, master plan and frozen files. Do not display credentials.

Help us prepare a 5–7-minute live pitch covering:
- Exact user problem and audience;
- SDG 3 relevance;
- Live demonstration of the frozen app's existing working features;
- What makes AI meaningful (approved source grounding, language transformation, validated quiz);
- Safety and privacy boundaries;
- Practical startup/pilot model;
- Limitations and future validation.

Make a speaker script and Q&A practice notes in chat only, without creating or editing repo files. Use only functionality already confirmed to work in the frozen version. If a feature failed before freeze, do not claim it is ready.

Rehearsal may run the frozen app as-is using its approved environment; never run tooling that changes tracked source or produces a replacement build. Do not fabricate live AI responses. Report potential demo risks truthfully.
```

**Acceptance:** [ ] frozen build unchanged, [ ] 5–7-minute script, [ ] no unsupported claims, [ ] hotspot and credentials ready privately.

---

# 12. RECOVERY PROMPTS — USE WHEN THE AGENT GETS STUCK

Each recovery prompt below is intentionally narrow. Do not run a large auto-refactor in response to a small error.

## A. Gemini key, provider or model issue

```text
STOP FEATURE WORK. Debug the live Gemini connection only. Never view, print or log actual API key values. Check configuration PRESENCE without revealing value, official google-genai SDK compatibility, configured model ID, HTTP error class and timeout. Ask me to configure or rotate credentials privately if required. Make at most one explicitly approved live public-content test request, report only success/failure and a safe error category. Do not implement a fake AI response, fallback mock or secret-logging debug endpoint. Do not move on until the endpoint is genuinely live or report the blocker.
```

## B. Blank page, broken static files, JS errors

```text
Focus exclusively on the current page-rendering failure. Check Flask route status, template path, static asset URLs, browser console errors and fetch response shape. Fix the smallest root cause. Do not change AI prompt/model/content logic. Verify GET / and /api/topics and load the page at mobile + desktop sizes. Report exact changed files and real test outcomes, then stop.
```

## C. Urdu layout broken

```text
Fix Urdu rendering only. Ensure UTF-8 files, lang='ur', dir='rtl' for content/quiz blocks, readable glyphs and mixed-script/URL layout. Do not reverse all control elements. Preserve English UI and API behavior. Test both directions and report results. No new dependencies unless explicitly approved.
```

## D. Invalid model JSON

```text
Concentrate only on model-output validation. Inspect schema and safe error categories, but do not expose secrets or private prompts. Use current SDK structured output where supported; otherwise parse/validate with explicit length and type checks. Never invent missing fields or report live_ai=true for malformed output. Add tests for missing keys, wrong array lengths, invalid correct_index and provider timeouts. Report tests and stop.
```

## E. Git tracking or possible credential exposure

```text
POTENTIAL SECRET EXPOSURE: Stop all commits and pushes. Do not open, print, paste or quote any secret values. Inspect tracked FILE NAMES and safe status metadata to identify .env, token dumps, logs, or credential-bearing artifacts. Report redacted risk and safest next steps. Ask for human approval before modifying Git history, removing files from the index or rotating a key. Do not force-push or delete evidence automatically.
```

## F. Build behind schedule

```text
We are approaching the official 3:55 PM code freeze. Freeze scope to a working minimum: two topics, one real Gemini explanation, bilingual text, trusted source and one quiz. Remove optional follow-up, voice polish and animation work from the active plan. Identify the single most critical blocker, propose only a minimal fix if there is sufficient time, run targeted tests, and prioritize a safe Git push before the deadline. Do not start an operation that may continue changing source past 3:55 PM.
```

## G. Post-freeze issue

```text
The official code freeze has passed. Do NOT edit, commit, rebuild, redeploy a replacement or change dependencies. Help us assess the current frozen version read-only, prepare an honest demo workaround involving only existing functionality, and state limitations clearly. If the frozen app cannot perform a required live AI capability, do not simulate it or claim otherwise.
```

---

# 13. TEST MATRIX AND DEFINITION OF DONE

## Must-run automated tests

| Area | Test | Expected |
|---|---|---|
| Flask | `GET /` | HTTP 200 and expected HTML |
| Topics | `GET /api/topics` | Two approved topics; no sensitive fields |
| Topic validation | Unknown `topic_id` | HTTP 400 / documented error |
| Language validation | Unknown language (e.g. `xx`) | HTTP 400 |
| Input format | Missing JSON or fields | Safe 400; no stack trace |
| AI service | Valid mock in **tests only** | Parses correct response shape |
| AI service | Invalid JSON or missing quiz | Error; not fake successful output |
| AI service | Provider timeout | Safe failure status and message |
| AI service | Missing key configuration | Safe failure; no credential text |
| Source link | Each topic's approved URL | Local source metadata preserved |
| Security | `.env`, `venv`, logs | Not tracked/staged |
| Rendering | Model text with markup-looking characters | Displayed as text, not executed HTML |
| Privacy | Submission and logs | No private patient data required or stored |

## Manual browser scenarios

- [ ] The app launches in the chosen browser on the **demo laptop**.
- [ ] Handwashing → Urdu → real AI response → source link → quiz works.
- [ ] Healthy Sleep → English → second real AI response → source link → quiz works.
- [ ] Changing language and topic clears previous quiz.
- [ ] Layout remains usable at narrow mobile width.
- [ ] Keyboard navigation reaches interactive controls and shows focus.
- [ ] Offline/failed provider state shows an honest error and a retry option.
- [ ] Browser voice gracefully degrades if unavailable.
- [ ] User is not asked for personal health records or identifiers.
- [ ] No API key appears in page source, network responses or logs.

## “Done” means all of the following

1. A real person can complete the full app journey in a browser.
2. A **real** Gemini request runs for approved public content.
3. The source is clearly attributable to the curated public URL.
4. No diagnosis, clinical claims or confidential patient information involved.
5. The app is robust to common errors; tests and smoke checks pass.
6. README and environment template let judges understand the design and run the frozen project.
7. Both organizer invitations were sent before noon, code history exists, and freeze was respected.

If one condition fails, describe it accurately rather than marking it complete.

---

# 14. README, STARTUP MODEL AND JUDGING STRATEGY

## Required README outline

Antigravity should ultimately write a concise README with:

1. Product name and SDG 3 challenge alignment.
2. Specific accessibility / health-literacy barrier and user group.
3. What works in the **frozen** prototype (do not list unimplemented features as completed).
4. Why AI is required; what source grounding and validation do.
5. Tech stack and architecture diagram.
6. Curated content sources, links and dates reviewed.
7. Installation instructions, environment placeholders and safe run commands.
8. Safe usage boundaries and privacy statement.
9. Tests and last verified outcomes.
10. Startup pilot, sustainability model and real limitations.
11. Team credits and hackathon development context.

## Credible startup path — clearly a **proposal**, not current traction

**Mission:** Help organizations distribute clear, accessible public-health education in Urdu and English.

**Potential first pilot:** Collaborate with a local educational organization, community NGO or health-education program to test comprehension outcomes for short public-health lessons.

**Who benefits:** Learners and educators; organizations that need simple bilingual education content.

**Sustainability hypothesis:** Public core features remain free, while institutions could later pay for administration, reviewed learning modules, multilingual publishing tools or impact dashboards. **These are unvalidated business ideas, not signed partnerships or current revenue.**

**Validation milestones after hackathon:** Conduct consent-based, privacy-conscious usability sessions; ask domain professionals to review content; measure comprehension and readability; test interest from community organizations; explore recurring operational costs and safeguarding requirements.

**Differentiator:** Source-grounded, plain-language Urdu/English explanations and AI-generated understanding checks, rather than generic unrestricted medical chat.

## Judge-facing one-liner for each criterion

- **Problem fit (25%):** “We solve a specific barrier: understanding trustworthy everyday health information across language and reading-level differences.”
- **Working prototype (25%):** “Select a topic, pick Urdu or English, see a live grounded AI explanation and complete a comprehension quiz.”
- **AI depth (20%):** “Gemini receives reviewed public-health source facts, returns validated structured explanations and quizzes, while the server controls trusted source attribution and errors.”
- **Design (15%):** “Responsive bilingual UI, Urdu RTL support and accessibility-first interactions; optional audio when browser-supported.”
- **Demo (15%):** “We show the frozen functioning app live, demonstrate real inference, explain limitations and answer questions without exaggerated claims.”

---

# 15. LIVE DEMONSTRATION AND PRESENTATION

## Suggested six-minute pitch script outline

**0:00–0:40 — The problem:**

“Many people find important health information hard to understand when it is technical or not in their preferred language. We focused on health literacy and accessibility, a practical part of SDG 3.”

**0:40–1:15 — Our solution:**

“SehatSaathi AI lets users select a trusted public-health topic, choose Urdu or English and receive a plain-language explanation. This is an education tool — not a diagnostic service.”

**1:15–2:45 — Live product demo:**

Open the **frozen** app, choose **Handwashing → اردو → Explain with AI**. Make the real Gemini request. Point out the structured response, source title and URL. Avoid sharing keys on screen.

**2:45–3:30 — Comprehension and inclusion:**

Answer the generated quiz; if the available browser supports audio, show read-aloud briefly. If voice was not verified, skip it.

**3:30–4:30 — Why AI / architecture:**

“Flask keeps the API key server-side. We supply approved public-health facts as context. Gemini creates a simplified explanation and quiz, while server-side validation checks the format and source metadata comes from our curated dataset.”

**4:30–5:25 — Startup path / safety:**

“We envision a free public-facing health-literacy tool and pilots with educators or community organizations. Our monetization/pilot model is a future hypothesis, not existing traction. We don't collect patient records and don't claim diagnosis.”

**5:25–6:00 — Close:**

“Better health information should be easier to understand. SehatSaathi makes general health education more accessible and testable — one trusted topic at a time.”

**Plan to finish by six minutes** so there is room for a slight live AI delay; official limit is 5–7 minutes.

## Judge Q&A — suggested factual responses

**Q: What makes this AI more than a simple chatbot?**  
A: The model receives constrained, curated public-health facts, produces two different plain-language presentations and comprehension questions, and output is validated before display. The source link is provided by the application, not improvised by AI.

**Q: Can users diagnose illness using this?**  
A: No. The current scope is general health literacy. We intentionally exclude diagnostic decisions, prescriptions and personal medical records.

**Q: How do you know the content is reliable?**  
A: The prototype grounds explanations in limited, selected official public-health information and displays the source. This reduces unsupported generation risk, but it is not a guarantee of perfect accuracy; clinical deployment would require further review and validation.

**Q: Why Urdu?**  
A: Our intended audience includes people who prefer Urdu. Native-language presentation can reduce a practical comprehension barrier. We still need to validate quality with real users.

**Q: Is there a market?**  
A: Our proposed path is a public tool plus future institutional partnerships or educational-content services; we have not claimed contracted customers or proven willingness to pay.

**Q: What data do you collect?**  
A: The MVP does not require registration or patient records. It uses public, non-sensitive source material and sends only the selected educational topic context to an AI service, plus an optional non-sensitive follow-up question if that feature was implemented.

**Q: What if the AI fails live?**  
A: The application truthfully reports service unavailability. We won't pretend a static explanation is generated live. We use the fixed, tested codebase and a prepared personal internet connection to minimize that risk.

## Operational demo checklist

- Demo laptop charged and charger packed.
- Personal hotspot/data tested; do not rely solely on campus Wi-Fi.
- Gemini API credentials already configured privately and tested in the **frozen** application.
- Browser URL and login-free app ready; no API key visible on display.
- Two preselected, non-sensitive public topics.
- Live request succeeds without developer tools / secret-bearing terminal text on projector.
- At least one teammate can explain why source grounding matters.
- The app version is exactly the final commit frozen at 3:55 PM on Tuesday.
- If organizer verifies commit history, it clearly started after kickoff.
- The team arrives in the designated rooms by 11:30 AM on Wednesday.

---

# 16. FINAL MASTER CHECKLIST

## Before **12:00 PM, Tuesday** — Disqualification prevention

- [ ] New GitHub repository created **after 10:00 AM kickoff**.
- [ ] `@httpsharis` invited and the invitation retained.
- [ ] `@anamta-JINX` invited and the invitation retained.
- [ ] Official GitHub collaboration page checked by a human.
- [ ] No copied prebuilt J.A.R.V.I.S. or third-party SaaS solution.

## Before **3:55 PM, Tuesday** — Build freeze

- [ ] Flask app runs locally.
- [ ] Two public-source topics available.
- [ ] Live Gemini integration tested on non-sensitive content.
- [ ] Urdu and English flows work.
- [ ] Quiz works and sources are displayed.
- [ ] Missing API / timeout / invalid input errors are truthful.
- [ ] `.env` and keys are not tracked; `.env.example` contains placeholders only.
- [ ] README and requirements document the working product.
- [ ] Tests and browser smoke check performed and recorded honestly.
- [ ] Final commit approved, completed and pushed **before** 3:55 PM.
- [ ] All agent sessions that could modify code terminated before freeze.
- [ ] **No edits, commits, replacement builds or post-freeze fixes.**

## Wednesday demo

- [ ] Report by **11:30 AM**; demos scheduled **12:00–4:00 PM** in rooms **6206–6209**.
- [ ] Use the exact frozen Tuesday project version.
- [ ] Show a genuine live model call.
- [ ] Pitch 5–7 minutes; finish in around 6.
- [ ] Explain problem, users, AI depth, reliability, accessibility, startup potential and limitations.
- [ ] Answer judges honestly without inflated health or commercial claims.

---

# 17. SOURCE AND REFERENCE LINKS

### Official event PDFs supplied by the user

1. **AI Hackathon STC Guidelines.pdf**, 3-page STCS participant rulebook, 17–18 November 2026 — policies on on-site work, allowed technology, Git, attendance, demonstrations and judging.
2. **AI Hackathon NICHE REVEAL STC.pdf**, 2-page official challenge release, 17 November 2026 — SDG 3 problem statement, updated collaborator handles, 12:00 PM and 3:55 PM hard deadlines, safety and judging weights.

### Public technical documentation and reference content

- Google Antigravity getting started: https://antigravity.google/docs/getting-started
- Google Antigravity overview: https://antigravity.google/docs/overview?tab=ide
- Google Gen AI Python SDK: https://googleapis.github.io/python-genai/
- Google Gen AI Python SDK source: https://github.com/googleapis/python-genai
- Gemini API content generation docs: https://ai.google.dev/api/generate-content
- WHO health literacy: https://www.who.int/news-room/fact-sheets/detail/health-literacy
- WHO plain-language communication: https://www.who.int/about/communications/understandable/plain-language
- CDC About Handwashing: https://www.cdc.gov/clean-hands/about/
- CDC About Sleep: https://www.cdc.gov/sleep/about/

### Interpretation notes

- Competition policies above are **source-derived** from the two organizer PDFs.
- Architecture, features, timelines within the official day, safety controls, API contracts, AI prompts, interface style, tests and startup plan are **proposed implementation choices**, not additional organizer requirements.
- Public-source references are for grounding the product's educational topic content; they are **not an endorsement** of this prototype by WHO, CDC or Google.
- Agent permissions are useful safeguards, but actual tool access must also be managed in Antigravity's product controls.

---

**FINAL DIRECTIVE TO THE BUILD AGENT:** Protect the competition deadlines and user credentials. Deliver the smallest reliable, source-grounded **live AI** education journey, keep it honest, and freeze it on time. A complete, working project beats a collection of unfinished features.
