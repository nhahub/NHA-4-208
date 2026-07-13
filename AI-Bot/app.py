"""
MindWell Clinical Data Assistant
--------------------------------
Streamlit front-end for an AI-powered exploration of SAMHSA behavioral-health
survey data (NSDUH, TEDS-A, MH-CLD). Visual language matches the NSDUH Power BI
dashboards: deep navy canvas, muted lavender-blue chart palette, teal accent.
"""

import os
import streamlit as st
import plotly.express as px
import plotly.io as pio

from athena_utils import run_athena_query
from ai_engine import (
    analyze_user_intent,
    answer_from_schema,
    generate_sql,
    summarize_results,
    generate_insight_plan,
    narrate_insight,
)
from db_utils import init_db, log_query, get_history, clear_history

# ------------------------------------------------------------------
# 1. PAGE CONFIG  (must be the first Streamlit command)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="MindWell • Behavioral Health Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345678")
SCHEMA_FILE_PATH = "schema.txt"

# ------------------------------------------------------------------
# 2. BRAND THEME — dark (deep navy) + light palettes with runtime toggle
# ------------------------------------------------------------------
BRAND_DARK = {
    "bg":        "#0a1a2f",
    "panel":     "#132745",
    "panel_2":   "#1b3050",
    "border":    "#243a5e",
    "ink":       "#e8ebf3",
    "ink_soft":  "#a9b4cc",
    "accent":    "#4fb3c9",
    "accent_2":  "#7aa7d9",
    "danger":    "#e26a6a",
    "good":      "#5ac8a0",
    "header_grad": "linear-gradient(135deg, #132745 0%, #1b3050 100%)",
    "sidebar_grad": "linear-gradient(180deg, #0a1a2f 0%, #0f2140 100%)",
    "user_msg_grad": "linear-gradient(135deg, #1b3050, #24365a)",
    "user_msg_border": "#2c4670",
    "btn_ink": "#0a1a2f",
}
BRAND_LIGHT = {
    "bg":        "#f4f7fb",
    "panel":     "#ffffff",
    "panel_2":   "#f0f4fa",
    "border":    "#d7deea",
    "ink":       "#0e1a2b",
    "ink_soft":  "#5b6a83",
    "accent":    "#2b8fa6",
    "accent_2":  "#3e6fb0",
    "danger":    "#c94a4a",
    "good":      "#2f9d78",
    "header_grad": "linear-gradient(135deg, #ffffff 0%, #eaf1fb 100%)",
    "sidebar_grad": "linear-gradient(180deg, #ffffff 0%, #eef3fb 100%)",
    "user_msg_grad": "linear-gradient(135deg, #eaf1fb, #dbe6f5)",
    "user_msg_border": "#c3d3ec",
    "btn_ink": "#ffffff",
}

CHART_PALETTE_DARK  = ["#8892b8", "#b8bfd4", "#e8ebf3", "#4fb3c9", "#7aa7d9", "#c9a84c"]
CHART_PALETTE_LIGHT = ["#3e6fb0", "#7aa7d9", "#2b8fa6", "#8892b8", "#c9a84c", "#5b6a83"]

# Toggle state (default: dark)
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

IS_DARK = st.session_state.theme_mode == "Dark"
BRAND = BRAND_DARK if IS_DARK else BRAND_LIGHT
CHART_PALETTE = CHART_PALETTE_DARK if IS_DARK else CHART_PALETTE_LIGHT

st.markdown(
    f"""
    <style>
    :root {{
        --mw-bg:       {BRAND["bg"]};
        --mw-panel:    {BRAND["panel"]};
        --mw-panel-2:  {BRAND["panel_2"]};
        --mw-border:   {BRAND["border"]};
        --mw-ink:      {BRAND["ink"]};
        --mw-ink-soft: {BRAND["ink_soft"]};
        --mw-accent:   {BRAND["accent"]};
        --mw-accent-2: {BRAND["accent_2"]};
    }}

    /* Global */
    .stApp {{
        background:
          radial-gradient(1400px 600px at 15% -10%, rgba(79,179,201,0.10) 0%, transparent 60%),
          radial-gradient(1200px 500px at 100% 0%, rgba(122,167,217,0.10) 0%, transparent 55%),
          var(--mw-bg) !important;
        color: var(--mw-ink) !important;
    }}
    html, body, [class*="css"], .stMarkdown, p, span, li, label {{
        color: var(--mw-ink) !important;
        font-family: "Inter","SF Pro Text",-apple-system,system-ui,sans-serif;
    }}
    h1, h2, h3, h4 {{ color: var(--mw-ink) !important; letter-spacing: -0.01em; }}
    .stCaption, small {{ color: var(--mw-ink-soft) !important; }}
    hr {{ border-color: var(--mw-border) !important; }}

    /* Header brand card */
    .mw-header {{
        background: {BRAND["header_grad"]};
        border: 1px solid var(--mw-border);
        border-radius: 18px;
        padding: 20px 26px;
        display: flex; align-items: center; gap: 16px;
        box-shadow: 0 10px 30px -18px rgba(0,0,0,0.6);
        margin-bottom: 18px;
    }}
    .mw-logo {{
        width: 50px; height: 50px; border-radius: 14px;
        background: linear-gradient(135deg, var(--mw-accent), var(--mw-accent-2));
        color: {BRAND["btn_ink"]}; display:flex; align-items:center; justify-content:center;
        font-size: 24px; font-weight: 700;
        box-shadow: 0 8px 22px -8px rgba(79,179,201,0.6);
    }}
    .mw-header h1 {{ margin: 0; font-size: 22px; }}
    .mw-header p  {{ margin: 2px 0 0; color: var(--mw-ink-soft) !important; font-size: 13px; }}

    /* KPI / metric cards */
    div[data-testid="stMetric"] {{
        background: var(--mw-panel);
        border: 1px solid var(--mw-border);
        border-radius: 14px;
        padding: 14px 18px;
        box-shadow: 0 4px 18px -12px rgba(0,0,0,0.6);
    }}
    div[data-testid="stMetricLabel"] p {{ color: var(--mw-ink-soft) !important; font-size: 12px; }}
    div[data-testid="stMetricValue"]   {{ color: var(--mw-ink) !important; }}

    /* Containers with border=True */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--mw-panel);
        border: 1px solid var(--mw-border) !important;
        border-radius: 14px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {BRAND["sidebar_grad"]} !important;
        border-right: 1px solid var(--mw-border);
    }}
    section[data-testid="stSidebar"] * {{ color: var(--mw-ink) !important; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        border-bottom: 1px solid var(--mw-border);
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: var(--mw-ink-soft) !important;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        border: 1px solid transparent; border-bottom: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--mw-panel) !important;
        color: var(--mw-accent) !important;
        border-color: var(--mw-border);
        box-shadow: 0 -2px 0 0 var(--mw-accent) inset;
    }}

    /* Chat messages */
    div[data-testid="stChatMessage"] {{
        background: var(--mw-panel) !important;
        border: 1px solid var(--mw-border);
        border-radius: 14px;
        padding: 12px 16px !important;
        margin-bottom: 10px;
        color: var(--mw-ink) !important;
        box-shadow: 0 2px 12px -8px rgba(0,0,0,0.5);
        animation: mw-fade 0.35s ease-out;
    }}
    div[data-testid="stChatMessage"] * {{ color: var(--mw-ink) !important; }}
    div[data-testid="stChatMessage"][data-testid*="user"] {{
        background: {BRAND["user_msg_grad"]} !important;
        border-color: {BRAND["user_msg_border"]};
    }}
    @keyframes mw-fade {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Chat input */
    div[data-testid="stChatInput"] textarea {{
        background: var(--mw-panel) !important;
        color: var(--mw-ink) !important;
        border: 1px solid var(--mw-border) !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stChatInput"] textarea:focus {{
        border-color: var(--mw-accent) !important;
        box-shadow: 0 0 0 3px rgba(79,179,201,0.20) !important;
    }}

    /* Buttons */
    .stButton>button, .stDownloadButton>button {{
        background: linear-gradient(135deg, var(--mw-accent), var(--mw-accent-2));
        color: {BRAND["btn_ink"]} !important;
        border-radius: 10px;
        border: none;
        padding: 9px 18px;
        font-weight: 700;
        transition: transform .15s ease, box-shadow .15s ease;
    }}
    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 8px 22px -10px rgba(79,179,201,0.55);
    }}

    /* Inputs / selects */
    input, textarea,
    .stTextInput input,
    .stSelectbox div[role="button"],
    .stMultiSelect div[role="button"] {{
        color: var(--mw-ink) !important;
        background: var(--mw-panel) !important;
        border-color: var(--mw-border) !important;
    }}

    /* Dataframe */
    .stDataFrame, .stDataFrame * {{ color: var(--mw-ink) !important; }}

    /* Typing indicator */
    .mw-typing {{
        display: inline-flex; align-items: center; gap: 6px;
        padding: 10px 14px; background: var(--mw-panel);
        border: 1px solid var(--mw-border); border-radius: 14px;
        color: var(--mw-ink-soft) !important; font-size: 14px;
        animation: mw-fade 0.3s ease-out;
    }}
    .mw-typing .dot {{
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--mw-accent); opacity: 0.35;
        animation: mw-pulse 1.2s infinite ease-in-out;
    }}
    .mw-typing .dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .mw-typing .dot:nth-child(3) {{ animation-delay: 0.30s; }}
    @keyframes mw-pulse {{
        0%, 80%, 100% {{ opacity: 0.25; transform: scale(0.9); }}
        40%           {{ opacity: 1;    transform: scale(1.15); }}
    }}

    /* Insight callout */
    .mw-card {{
        background: var(--mw-panel);
        border: 1px solid var(--mw-border);
        border-left: 4px solid var(--mw-accent);
        border-radius: 12px;
        padding: 16px 18px;
        margin-top: 14px;
        box-shadow: 0 4px 18px -14px rgba(0,0,0,0.7);
    }}
    .mw-card h4 {{ margin: 0 0 6px 0; color: var(--mw-accent) !important; font-size: 14px; text-transform: uppercase; letter-spacing: .06em; }}
    .mw-card p  {{ margin: 0; color: var(--mw-ink) !important; font-size: 14px; line-height: 1.55; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 3. PLOTLY GLOBAL TEMPLATE — matches dashboard aesthetic
# ------------------------------------------------------------------
_base_template = "plotly_dark" if IS_DARK else "plotly_white"
pio.templates["mindwell"] = pio.templates[_base_template]
pio.templates["mindwell"].layout.update(
    paper_bgcolor=BRAND["panel"],
    plot_bgcolor=BRAND["panel"],
    font=dict(color=BRAND["ink"], family="Inter"),
    colorway=CHART_PALETTE,
    xaxis=dict(gridcolor=BRAND["border"], zerolinecolor=BRAND["border"]),
    yaxis=dict(gridcolor=BRAND["border"], zerolinecolor=BRAND["border"]),
)
pio.templates.default = "mindwell"

# ------------------------------------------------------------------
# 4. HEADER
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="mw-header">
      <div class="mw-logo">🧠</div>
      <div>
        <h1>MindWell — Clinical Data Assistant</h1>
        <p>AI-driven exploration of SAMHSA behavioral-health surveys — NSDUH · TEDS-A · MH-CLD</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 5. SIDEBAR — appearance + about
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎨 Appearance")
    mode = st.radio(
        "Theme",
        ["Dark", "Light"],
        index=0 if IS_DARK else 1,
        horizontal=True,
        key="theme_radio",
    )
    if mode != st.session_state.theme_mode:
        st.session_state.theme_mode = mode
        st.rerun()

    st.divider()
    st.markdown("### About")
    st.caption(
        "MindWell blends generative AI with Amazon Athena to translate "
        "plain-English clinical questions into governed SQL and executive-ready visuals."
    )


# ------------------------------------------------------------------
# 6. HELPERS
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_schema(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Warning: Schema file not found."


def typing_indicator(placeholder, label="Analyzing clinical data"):
    placeholder.markdown(
        f"""
        <div class="mw-typing">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          <span style="margin-left:6px;">{label}…</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


schema_info = load_schema(SCHEMA_FILE_PATH)

# ------------------------------------------------------------------
# 7. KPI STRIP  (visual anchor at the top, matches BI dashboards)
# ------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Datasets connected", "3", "NSDUH · TEDS-A · MH-CLD")
with kpi2:
    st.metric("Survey years", "2021 – 2023")
with kpi3:
    st.metric("Query engine", "AWS Athena", "serverless")
with kpi4:
    st.metric("AI model", "Gemini 2.5", "reasoning + SQL")

st.write("")

# ------------------------------------------------------------------
# 8. TABS
# ------------------------------------------------------------------
tab_chat, tab_insights, tab_history = st.tabs(
    ["💬  Assistant", "📊  Insights", "🔒  Query History"]
)

# ==================================================================
# TAB 1 — CHAT ASSISTANT
# ==================================================================
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello, I'm **MindWell**, your clinical data assistant. "
                    "Ask about the SAMHSA mental-health and substance-use datasets — "
                    "e.g. *\"How many adults reported a past-year depressive episode in 2022?\"*"
                ),
                "df": None,
            }
        ]

    chat_box = st.container(height=540, border=True)
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🧠" if msg["role"] == "assistant" else "🧑"):
                st.markdown(msg["content"])
                if msg.get("df") is not None and msg["df"].height > 0:
                    st.dataframe(msg["df"], use_container_width=True)

    user_query = st.chat_input("Ask a clinical question about the data…")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query, "df": None})

        loader_slot = st.empty()
        typing_indicator(loader_slot)

        intent, sql_used, result_df = None, None, None
        try:
            intent = analyze_user_intent(user_query, schema_info)

            if "SCHEMA_ANSWER" in intent:
                answer_text = answer_from_schema(user_query, schema_info)
                log_query(user_query, intent, sql_query=None, status="success", row_count=None)
            else:
                sql_used = generate_sql(user_query, schema_info)
                result_df = run_athena_query(sql_used)
                answer_text = summarize_results(result_df, user_query)
                log_query(
                    user_query, intent, sql_query=sql_used, status="success",
                    row_count=result_df.height if result_df is not None else 0,
                )

            loader_slot.empty()
            st.session_state.messages.append(
                {"role": "assistant", "content": answer_text, "df": result_df}
            )
        except Exception as e:
            loader_slot.empty()
            log_query(user_query, intent or "UNKNOWN", sql_query=sql_used,
                      status="error", error_message=str(e))
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I hit a snag looking that up. Could you rephrase the question?",
                "df": None,
            })

        st.rerun()


# ==================================================================
# TAB 2 — INSIGHTS  (AI-generated interactive charts)
# ==================================================================
with tab_insights:
    st.subheader("AI-generated clinical insights")
    st.caption("Pick a topic — MindWell writes the SQL, queries Athena, and visualizes the finding.")

    preset_topics = [
        "Trends in past-year depressive episodes by age group",
        "Top 10 states by mental-health treatment admissions",
        "Substance use disorder prevalence by gender",
        "Suicidal thoughts vs Kessler-6 distress score",
        "Primary substance distribution among admissions",
    ]

    with st.container(border=True):
        with st.form("insight_form", border=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                topic = st.selectbox("Choose an insight to generate", preset_topics, index=0)
                custom = st.text_input("…or describe your own insight", "")
            with c2:
                st.write("")
                st.write("")
                run_it = st.form_submit_button("✨ Generate insight", use_container_width=True)
            chosen_topic = custom.strip() if custom.strip() else topic

    if run_it:
        slot = st.empty()
        typing_indicator(slot, "Designing analysis")
        try:
            plan = generate_insight_plan(chosen_topic, schema_info)
            typing_indicator(slot, "Running query on Athena")
            df_pl = run_athena_query(plan["sql"])
            log_query(f"[INSIGHT] {chosen_topic}", intent="INSIGHT",
                      sql_query=plan["sql"], status="success",
                      row_count=df_pl.height if df_pl is not None else 0)
            slot.empty()

            if df_pl is None or df_pl.height == 0:
                st.warning("Query returned no rows.")
            else:
                df = df_pl.to_pandas()

                with st.container(border=True):
                    st.markdown(f"### {plan.get('title', chosen_topic)}")

                    chart_type = plan.get("chart_type", "bar").lower()
                    x, y, color = plan.get("x"), plan.get("y"), plan.get("color")

                    try:
                        if chart_type == "line":
                            fig = px.line(df, x=x, y=y, color=color, markers=True)
                        elif chart_type == "pie":
                            fig = px.pie(df, names=x, values=y, hole=0.55)
                        elif chart_type == "scatter":
                            fig = px.scatter(df, x=x, y=y, color=color)
                        elif chart_type == "area":
                            fig = px.area(df, x=x, y=y, color=color)
                        else:
                            fig = px.bar(df, x=x, y=y, color=color)
                    except Exception:
                        fig = px.bar(df)

                    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=440)
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("View data table"):
                        st.dataframe(df, use_container_width=True)

                narrative = narrate_insight(df_pl, plan)
                st.markdown(
                    f"<div class='mw-card'><h4>Clinical takeaway</h4><p>{narrative}</p></div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            slot.empty()
            st.error(f"Couldn't generate this insight: {e}")


# ==================================================================
# TAB 3 — PASSWORD-PROTECTED QUERY HISTORY
# ==================================================================
with tab_history:
    st.subheader("Query History (Admin Only)")
    st.caption("Stored locally in `query_history.db` (SQLite) — never uploaded.")

    if "history_unlocked" not in st.session_state:
        st.session_state.history_unlocked = False

    if not st.session_state.history_unlocked:
        with st.container(border=True):
            pwd = st.text_input("Enter admin password", type="password")
            if st.button("Unlock", use_container_width=False):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.history_unlocked = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
    else:
        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            st.success("Unlocked — showing full query history.")
        with col_b:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with col_c:
            if st.button("🗑️ Clear", use_container_width=True):
                clear_history()
                st.rerun()

        rows = get_history()
        if not rows:
            st.info("No queries logged yet.")
        else:
            st.dataframe(rows, use_container_width=True, height=560)

        if st.button("Lock this tab again"):
            st.session_state.history_unlocked = False
            st.rerun()
