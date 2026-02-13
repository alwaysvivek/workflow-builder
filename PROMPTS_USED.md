# PROMPTS_USED.md

This file documents the exact prompts used during the development of this project, along with the manual verification steps taken to ensure the quality and correctness of the AI-generated output.

## 1. Requirement Clarification
**Prompt:**
> "Without fabricating anything, return all information related to project B so that I can start building it."

**Manual Verification:**
-   **Checked against:** The original email from Vibhum Prakash.
-   **Verified:** The extracted list of features (home page, status page, history, etc.) matched the email exactly.
-   **Correction:** None needed, but I cross-referenced the hosting requirement to ensure Docker support was included if I couldn't host immediately.

## 2. Workflow Template & Action Design
**Prompt:**
> "I've settled on these 3 templates for my workflow builder:
>
> 1. Quick Understanding
> 2. Simplify
> 3. Office Assistant
>
> Suggest what actions these 3 workflows can have. Reusability is fine. Ensure each has 3 steps."

**Manual Verification:**
-   **Checked for:** Logical flow and redundancy.
-   **Filtered:** The AI suggested ~15 actions. I manually selected only 7 robust ones (`clean`, `summarize`, `simplify`, etc.) that could be reused across templates.
-   **Constraint Check:** Enforced the "exactly 3 steps" rule myself in the code, using the AI suggestions only as a creative starting point.

## 3. Manual Workflow Chaining Reasoning
**Prompt:**
> "clean_text, summarize, extract_key_points, rewrite_simpler, add_examples, classify_report, analyze_sentiment
>
> now help me explain how these can be manually chained to achieve some other task. don’t introduce new actions."

**Manual Verification:**
-   **Checked for:** Hallucinations about what the steps do.
-   **Verified:** That the combinations made sense (e.g., `clean` -> `summarize` -> `classify`).
-   **Validation:** I manually tested these chains in the UI to ensure the output of one step (e.g., a JSON classification) didn't break the input of the next (e.g., a summarizer waiting for text).

## 4. Implementation Planning
**Prompt:**
> "Given all this info, prepare an implementation plan for this project. The tech I've chosen is \"FastApi, Sqlalchemy, Postgres & Jinja\". Make sure the plan you come up with is incremental and frontend is kept at last. While designing this project, ensure you keep in mind that I'll eventually host it and will be using neon-postgres at that time."

**Manual Verification:**
-   **Checked for:** Feasibility and scope creep.
-   **Adjusted:** The AI suggested a complex React frontend. I manually decided to stick to Jinja2 templates (SSR) to keep the project "Lite" and deployment simple, contradicting the AI's initial tendency to over-engineer.
-   **Infrastructure:** Verified the Docker/Database plan suited the "hosting is important" requirement.

## 5. Database Schema Design (Initial)
**Prompt:**
> "made this database schema, verified tocheck it captures relevant details or not
> ... [Schema Details] ...
> Create a fastAPI app and a database.py with the basic routes and connection to a postgres server. 
> Ensure the creation of a .env.example & you set up the table with the correct schema as mentioned above."

**Manual Verification:**
-   **Checked for:** Foreign key constraints and data types.
-   **Fixed:** The AI initially missed the `CASCADE` delete on the workflow runs. I manually added `ondelete="CASCADE"` in the SQLAlchemy models to ensure clean deletions when resetting the DB.
-   **Security:** Verified that no actual secrets were put into `.env.example`.

## 6. Workflow Validation Logic
**Prompt:**
> "Design a workflow validaton enforcing the rule that you cannot contain the same action twice in a row."

**Manual Verification:**
-   **Checked for:** Edge cases.
-   **Verified:** Tested what happens if a user tries to submit an empty workflow or a 1-step workflow.
-   **Refined:** Added Pydantic validators (`@field_validator`) to the `WorkflowCreate` schema to strictly enforce that consecutive duplicate actions are rejected.
-   **Testing:** Validated all edge cases (valid, duplicate, invalid action) using Postman before writing automated tests.

## 7. Workflow Executor Design
**Prompt:**
> "Design a workflow executor using dummy outputs. I want to be able to chain actions (3 at a time) to create a workflow..."

**Manual Verification:**
-   **Checked for:** Infinite loops and error handling.
-   **Implemented:** I added try/catch blocks in the `LLMService` to ensure that if the API fails, the error is caught and returned as a structured JSON step error instead of crashing the entire stream.
-   **Testing:** Tested the executor end-to-end using Postman, verifying that each step's output correctly flows as input to the next step.

## 8. LLM Integration (Gemini → Groq Migration)
**Prompt:**
> "Now that workflow validation & creation is done well, I want you to implement gemini-llm for execution of each task."

**What Happened:**
-   Initially implemented Gemini as the LLM provider for workflow execution.
-   During testing, Gemini consistently failed with **quota/rate limit errors**, making it unreliable for multi-step workflows that require 3 sequential API calls per run.
-   I manually decided to switch to **Groq** (Llama 3.3 70B Versatile) because of its fast inference speed and generous free-tier limits, which are well-suited for this kind of sequential text processing task.

**Manual Verification:**
-   **Tested:** Ran multiple workflows via Postman to confirm Groq handled all 7 action types without rate limiting.
-   **Compared:** Output quality between Gemini and Groq was comparable for the task types used (summarization, cleaning, classification, etc.).

## 9. Frontend Design & Validation
**Prompt:**
> "Design a jinja based frontend for it. Here are the requirements of the frontend:
> ... [Requirements List] ..."

**Manual Verification:**
-   **Checked for:** UX and Responsiveness.
-   **Fixed:** The AI's CSS was generic. I manually tweaked the `style.css` to improve the card-based layout and ensure the navbar and grid system work correctly on mobile devices.
-   **Security:** Verified that the API Key input in the frontend wasn't logging keys to the console or saving them to local storage insecurely (switched to Session Storage).

## 10. Project Reordering
**Prompt:**
> "Reorder this project according to this directory structure:
> core/ -> pure logic
> services/ -> external services
> db/ -> database
> routers/ -> FastAPI routes
> ..."

**Manual Verification:**
-   **Checked for:** Import errors.
-   **Fixed:** Moving files broke several imports (e.g., `from db import ...`). I manually went through `main.py` and `routers/*.py` to fix the relative/absolute imports that the AI-generated refactor script missed.

## 11. Post-Audit: Security & Operational Hardening
**Prompt:**
> "Here's the audit feedback. There are 3 critical issues: Persistent XSS in history rendering, zero structured logging, and blocking sync patterns in async routes. Help me fix these without breaking anything else."

**What I Did:**
- Reviewed the audit feedback and identified the three specific issues causing the -55 technical penalty
- Prioritized fixes by severity: XSS (critical) → Logging (medium) → Async (medium)

**Manual Verification:**
- **XSS:** Traced all 5 injection points in the history template. Tested by pasting `<script>alert('xss')</script>` as input, opened Chrome DevTools, confirmed it renders as escaped text in the DOM.
- **Logging:** Ran `grep` to confirm zero `print()` statements remain. Ran the server locally and checked JSON log output on stdout for correct fields.
- **Async:** Ran `grep` to confirm no `async def` routes call blocking code.
- **Regression:** All 4 pytest tests passed.

## 12. Post-Audit: Input Sanitization & Structured Output Validation
**Prompt:**
> "Add zero-trust input sanitization at every layer and use structured output validation with Pydantic for LLM responses."

**What I Did:**
- Created `core/sanitizer.py` with `sanitize_text()` and `sanitize_name()` — strips HTML tags via regex, escapes HTML entities via `html.escape()`, trims whitespace, enforces max length
- Added Pydantic `@field_validator` on all user-facing fields: `name`, `description`, `input_text`, `api_key` in `core/schemas.py`
- Created `LLMStepOutput` Pydantic model to validate each LLM step's output (non-empty, trimmed) before passing it to the next step
- Integrated `LLMStepOutput` validation into the streaming generator in `routers/workflows.py`

**Manual Verification:**
- **Sanitization placement:** Chose the Pydantic schema layer so sanitization runs automatically for every route — no per-route logic needed    
- **Max lengths:** Set 200 (names), 1000 (descriptions), 10000 (input text), 256 (API keys) based on reasonable usage limits
- **LLM validation:** Validated *after* DB persistence but *before* next step — raw output is still saved for debugging even if validation fails
- **Regression Testing:** Ran `pytest tests/test_workflow.py tests/test_run_limit.py` — all 4 tests passed

## 13. Post-Audit: Retry/Repair Logic for LLM Steps
**Prompt:**
> "If a step fails or returns empty, automatically retry once with a modified prompt that includes the error context."

**What I Did:**
- Added a `MAX_RETRIES = 1` while-loop around the LLM stream call in `routers/workflows.py`
- On empty output, prepends "The previous attempt returned an empty response" to the prompt and retries
- Emits `{"status": "retrying"}` events for frontend visibility
- Logs retries via `logger.warning` with step/action context

**Manual Verification:**
- Verified the retry loop only triggers on empty/whitespace output, not on valid short responses
- Confirmed the repair prompt wraps the *full original prompt* (not just raw input), preserving LLM context
- **Hands-on test:** Ran the retry prompt logic in a separate Python script outside the project to verify the repair prompt construction is correct and the LLM responds meaningfully on retry. Tested with empty input to confirm the retry path activates.
- Regression Testing: All 4 tests passed

## 14. Security Audit (Round 2)
**Prompt:**
> "Do a full security edit to let me of any significant issues to harden it for production-grade."

**What Happened:**
-   Ran a full security audit across every source file (routers, core, services, templates, static JS, Dockerfile, docker-compose, tests)
-   The audit confirmed all first-round fixes (XSS, input sanitization, async blocking, structured logging) were properly implemented
-   Identified 9 additional infrastructure-level issues categorized by severity (2 high, 3 medium, 4 low)

**Manual Verification:**
-   Reviewed the audit report and triaged each issue by real-world impact
-   Decided which issues to fix immediately vs. document as known trade-offs (e.g., API key in `sessionStorage` is intentional for a bring-your-own-key app)

## 15. Production Hardening (Round 2)
**Prompt:**
> "Implement the SlowAPI boilerplate, and a CORS policy along with a CSP directive string."

**What I Did:**
-   **SlowAPI setup:** Initialized `Limiter` with `get_remote_address` in `main.py`, registered the `RateLimitExceeded` exception handler on the app, and added `@limiter.limit()` decorators on the three most abuse-prone endpoints — `/validate-key` (10/min), `/run_stream` (5/min), `/health` (30/min). Each rate-limited route handler takes `request: Request` as its first parameter (required by SlowAPI).
-   **CORS policy:** Added `CORSMiddleware` in `main.py` with an explicit origin allowlist (`localhost:8000`, `127.0.0.1:8000`, Render deployment URL). Restricted allowed methods to `GET`/`POST` and whitelisted only `Content-Type` and `x-groq-api-key` headers.
-   **CSP directive:** Added a response middleware that sets `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: strict-origin-when-cross-origin`. The CSP allows `self`, Google Fonts (`fonts.googleapis.com` for styles, `fonts.gstatic.com` for font files), and `unsafe-inline` for the inline `<script>` and `<style>` blocks used in Jinja templates.

**Manual Verification:**
-   Ran `py_compile` on all 3 modified files (`main.py`, `routers/system.py`, `routers/workflows.py`) — all passed
-   Verified the CSP allows Google Fonts (used in `layout.html` for Inter font) and `unsafe-inline` for template scripts/styles
-   Confirmed `slowapi` decorator syntax is compatible with FastAPI's `Request` parameter requirement
-   Reviewed rate limit values against realistic usage: 5 workflow runs/min is generous for a single user but prevents bulk abuse
