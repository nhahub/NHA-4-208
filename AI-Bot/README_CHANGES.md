# MindWell Data Assistant — What Changed

## ⚠️ First: rotate your credentials
The `.env` you uploaded (as `_env.crash`) had real AWS keys and a real Gemini
key in plain text inside this chat. Please **rotate/revoke both** (AWS IAM
console + Google AI Studio) and use `.env.example` → copy to `.env` with the
new values going forward. Don't re-upload the real `.env` file anywhere.

## Setup
```bash
cd ~/Desktop/"depi project"
# put these new files in, then:
cp .env.example .env        # fill in your real (rotated) keys
pip install -r requirements.txt
streamlit run app.py
```

## Bugs fixed
- **`athena_utils.py`**: it assumed the result CSV always lived at
  `athena_results/{execution_id}.csv`. It now reads the *actual*
  `OutputLocation` Athena reports back — more robust if workgroups/output
  settings ever change. Also added a query timeout (was an infinite poll
  loop) and it no longer crashes on a query that returns zero rows.
- **`ai_engine.py`**: the Gemini client now uses the key explicitly from
  `.env` (clearer error if missing) and generated SQL gets any stray
  ```sql fences stripped automatically, since models don't always follow
  "no markdown" instructions perfectly.

## New: `db_utils.py`
A tiny SQLite wrapper (`query_history.db`, created automatically on first
run) that logs every question, the AI's intent decision, the SQL it ran (if
any), status, error message, and row count.

## `app.py` — two tabs
1. **💬 Ask MindWell** — the chat. Mental-health-themed styling, message
   history above, `st.chat_input` pinned to the bottom. While the AI is
   thinking, a bouncing 🧠 with rotating funny captions shows. The SQL query
   is **never shown here** — only the plain-language answer and the result
   table.
2. **🔒 Query History** — locked behind the password `12345678` (change it
   via `ADMIN_PASSWORD` in `.env`). Once unlocked it shows the full SQL
   query history pulled straight from `query_history.db`, with refresh/clear
   controls.

## Notes / things worth double-checking on your end
- The password gate is a simple UI check, not real authentication — fine for
  a personal/small-team tool, but don't treat it as a security boundary for
  sensitive data.
- `query_history.db` will sit next to `app.py`. Back it up if you care about
  keeping the log long-term, and consider adding it to `.gitignore` too.
