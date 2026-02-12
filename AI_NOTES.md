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
