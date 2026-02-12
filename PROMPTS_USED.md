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
