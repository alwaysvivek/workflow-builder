# AI_NOTES.md

## Overview

AI tools were used selectively during the **planning and design phase** of this project to improve clarity, reduce ambiguity, and validate design choices.
All final architectural decisions, workflow constraints, and implementation details were reviewed and finalized manually.

---

## 1. Requirement Clarification

**Prompt Used:**

> “Without fabricating anything, return all information related to project B.”

**Purpose:**
Extract and organize all explicit requirements for Project B from the original email communication.

**Why AI Was Used:**
To avoid misinterpreting requirements and to ensure complete coverage of expectations before beginning system design and implementation.

**What I Verified Myself:**

* Cross-checked the extracted requirements directly against the original email
* Ensured no inferred or fabricated requirements were introduced
* Confirmed alignment with submission, hosting, and evaluation criteria

**Tool Used:**
ChatGPT (OpenAI)

---

## 2. Workflow Template & Action Design

**Prompt Used:**

> “I've settled on these 3 templates for my workflow builder:
>
> 1. Quick Understanding
> 2. Simplify
> 3. Office Assistant
>
> Suggest what actions these 3 workflows can have. Reusability is fine. Ensure each has 3 steps.”

**Purpose:**
Explore possible action sets for three predefined workflow templates while keeping workflows constrained to exactly three steps.

**Why AI Was Used:**
To assist with brainstorming reasonable and reusable action combinations and to sanity-check logical step ordering.

**What I Came Up With Myself:**

* The decision to enforce **exactly three steps** per workflow
* The choice of **template goals** (Quick Understanding, Simplify, Office Assistant)
* The constraint that **actions must be reusable and composable**
* The final decision on **which actions to keep and which to exclude**
* The naming and responsibility boundaries of each action

**Final Actions Selected (Manually Validated):**

* `clean_text`
* `summarize`
* `extract_key_points`
* `rewrite_simpler`
* `add_examples`
* `classify`
* `analyze_sentiment`

Each action has a single responsibility and a fixed, hard-coded prompt.

**Tool Used:**
ChatGPT (OpenAI)

---

## 3. Manual Workflow Chaining Reasoning

**Prompt Used:**

> “clean_text, summarize, extract_key_points, rewrite_simpler, add_examples, classify_report, analyze_sentiment
>
> now help me explain how these can be manually chained to achieve some other task. don’t introduce new actions.”

**Purpose:**
Validate that the same fixed set of actions could be manually chained to support additional use cases beyond predefined templates.

**Why AI Was Used:**
To reason about composability and ensure that different action sequences still produce coherent and meaningful outputs.

**What I Came Up With Myself:**

* The rule that **manual workflows must also use exactly three steps**
* The decision to **not allow new or user-defined actions**
* The enforcement of **fixed prompts per action** for determinism
* The choice to reuse the **same execution engine** for templates and manual workflows
* The UX decision to optionally suggest a template if a manual chain matches one

**Manual Validation Performed:**

* Confirmed that each chained workflow produces sensible output
* Ensured no action depends on hidden context
* Verified that outputs of each step are safe as inputs for the next step

**Tool Used:**
ChatGPT (OpenAI)

---

## 4. LLM Used in the Application

**Model:**
Llama 3.3 70B Versatile

**Provider:**
Groq

**Reason for Selection:**

* **Speed**: Groq provides exceptionally fast inference, which is critical for a smooth user experience in a multi-step workflow application.
* **Cost**: Efficient and cost-effective for high-volume text processing.
* **Performance**: Llama 3.3 70B offers strong instruction-following capabilities, ensuring `clean_text`, `summarize`, and other actions are performed accurately without the need for a more expensive model.

---

## 5. Coding Assistance

**Tools Used:**
- **ChatGPT (OpenAI)**: Used for planning, requirement analysis, brainstorming workflow templates, and reasoning about action composability.
- **Antigravity (Google)**: Used for hands-on coding, debugging, and file-level implementation. Primarily used **Gemini 3** for fast iteration and **Claude Opus** for complex multi-file edits.

**Why Different Tools for Different Tasks:**
- ChatGPT excels at conversational reasoning and design-phase tasks — extracting requirements from emails, comparing action sets, and thinking through edge cases. It was the right fit for the early planning prompts (1–4).
- Antigravity is an agentic coding assistant that can read, edit, and run code directly in the project. This made it far more efficient for implementation tasks like setting up FastAPI routes, refactoring the project structure, fixing imports, and writing tests.

**Purpose:**
Assisted with generating boilerplate code, setting up the project structure (FastAPI, SQLAlchemy) & connection with database. Also used for writing and structuring README.md, as AI is well-suited for organizing documentation clearly and consistently.

---

## 6. Post-Audit Fixes

After receiving the technical audit (scored 40.5/100 with a -55 penalty for operational gaps), I fixed all three flagged issues plus implemented the Growth Roadmap items. The initial submission focused on core functionality and real-time streaming. After receiving the audit, I used the feedback to add production-grade hardening — security, logging, and validation.

### XSS Fix

The history page was rendering user data (`input_text`, `output_text`, `step_type`) directly via `innerHTML` with no escaping — classic stored XSS.

I couldn't just swap to `textContent` because the history cards are built as full HTML structures (divs, spans, pre tags with CSS classes) inside template literals. Using `textContent` would've destroyed the layout. Jinja `| e` wasn't applicable either since history rendering is client-side via `fetch('/runs')` + JS, not server-side templates.

So I added an `escapeHtml()` helper that converts `& < > " '` to HTML entities, and wrapped every dynamic value with it (5 injection points total). Also switched the error catch block to `textContent` since that one is just plain text.

Tested by opening the history page, inspecting the DOM in Chrome DevTools, and confirming that `<script>alert('xss')</script>` renders as literal escaped text, not as an executable script.

**AI used for:** Writing the `escapeHtml()` function. I manually went through the `history.html` template literal line by line to find all 5 injection points — `input_text`, `output_text`, `step_type`, status badge, and the run ID header. Also checked `app.js` to make sure its `innerHTML` usages only insert hardcoded action labels, not user data. Tested in Chrome DevTools by pasting script tags as workflow input and confirming they render as escaped text.

### Structured JSON Logging

The app had literally one `print(f"Error: {e}")` statement and nothing else. No request logging, no structured output.

I went with Python's stdlib `logging` module instead of adding structlog or loguru — didn't want new dependencies for something this straightforward. Created `core/logging_config.py` with a custom `JsonFormatter` that outputs single-line JSON with `timestamp`, `level`, `logger`, `message`, and contextual fields. Added request logging middleware in `main.py` that captures method, path, status code, and duration for every request. Replaced all `print()` calls with proper logger calls.

Tested by running the server locally, hitting different endpoints, and checking that the JSON output on stdout had the right fields and format.

**AI used for:** Generating the `JsonFormatter` class boilerplate. I decided which fields to log (went with `timestamp`, `level`, `message`, `method`, `path`, `status_code`, `duration_ms` — the standard set you'd want for debugging production issues). Ran `grep -rn 'print('` across all source files to make sure none were left. Tested by running the server, hitting GET and POST endpoints, and reading the JSON lines in stdout to confirm they parse correctly.

### Async Blocking Fix

`run_workflow_stream` and `validate_key` were both `async def` but called blocking sync code (Groq SDK). This blocks the event loop.

I just removed the `async` keyword. FastAPI runs `def` routes in a threadpool automatically, so blocking calls are fine. Much simpler than wrapping everything in `run_in_threadpool()` or switching to `AsyncGroq` (which would've meant rewriting the stream logic).

Verified via `grep` that no remaining `async def` routes have blocking code. The `async def` routes in `pages.py` just return Jinja templates which is correct.

**AI used for:** Confirming that removing `async` was the right approach for FastAPI. I ran `grep -rn 'async def' routers/` to check which routes were still async — only `pages.py` (Jinja template rendering, which is non-blocking). Verified the Groq SDK returns sync iterators, not async ones, so keeping `async def` was the actual bug. Ran all 4 tests after the change.

### Input Sanitization (Defense in Depth)

Even with frontend escaping, a direct API call could bypass it and store malicious payloads. So I added server-side sanitization at the Pydantic schema layer — every user-facing field (`name`, `description`, `input_text`, `api_key`) goes through `sanitize_text()` or `sanitize_name()` via `@field_validator` before any route logic runs. These strip HTML tags, escape entities, trim whitespace, and enforce max lengths.

Created `core/sanitizer.py` using stdlib `html.escape()` and `re.sub` for tag stripping — no new dependencies.

**AI used for:** Generating the `sanitize_text()` and `sanitize_name()` functions. I decided to put sanitization at the Pydantic `@field_validator` layer instead of per-route — this way any new route that uses these schemas gets automatic sanitization without remembering to call it. Picked the max lengths based on realistic usage: 200 for workflow names, 1000 for descriptions, 10000 for input text (LLMs can handle long input), 256 for API keys.

### Structured Output Validation (Pydantic)

LLM step outputs were being passed as raw strings between steps with no checks. If the LLM returned empty, it'd silently chain garbage through the workflow.

Added an `LLMStepOutput` Pydantic model in `core/schemas.py` that validates each step's output is non-empty before passing it to the next step. Integrated into the streaming generator in `workflows.py`. I validate after DB persistence but before the next step — so we still have the raw output saved for debugging even if validation fails.

**AI used for:** Writing the `LLMStepOutput` Pydantic model. I decided to validate after saving the step to the DB but before passing output to the next step — this way even if validation fails, we still have the raw LLM response saved for debugging. Content emptiness is the critical check since a blank output would produce garbage in all downstream steps.

### Retry/Repair Logic

If an LLM step returns empty output, it now retries once with a repair prompt: "The previous attempt returned an empty response. Please try again carefully." + the original prompt.

Kept it simple — a while loop with `MAX_RETRIES = 1`. Emits a `{"status": "retrying"}` event so the frontend knows what's happening. Logs each retry via `logger.warning`. If both attempts fail, Pydantic validation catches it downstream.

Chose a while-loop over `tenacity` or similar retry libraries — no need for new dependencies for a single retry.

Tested the retry prompt logic separately in a standalone Python script to make sure the prompt construction was right and the LLM actually responds meaningfully on retry.

**AI used for:** Implementing the retry loop structure. I tested the repair prompt in a separate Python script to make sure the LLM actually gives a meaningful response when you prepend "The previous attempt returned an empty response" to the original prompt. Also verified that the `{"status": "retrying"}` SSE event is compatible with the existing frontend event parser so it doesn't break the streaming UI.

### Removed Dead Code

Cleaned up `services/llm.py` — removed an unused `async def run_step_stream()` function that had blocking sync code inside it. The streaming logic lives inline in `workflows.py` now. Also removed its unused imports (`json`, `PROMPTS`).

---

## 7. Production Hardening (Round 2)

After the first round of post-audit fixes, a second security audit identified additional infrastructure-level gaps. These were all addressed:

### Exception Detail Leakage Fix

The `/health` endpoint was returning raw exception messages (database host, port, driver errors) in the HTTP response via `f"Database connection failed: {str(e)}"`. The `/run_stream` endpoint was streaming raw Groq SDK errors via `str(e)`. Both now return generic messages ("Service unavailable" / "Workflow execution failed. Please try again.") while the full stack trace is still logged server-side via `exc_info=True`.

**AI used for:** Identifying the leakage points during the audit. I changed the error messages to generic strings and verified the logger still captures the full exception.

### Rate Limiting (SlowAPI)

Added `slowapi` for per-IP rate limiting on the three most abuse-prone endpoints:
- `/validate-key`: 10 requests/minute (prevents API key brute-forcing)
- `/run_stream`: 5 requests/minute (prevents unlimited LLM cost)
- `/health`: 30 requests/minute (prevents monitoring abuse)

Chose `slowapi` because it wraps `limits` and integrates directly with FastAPI via decorators — no custom middleware needed. The limiter uses `get_remote_address` for IP extraction.

**AI used for:** Setting up the SlowAPI boilerplate (Limiter init, exception handler registration, decorator syntax). I decided on the specific rate limits based on realistic usage patterns.

### CORS Policy

Added `CORSMiddleware` with an explicit allowlist: `localhost:8000`, `127.0.0.1:8000`, and the Render deployment URL. Only `GET` and `POST` methods are allowed. Only `Content-Type` and `x-groq-api-key` headers are whitelisted.

**AI used for:** Generating the middleware config. I selected the specific origins and headers to whitelist.

### Security Headers

Added a response middleware that sets four security headers on every response:
- `X-Content-Type-Options: nosniff` — prevents MIME-type sniffing
- `X-Frame-Options: DENY` — prevents clickjacking via iframes
- `Referrer-Policy: strict-origin-when-cross-origin` — limits referrer leakage
- `Content-Security-Policy` — restricts script/style/font/image sources to self and Google Fonts (needed for the Inter font)

**AI used for:** Generating the CSP directive string. I tailored the policy to allow Google Fonts (used in `layout.html`) and `unsafe-inline` for the inline `<script>` and `<style>` blocks in the templates.

### Docker Hardening

- Added a non-root `appuser` in the Dockerfile (`RUN adduser --disabled-password --gecos "" appuser` + `USER appuser`)
- Added `--proxy-headers` to the uvicorn CMD for correct client IP logging behind reverse proxies

