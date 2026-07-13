import os
import re
import json
from google import genai
import streamlit as st  


_api_key = st.secrets["GEMINI_API_KEY"]

if not _api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. Set it in your Streamlit Secrets before running the app."
    )

client = genai.Client(api_key=_api_key)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _strip_code_fences(text):
    text = text.strip()
    text = re.sub(r"^```(?:sql|json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def analyze_user_intent(question, schema_info):
    prompt = f"""
    You are an AI Data Analyst. Analyze the user's question and determine the best action.

    Database Schema Info:
    {schema_info}

    User Question: '{question}'

    Respond with ONLY one of these two options:
    1. If the question is general about what the data is, list of tables, description of columns, or can be fully answered using JUST the schema info provided above, reply with: SCHEMA_ANSWER
    2. If the question requires counting rows, calculating metrics, extracting specific records, or querying the actual database, reply with: REQUIRES_SQL
    """
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()


def answer_from_schema(question, schema_info):
    prompt = f"""
    You are a professional clinical Data Analyst. The user is asking a general question about the dataset structure or metadata.
    Answer clearly and comprehensively using ONLY the provided schema information.

    Schema Info:
    {schema_info}

    User Question: '{question}'
    """
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text


def generate_sql(question, schema_info):
    prompt = f"""
    You are a professional Data Analyst.
    Given this database schema:
    {schema_info}

    Write a single Athena SQL query to answer the user's question: '{question}'
    Return ONLY the raw SQL code. Do not include markdown blocks like ```sql or any text other than the query itself.
    """
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return _strip_code_fences(response.text)


def summarize_results(df, question):
    prompt = f"""
    Explain the findings of this data in simple, friendly clinical language to answer: '{question}'.
    Keep it concise (2-5 sentences). Avoid heavy jargon.
    Data (first rows):
    {str(df.head(10))}
    """
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text


# ------------------------------------------------------------------
# NEW: Insights generator — returns SQL + chart spec + narrative
# ------------------------------------------------------------------
def generate_insight_plan(topic, schema_info):
    """
    Ask the model to design ONE interactive insight: a SQL query plus a
    recommended chart. Returns a dict:
        { "title", "sql", "chart_type", "x", "y", "color", "narrative_prompt" }
    chart_type in: bar, line, pie, scatter, area
    """
    prompt = f"""
You are a senior behavioral-health data analyst. Design ONE insight for the topic below.

Schema:
{schema_info}

Topic: '{topic}'

Return ONLY valid minified JSON with keys:
- "title": short chart title
- "sql": a single Athena SQL query. MUST return at most ~30 rows and include
  aggregated numeric column(s) suitable for plotting. Do NOT use markdown.
- "chart_type": one of "bar", "line", "pie", "scatter", "area"
- "x": column name for x axis (or category for pie)
- "y": column name for y axis (or value for pie)
- "color": optional column name for grouping, or null
- "narrative_prompt": short instruction we will later use to describe the result

No explanation, no code fences, JSON only.
"""
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    raw = _strip_code_fences(response.text)
    try:
        return json.loads(raw)
    except Exception:
        # try to salvage first {...} block
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


def narrate_insight(df, plan):
    prompt = f"""
You are a clinical data analyst. In 2-4 sentences, describe the key takeaway
from this chart for a healthcare stakeholder. Be specific with numbers.

Chart title: {plan.get('title')}
Data:
{str(df.head(20))}
"""
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text
