# MindWell — Clinical Data Assistant
### Project Documentation

**Author:** Khaled Morsi
**Stack:** Streamlit · Google Gemini · AWS Athena · SQLite · Plotly
**Data source:** SAMHSA behavioral-health public datasets (NSDUH, TEDS-A, MH-CLD, 2021–2023)

---

## 1. What this project is

MindWell is a **conversational, AI-first analytics dashboard** for U.S. behavioral-health survey data. Instead of forcing analysts to write SQL against a data lake, the user asks a plain-English clinical question ("*How does the treatment gap differ by age category in 2022?*") and MindWell:

1. Classifies the intent (schema-only question vs. data question).
2. Generates an Athena-safe SQL query with Google Gemini.
3. Executes it against the SAMHSA data lake on S3 via **AWS Athena** (serverless).
4. Summarizes the result in clinical language.
5. Renders an interactive Plotly chart plus a written clinical takeaway.
6. Logs every generated SQL query to a local **SQLite audit log** behind an admin password.

The visual language of the app mirrors the NSDUH Power BI dashboards used by the SAMHSA program team: a deep-navy canvas, muted lavender-blue chart palette, and a single teal accent color for KPIs and calls-to-action.

---

## 2. Stakeholders

| Stakeholder | Interest in the product | Why they matter |
| --- | --- | --- |
| **Clinicians & behavioral-health researchers** | Need to explore population-level trends (depression, suicidal ideation, substance use) without SQL. | They are the primary end-users — the assistant must speak *their* vocabulary. |
| **Public-health policy analysts (state / SAMHSA)** | Need reproducible, auditable evidence to justify funding, campaigns, and treatment-gap interventions. | The audit log + governed schema make outputs defensible. |
| **Health-system executives** | Need executive-ready visuals and short narratives, not raw tables. | Drives the "clinical takeaway" narrative card next to every chart. |
| **Data engineering / platform team** | Owns the S3 → Athena data lake and pays for every scan. | We use Athena's `LIMIT`-friendly aggregations and cache schema locally to keep bill low. |
| **Compliance & security officers** | Care about who ran what query, when, and against which dataset. | The password-gated Query History tab exists specifically for this audience. |
| **Product owner (Khaled Morsi)** | Needs a demonstrable, portfolio-grade AI + cloud project. | Justifies the polished dashboard aesthetic and the "why" behind every design choice. |

---

## 3. Why we chose this architecture

### Streamlit (front-end)
Fastest path from a Python analytics script to a shareable, interactive web app. No JS build step, first-class support for chat, dataframes, Plotly and forms — a huge accelerator for a data-team-authored product.

### Google Gemini 2.5 Flash (AI engine)
Chosen over GPT-4-class models because:
- Native JSON-mode-friendly output (used by `generate_insight_plan`).
- Strong SQL generation quality on relational schemas.
- Cost-per-token is materially lower, which matters for a demo/portfolio app.

### AWS Athena (query engine)
The SAMHSA files live on S3 as decoded Parquet-style views. Athena lets us query terabyte-scale public data with **zero servers** — we pay only per scan. That directly enables the "ask any question" UX without provisioning a warehouse.

### Polars → Pandas (data layer)
Athena results are read via **Polars** for speed and memory efficiency, then converted to Pandas *only* at the Plotly rendering boundary because Plotly Express is Pandas-native.

### SQLite audit log
Local, file-based, zero-config. Meets the compliance requirement ("every AI-generated query must be reviewable") without introducing another cloud service.

### Deep-navy Power-BI-style theme
Matches the visual brand of the NSDUH dashboards the stakeholders already know. Reduces cognitive load — the AI assistant looks like a natural extension of the existing BI surface, not a separate toy.

---

## 4. File-by-file walkthrough

### `app.py` — the Streamlit UI
The single entry point. Structured in numbered sections so future contributors can navigate quickly:

1. **`st.set_page_config`** — first Streamlit call. Sets tab title, favicon, `layout="wide"` to maximize screen real estate for charts, and expands the sidebar by default.
2. **Brand theme** — defines a `BRAND` dict of hex codes and injects a single large `<style>` block that themes: page background (radial-gradient navy), headers, metric cards, Streamlit containers with `border=True`, sidebar, tabs, chat bubbles, chat input, buttons, inputs, dataframes, a typing indicator, and the "clinical takeaway" callout.
3. **Plotly global template** — we register a custom template `"mindwell"` derived from `plotly_dark` with our own `colorway`, panel background, and grid colors, then set it as the default. Every chart the app renders inherits the brand automatically.
4. **Header** — brand card with logo + tagline.
5. **Sidebar with `st.form`** — the filter widgets (dataset, year, age group) are wrapped in a form so the entire app does **not** re-run every time the user touches a dropdown; it only re-runs once they click *Apply filters*. This is the "prevent UI flickering" pattern from the design brief.
6. **Helpers** — `load_schema` is decorated with `@st.cache_data` so the schema file is read from disk only once per session. `typing_indicator` renders the animated three-dot loader used while the AI is thinking.
7. **KPI strip** — four `st.metric` cards inside columns, matching the "KPI tiles across the top" convention of the reference Power BI dashboards.
8. **Tabs** — three tabs (`Assistant`, `Insights`, `Query History`) so users are not forced to scroll a single infinite page.

**Tab 1 – Assistant.** Full chat UI backed by `st.session_state.messages`. Every turn: classify intent → either answer from schema or generate + run SQL → summarize → append to the transcript and log to SQLite.

**Tab 2 – Insights.** User picks a preset topic (or types their own). Wrapped in `st.form` so the chart only regenerates on submit. The AI returns a *plan* (title + SQL + chart type + axes) which we execute and render with Plotly Express, then follow with a written "Clinical takeaway" card.

**Tab 3 – Query History.** Password-gated (env var `ADMIN_PASSWORD`, default `12345678` for demo). Shows the full SQLite audit trail with Refresh, Clear, and Re-lock controls.

### `ai_engine.py` — the LLM layer
Thin, focused wrappers around Gemini:
- `analyze_user_intent` — cheap classifier: `SCHEMA_ANSWER` vs `REQUIRES_SQL`. This routing saves both cost and latency for meta-questions like "what tables are there?".
- `answer_from_schema` — natural-language response using only the schema string.
- `generate_sql` — turns a question into a single Athena SQL query. Uses `_strip_code_fences` to defensively remove ```` ```sql ```` blocks the model may add.
- `summarize_results` — narrates a dataframe in 2–5 sentences of clinical language.
- `generate_insight_plan` — returns strict JSON describing a chart (title, SQL, chart type, x, y, color, narrative prompt). We salvage the first `{...}` block if the model wraps it in prose.
- `narrate_insight` — 2–4-sentence stakeholder-facing takeaway for the Insights tab.

### `athena_utils.py` — the query engine
- `_get_clients` — lazy AWS client factory that fails loudly if `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` are missing.
- `run_athena_query` — starts the query, polls with a **timeout** (so a runaway query can never hang the UI forever), reads the *actual* result location Athena reports back (not an assumed key), and parses the CSV with **Polars**. Returns an empty DataFrame instead of crashing on zero-row results — an important robustness fix.

### `db_utils.py` — the audit log
Plain SQLite (`query_history.db`) with one table (`query_history`) storing timestamp, user question, intent classification, generated SQL, status, error message, and row count. Functions: `init_db`, `log_query`, `get_history(limit=500)`, `clear_history`. Chosen for zero operational overhead.

### `schema.txt`
Copy of the `DESCRIBE` output for the three SAMHSA views. Loaded once per session and injected into every AI prompt as grounding context. Keeping it as a file (not a DB call) means the AI never has to touch Athena just to understand the schema — big cost win.

### `.streamlit/config.toml`
Sets Streamlit's own theme (`base = "dark"`, primary `#4fb3c9`, background `#0a1a2f`) so any element we don't manually restyle still lands in-brand. `gatherUsageStats = false` for privacy, `headless = true` for production.

### `requirements.txt`
`streamlit`, `boto3` (AWS), `polars` + `pandas` (data), `google-genai` (Gemini), `python-dotenv` (secrets from `.env`), `s3fs` (S3 file access), `plotly` (charts).

---

## 5. How to run it

```bash
pip install -r requirements.txt

# .env in project root
GEMINI_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
ATHENA_DATABASE=samhsa_master_db
ATHENA_S3_BUCKET=samhsa-datalake-2021-2023-depi
ADMIN_PASSWORD=change-me

streamlit run app.py
```

---

## 6. Design principles applied (from the professional-Streamlit brief)

| Principle | Where it lives in the code |
| --- | --- |
| `st.set_page_config` first, wide layout | `app.py` §1 |
| Bordered containers for grouping | KPI strip, Insights card, Query History gate |
| Advanced structural layout (tabs) | `st.tabs([...])` §8 |
| Batch inputs via `st.form` | Sidebar workspace form, Insights form |
| Clean brand theme via `config.toml` | `.streamlit/config.toml` |
| Smart caching to prevent flicker | `@st.cache_data` on `load_schema` |
| Custom CSS for polish | Single injected `<style>` block in §2 |

---

## 7. What could come next

- Wire the sidebar filters into the actual SQL prompts (currently context-only).
- Replace SQLite audit log with DynamoDB for multi-user deployments.
- Add a "Compare with previous year" toggle on every insight.
- Row-level access control per state / provider for HIPAA-adjacent workloads.
- Export the current chat as a PDF clinical brief.
