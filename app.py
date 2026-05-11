import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import streamlit.components.v1 as components
from google import genai
import json


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    

hero_img_base64 = get_base64_image("Blue Page.jpg")
# logos_img_base64 = get_base64_image("Blue Page.jpg")

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Campaign Presentation",
    page_icon="📊",
    layout="wide",
)

# --------------------------------------------------
# PLACEHOLDER CONTENT
# --------------------------------------------------
APP_TITLE = "Campaign Performance Overview"
APP_SUBTITLE = "Interactive presentation replacing the static slide deck."

HOME_SHORT_SUMMARY = """
- Campaigns can be viewed interactively
- Bubble chart highlights relative channel positioning and scale
- Weekly sales decomposition shows how RSV is built over time
- RSV contribution split shows movement and share by driver
- Weekly media spends shows spend landscape with RSV overlay
- Media YoY shows shifts in investment, RSV, and ROI across years
"""

HOME_NOTE = """
Use the navigation tabs to explore each section of the presentation.
"""

CAMPAIGN_INSIGHT = """
Channels in the upper-right quadrant indicate stronger overall performance,
while larger bubbles reflect higher contribution or spend.
"""

WEEKLY_SALES_INSIGHT = """
Base contribution remains the dominant component across the time series,
while media and promotion-driven variation can be observed across specific periods.
"""

RSV_SPLIT_INSIGHT = """
Baseline remains the dominant contribution driver, while media and promotion shares vary across years.
The waterfall highlights which factors are driving the relative change between the two periods.
"""

WEEKLY_MEDIA_INSIGHT = """
Media investments intensify in selected periods, while total RSV can be tracked
in parallel to understand spend-response patterns over time.
"""

MEDIA_YOY_INSIGHT = """
TM shows the largest absolute investment and RSV scale, while sub-channels
can be compared across ST/LT mix and overall ROI progression over time.
"""

MEDIA_SPEND_MIX_INSIGHT = """
The mix shifts over time across campaigns, while the ROI line helps compare
whether changes in allocation are associated with stronger or weaker returns.
"""

CAMPAIGN_ROI_INSIGHT = """
Comparing the two periods highlights how campaign mix shifted and whether
higher investment concentration translated into stronger RSV ROI.
"""

CROSS_SYNERGY_INSIGHT = """
The darker cells highlight stronger interactions between selected channel pairs,
helping identify combinations that may work well together.
"""

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>

        /* =========================
        GLOBAL
        ========================= */
        .stApp,
        div[data-testid="stAppViewContainer"],
        header[data-testid="stHeader"],
        section[data-testid="stHeader"] {
            background-color: #F7F8FA !important;
            color: #111111;
        }

        header {
            box-shadow: none !important;
        }

        .block-container {
            padding-top: 0.6rem;
            padding-bottom: 3.6rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
            max-width: 100%;
        }

        /* =========================
        TITLES
        ========================= */
        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            color: #111111;
            margin-bottom: 0.15rem;
            line-height: 1.1;
        }

        .hero-subtitle {
            font-size: 0.9rem;
            color: #666666;
            margin-bottom: 0.7rem;
        }

        /* =========================
        TABS (FIXED + BOLD)
        ========================= */
        div[data-testid="stTabs"] {
            background-color: #F7F8FA !important;
            margin-bottom: 0.5rem !important;
        }

        div[data-testid="stTabs"] [role="tablist"] {
            gap: 0.4rem !important;
            align-items: flex-end !important;
            padding-top: 0.2rem !important;
            padding-bottom: 0.2rem !important;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            # font-family: "Trebuchet MS", Arial, sans-serif !important;
            font-family: inherit
            font-size: .85rem !important;
            font-weight: 700 !important;
            line-height: 1.3 !important;
            color: #444444 !important;
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0.55rem 0.9rem 0.45rem 0.9rem !important;
            min-height: 42px !important;
            height: auto !important;
            transition: all 0.2s ease-in-out !important;
        }

        div[data-testid="stTabs"] button[role="tab"]:hover {
            color: #000000 !important;
        }

        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #D80000 !important;
            font-weight: 800 !important;
            border-bottom: 3px solid #D80000 !important;
        }

        /* Force inner text bold */
        div[data-testid="stTabs"] button[role="tab"] p {
            # font-family: "Trebuchet MS", Arial, sans-serif !important;
            font-family: inherit
            font-size: .85rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }

        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {
            font-weight: 800 !important;
            color: #D80000 !important;
        }

        /* =========================
        INPUTS
        ========================= */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        .stMultiSelect div[data-baseweb="select"] > div {
            background-color: rgba(255, 255, 255, 0.78) !important;
            border: 1px solid rgba(0, 0, 0, 0.10) !important;
            color: #111111 !important;
            border-radius: 6px !important;
            min-height: 36px !important;
        }

        label {
            color: #333333 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
        }

        /* =========================
        NOTES / INSIGHTS
        ========================= */
        .compact-note {
            font-size: 0.95rem;
            font-weight: 600;
            color: #333333;
            line-height: 1.4;
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            margin-top: 0.4rem;
        }

        /* =========================
        METRICS
        ========================= */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.60);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 8px;
            padding: 0.65rem 0.85rem;
        }

        /* =========================
        FOOTER
        ========================= */
        .ppt-footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background: #FF1414;
            color: white;
            z-index: 9999;
            padding: 0.65rem 1rem;
            font-size: 0.72rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .ppt-footer-left {
            display: flex;
            align-items: center;
        }

        .ppt-footer-right {
            font-size: 0.68rem;
            opacity: 0.95;
            white-space: nowrap;
        }

        footer {visibility: hidden;}
       
        /* =========================
        CHART CARD
        ========================= */
        .chart-card {
            background: #FFFFFF;
            border: 1px solid rgba(0, 0, 0, 0.06);
            border-radius: 18px;
            padding: 0.9rem 1rem 0.5rem 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            margin-top: 0.35rem;
            margin-bottom: 0.9rem;
        }

        .chart-card-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: #222222;
            margin-bottom: 0.25rem;
        }

        .chart-card-subtitle {
            font-size: 0.88rem;
            color: #6B7280;
            margin-bottom: 0.7rem;
        }
        /* =========================
        EXECUTIVE SUMMARY KPI CARDS
        ========================= */
        .exec-summary-meta {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.15rem;
        }

        .exec-summary-meta b {
            color: #2A2F3A;
            font-weight: 800;
        }

        .kpi-card {
            background: linear-gradient(180deg, #284D78 0%, #2F6497 100%);
            border-radius: 20px;
            min-height: 220px;
            padding: 1.4rem 1.2rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.10);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
        }

        .kpi-card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: rgba(255,255,255,0.88);
            line-height: 1.15;
            margin-top: 0.3rem;
        }

        .kpi-card-value {
            font-size: 2.05rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.15;
            word-break: break-word;
            margin-bottom: 0.2rem;
        }
        
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ppt-footer">
        <div class="ppt-footer-left"></div>
        <div class="ppt-footer-right">
            Copyright © 2025 Incorporated — Confidential
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
# --------------------------------------------------
# AI / OLLAMA HELPERS
# --------------------------------------------------
GEMINI_MODEL = "gemini-2.5-flash"
client = genai.Client(api_key="AIzaSyAOe1x-L9soZE9UIL_rZ0PJCb967XxRhwI")

def build_rsv_split_context(df: pd.DataFrame, selected_sheet: str) -> dict:
    preview_df = df.copy()

    if len(preview_df) > 12:
        preview_df = preview_df.head(12)

    numeric_summary = {}
    for col in df.columns:
        if col != "variables":
            numeric_col = pd.to_numeric(df[col], errors="coerce")
            if numeric_col.notna().any():
                numeric_summary[col] = {
                    "sum": float(numeric_col.sum()),
                    "min": float(numeric_col.min()),
                    "max": float(numeric_col.max()),
                }

    return {
        "tab": "RSV Contribution Split",
        "chart_type": "waterfall + stacked bar",
        "title": selected_sheet,
        "columns": df.columns.tolist(),
        "row_count": int(len(df)),
        "numeric_summary": numeric_summary,
        "data_preview": preview_df.to_dict(orient="records")
    }


def ask_gemini_stream(question: str, context: dict, model: str = GEMINI_MODEL):
    system_prompt = """
You are an AI insights assistant embedded inside a Streamlit dashboard.

Rules:
- Answer ONLY from the supplied dashboard context.
- Do NOT invent numbers, causes, or external business facts.
- If something cannot be determined from the context, say so clearly.
- Keep the response concise, polished, and presentation-ready.
- Prefer this structure when relevant:
  1. Direct answer
  2. 2-4 key insights
  3. 1 executive takeaway
"""

    prompt = f"""
{system_prompt}

User question:
{question}

Dashboard context:
{json.dumps(context, default=str, indent=2)}
"""

    response = client.models.generate_content_stream(
        model=model,
        contents=prompt,
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text

def reset_rsv_ai_chat_if_sheet_changed(sheet_name: str):
    signature = f"rsv_split::{sheet_name}"
    prev_signature = st.session_state.get("_rsv_ai_signature")

    if prev_signature != signature:
        st.session_state["_rsv_ai_signature"] = signature
        st.session_state["rsv_ai_chat_messages"] = [
            {
                "role": "assistant",
                "content": "Ask me about the RSV Contribution Split currently shown on screen."
            }
        ]

def render_rsv_ai_chat_compact():
    if "rsv_ai_chat_messages" not in st.session_state:
        st.session_state["rsv_ai_chat_messages"] = [
            {
                "role": "assistant",
                "content": "Ask me about the RSV Contribution Split currently shown on screen."
            }
        ]

    st.markdown(
        """
        <style>
        .rsv-ai-row-shell {
            background: rgba(240,240,240,0.92);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 0px;
            padding: 18px 16px;
            margin-top: 16px;
            margin-bottom: 10px;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
        }

        .rsv-ai-title-inline {
            font-size: 1.15rem;
            font-weight: 800;
            color: #222222;
            white-space: nowrap;
            padding-top: 10px;
        }

        .rsv-ai-answer {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 12px 14px;
            margin-top: 12px;
            color: #222222;
            font-size: 0.95rem;
            line-height: 1.45;
        }

        .rsv-ai-progress-label {
            font-size: 0.88rem;
            font-weight: 600;
            color: #555555;
            margin-top: 8px;
            margin-bottom: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="rsv-ai-row-shell">', unsafe_allow_html=True)

    row_cols = st.columns([1.4, 1.4, 1.7, 1.7, 1.3, 3.6, 0.9])

    with row_cols[0]:
        st.markdown('<div class="rsv-ai-title-inline">AI Insight Assistant</div>', unsafe_allow_html=True)

    sample_prompts = [
        "Summarize this view",
        "What is the biggest driver?",
        "What changed the most?",
        "Give me 3 insights",
    ]

    for i, txt in enumerate(sample_prompts):
        with row_cols[i + 1]:
            if st.button(txt, key=f"rsv_compact_prompt_{i}", use_container_width=True):
                st.session_state["_rsv_pending_prompt"] = txt

    with row_cols[5]:
        typed_prompt = st.text_input(
            "Ask about this RSV Contribution Split",
            key="rsv_compact_text_input",
            label_visibility="collapsed",
            placeholder="Ask about this RSV Contribution Split"
        )

    with row_cols[6]:
        send_clicked = st.button("Send", key="rsv_send_btn", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    prompt = None
    if st.session_state.get("_rsv_pending_prompt"):
        prompt = st.session_state.pop("_rsv_pending_prompt")
    elif send_clicked and typed_prompt.strip():
        prompt = typed_prompt.strip()

    answer_container = st.container()

    if prompt:
        context = st.session_state.get("rsv_ai_context", {})

        st.session_state["rsv_ai_chat_messages"].append({
            "role": "user",
            "content": prompt
        })

        with answer_container:
            progress_text = st.empty()
            progress_bar = st.progress(0)
            answer_placeholder = st.empty()

            answer = ""
            partial = ""

            try:
                progress_steps = [8, 16, 24, 33, 41, 50, 58, 66, 74, 82, 90]
                progress_messages = [
                    "Reading chart context...",
                    "Understanding contribution drivers...",
                    "Preparing insight response...",
                    "Generating answer..."
                ]

                step_index = 0
                for chunk in ask_gemini_stream(prompt, context, model=GEMINI_MODEL):
                    partial += chunk

                    if step_index < len(progress_steps):
                        pct = progress_steps[step_index]
                        label = progress_messages[min(step_index // 3, len(progress_messages) - 1)]
                        progress_text.markdown(
                            f'<div class="rsv-ai-progress-label">{label} {pct}%</div>',
                            unsafe_allow_html=True
                        )
                        progress_bar.progress(pct)
                        step_index += 1

                    answer_placeholder.markdown(
                        f'<div class="rsv-ai-answer">{partial}</div>',
                        unsafe_allow_html=True
                    )

                answer = partial.strip() if partial.strip() else "I could not generate a response."

                progress_text.markdown(
                    '<div class="rsv-ai-progress-label">Done 100%</div>',
                    unsafe_allow_html=True
                )
                progress_bar.progress(100)

            except Exception as e:
                answer = "AI assistant is currently busy. Please try again in a few seconds."
                progress_text.markdown(
                    '<div class="rsv-ai-progress-label">Request failed</div>',
                    unsafe_allow_html=True
                )
                answer_placeholder.markdown(
                    f'<div class="rsv-ai-answer">{answer}</div>',
                    unsafe_allow_html=True
                )

        st.session_state["rsv_ai_chat_messages"].append({
            "role": "assistant",
            "content": answer
        })

    else:
        last_answer = None
        msgs = st.session_state.get("rsv_ai_chat_messages", [])
        for msg in reversed(msgs):
            if msg["role"] == "assistant" and msg["content"] != "Ask me about the RSV Contribution Split currently shown on screen.":
                last_answer = msg["content"]
                break

        if last_answer:
            st.markdown(
                f'<div class="rsv-ai-answer">{last_answer}</div>',
                unsafe_allow_html=True
            )

    
# --------------------------------------------------
# GENERIC HELPERS
# --------------------------------------------------
def normalize_cell(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def money_to_millions(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric / 1_000_000


def extract_table_from_positions(raw_df: pd.DataFrame, header_row_idx: int, header_positions: dict) -> pd.DataFrame:
    ordered_headers = sorted(header_positions.items(), key=lambda x: x[1])
    output_columns = [header for header, _ in ordered_headers]

    rows = []
    for r in range(header_row_idx + 1, len(raw_df)):
        row = raw_df.iloc[r]
        vals = []
        row_dict = {}
        for header, col_idx in ordered_headers:
            val = row.iloc[col_idx] if col_idx < len(row) else None
            row_dict[header] = val
            vals.append(val)

        if all(pd.isna(v) or str(v).strip() == "" for v in vals):
            break

        rows.append(row_dict)

    if not rows:
        return pd.DataFrame(columns=output_columns)

    return pd.DataFrame(rows)


def render_section_card(title: str, body: str):
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <div class="muted-text">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_section(title: str, description: str):
    st.markdown(f'<div class="hero-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Section structure added — content to be connected next</div>',
        unsafe_allow_html=True,
    )
    render_section_card("Section Description", description)
    st.markdown(
        """
        <div class="placeholder-box">
            This section has been added to the app structure.
            The chart logic, Excel sheet mapping, and final formatting can be connected next.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_compact_note(text: str):
    st.markdown(f'<div class="compact-note">{text}</div>', unsafe_allow_html=True)

def render_kpi_card(title: str, value: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-card-title">{title}</div>
            <div class="kpi-card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_campaign_roi_display_table(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()

    display_df["Investment ($ M)"] = display_df.apply(
        lambda r: f"{r['investment_m']:.1f}M    {r['investment_pct']:.1f}%"
        if pd.notna(r["investment_m"]) and pd.notna(r["investment_pct"])
        else "",
        axis=1,
    )
    display_df["RSV ($ M)"] = display_df["rsv_m"].apply(lambda x: f"{x:.1f}M" if pd.notna(x) else "")
    display_df["RSV ROI"] = display_df["roi"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "")

    display_df = display_df.rename(columns={"campaign": "Campaign"})
    return display_df[["Campaign", "Investment ($ M)", "RSV ($ M)", "RSV ROI"]]

def prepare_channel_roi_display_table(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()

    display_df["channel_display"] = display_df["channel"]
    display_df.loc[display_df["channel"].duplicated(), "channel_display"] = ""

    display_df["Investment ($ Thousand)"] = display_df.apply(
        lambda r: f"{int(r['investment_k']) if pd.notna(r['investment_k']) else ''}    {r['investment_pct']:.1f}%"
        if pd.notna(r["investment_k"]) and pd.notna(r["investment_pct"])
        else "",
        axis=1,
    )
    display_df["RSV ($ Thousand)"] = display_df["rsv_k"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else ""
    )
    display_df["RSV ROI"] = display_df["roi"].apply(
        lambda x: f"{x:.1f}" if pd.notna(x) else ""
    )

    return display_df[["channel_display", "platform", "Investment ($ Thousand)", "RSV ($ Thousand)", "RSV ROI"]]

# --------------------------------------------------
# SECTION-SPECIFIC PARSERS
# --------------------------------------------------
def extract_weekly_media_blocks(raw_df: pd.DataFrame):
    line_df = None
    spend_df = None

    for row_idx in range(len(raw_df)):
        row_values = [normalize_cell(v) for v in raw_df.iloc[row_idx].tolist()]

        if line_df is None and "date" in row_values and "value" in row_values:
            header_positions = {
                "date": row_values.index("date"),
                "value": row_values.index("value"),
            }
            candidate = extract_table_from_positions(raw_df, row_idx, header_positions)
            if not candidate.empty:
                candidate["date"] = pd.to_datetime(candidate["date"], errors="coerce")
                candidate["value"] = clean_numeric(candidate["value"])
                candidate = candidate.dropna(subset=["date", "value"]).sort_values("date")
                if not candidate.empty:
                    line_df = candidate

        if spend_df is None and "date" in row_values and "national media" in row_values and "retail media" in row_values:
            header_positions = {
                "date": row_values.index("date"),
                "national media": row_values.index("national media"),
                "retail media": row_values.index("retail media"),
            }
            if "national recruitment" in row_values:
                header_positions["national recruitment"] = row_values.index("national recruitment")

            candidate = extract_table_from_positions(raw_df, row_idx, header_positions)
            if not candidate.empty:
                candidate["date"] = pd.to_datetime(candidate["date"], errors="coerce")
                spend_cols = [c for c in candidate.columns if c != "date"]
                for col in spend_cols:
                    candidate[col] = clean_numeric(candidate[col])
                candidate = candidate.dropna(subset=["date"]).sort_values("date")
                candidate[spend_cols] = candidate[spend_cols].fillna(0)
                if not candidate.empty:
                    spend_df = candidate

    if line_df is None or spend_df is None:
        return None

    return {"line_df": line_df, "spend_df": spend_df}

# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------
@st.cache_data
def load_campaign_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    campaign_data = {}

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("campaign"):
            continue

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        for col in ["xvalues", "yvalues", "size"]:
            if col in df.columns:
                df[col] = clean_numeric(df[col])

        required_cols = ["channel", "xvalues", "yvalues", "size"]
        if any(col not in df.columns for col in required_cols):
            continue

        df = df.dropna(subset=required_cols).copy()
        df["campaign"] = sheet_name
        campaign_data[sheet_name] = df

    if not campaign_data:
        raise ValueError("No valid Campaign sheets found. Sheet names must start with 'Campaign'.")

    return campaign_data


@st.cache_data
def load_weekly_sales_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    weekly_sales_data = {}

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("weeklysales"):
            continue

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        column_map = {
            "baseline": "base",
            "promo": "promotions",
            "promotion": "promotions",
            "national_media": "national media",
            "national_recruitment": "national recruitment",
            "retail_media": "retail media",
            "retailmedia": "retail media",
            "trade": "retail media",
        }
        df = df.rename(columns=column_map)

        if "week" not in df.columns:
            continue

        df["week"] = pd.to_datetime(df["week"], errors="coerce")

        for col in df.columns:
            if col != "week":
                df[col] = clean_numeric(df[col])

        df = df.dropna(subset=["week"]).sort_values("week")
        weekly_sales_data[sheet_name] = df

    return weekly_sales_data


@st.cache_data
def load_rsv_split_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    rsv_split_data = {}

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("rsvcontribution"):
            continue

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        rename_map = {
            "national_media": "national media",
            "national_recruitment": "national recruitment",
            "retail_media": "retail media",
            "promotion": "promotions",
            "promo": "promotions",
        }
        df = df.rename(columns=rename_map)

        seen = {}
        cols = []
        for col in df.columns:
            if col in seen:
                seen[col] += 1
                cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                cols.append(col)
        df.columns = cols

        for col in df.columns:
            if col != "variables":
                df[col] = clean_numeric(df[col])

        rsv_split_data[sheet_name] = df

    return rsv_split_data


@st.cache_data
def load_weekly_media_spends_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None, header=None)

    weekly_media_data = {}

    for sheet_name, raw_df in workbook.items():
        clean_name = str(sheet_name).strip().lower()
        if not clean_name.startswith("weeklymediaspends"):
            continue

        result = extract_weekly_media_blocks(raw_df)
        if result is not None:
            weekly_media_data[sheet_name] = result

    return weekly_media_data


@st.cache_data
def load_media_yoy_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    media_yoy_data = {}
    required_cols = [
        "year", "media group", "spend", "rsv st", "rsv lt",
        "rsv total", "roi st", "roi lt", "roitotal"
    ]

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("mediainvrsvroiyoy"):
            continue

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        if not all(col in df.columns for col in required_cols):
            continue

        df = df[required_cols].copy()
        df = df.dropna(subset=["year", "media group"]).copy()

        df["year"] = df["year"].astype(str).str.strip()
        df["media group"] = df["media group"].astype(str).str.strip()

        money_cols = ["spend", "rsv st", "rsv lt", "rsv total"]
        for col in money_cols:
            df[col] = money_to_millions(df[col])

        roi_cols = ["roi st", "roi lt", "roitotal"]
        for col in roi_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        group_order = ["TM", "NM", "RM", "NR"]
        year_order = ["2023", "2024", "2025"]

        df = df[df["media group"].isin(group_order)].copy()
        df = df[df["year"].isin(year_order)].copy()

        df["media group"] = pd.Categorical(df["media group"], categories=group_order, ordered=True)
        df["year"] = pd.Categorical(df["year"], categories=year_order, ordered=True)
        df = df.sort_values(["media group", "year"])

        media_yoy_data[sheet_name] = df

    return media_yoy_data


@st.cache_data
def load_media_spend_mix_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    main_sheet = None
    roi_sheet = None

    for sheet_name, df in workbook.items():
        clean_name = str(sheet_name).strip().lower()

        if clean_name.startswith("mediaspendmix_main"):
            main_sheet = df.copy()
        elif clean_name.startswith("mediaspendmix_roi"):
            roi_sheet = df.copy()

    if main_sheet is None or roi_sheet is None:
        return None

    main_sheet.columns = main_sheet.columns.str.strip().str.lower()

    required_main_cols = ["half_year", "campaign", "spend_value", "spend_pct"]
    if not all(col in main_sheet.columns for col in required_main_cols):
        return None

    main_sheet = main_sheet[required_main_cols].copy()
    main_sheet = main_sheet.dropna(subset=["half_year", "campaign"]).copy()

    main_sheet["half_year"] = main_sheet["half_year"].astype(str).str.strip()
    main_sheet["campaign"] = main_sheet["campaign"].astype(str).str.strip()
    main_sheet["spend_value"] = pd.to_numeric(main_sheet["spend_value"], errors="coerce")
    main_sheet["spend_pct"] = pd.to_numeric(main_sheet["spend_pct"], errors="coerce")
    main_sheet["spend_value_m"] = main_sheet["spend_value"] / 1_000_000

    roi_sheet.columns = roi_sheet.columns.str.strip().str.lower()

    required_roi_cols = ["half_year", "roi"]
    if not all(col in roi_sheet.columns for col in required_roi_cols):
        return None

    roi_sheet = roi_sheet[required_roi_cols].copy()
    roi_sheet = roi_sheet.dropna(subset=["half_year"]).copy()

    roi_sheet["half_year"] = roi_sheet["half_year"].astype(str).str.strip()
    roi_sheet["roi"] = pd.to_numeric(roi_sheet["roi"], errors="coerce")

    half_year_order = roi_sheet["half_year"].dropna().tolist()
    if not half_year_order:
        half_year_order = main_sheet["half_year"].dropna().unique().tolist()

    main_sheet["half_year"] = pd.Categorical(main_sheet["half_year"], categories=half_year_order, ordered=True)
    roi_sheet["half_year"] = pd.Categorical(roi_sheet["half_year"], categories=half_year_order, ordered=True)

    main_sheet = main_sheet.sort_values(["half_year", "campaign"])
    roi_sheet = roi_sheet.sort_values("half_year")

    return {
        "main": main_sheet,
        "roi": roi_sheet,
        "half_year_order": half_year_order,
    }


@st.cache_data
def load_campaign_roi_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    campaign_roi_data = {}

    required_cols = ["period", "campaign", "investment_m", "investment_pct", "rsv_m", "roi"]

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("campaignroi"):
            continue

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        if not all(col in df.columns for col in required_cols):
            continue

        df = df[required_cols].copy()
        df = df.dropna(subset=["period", "campaign"]).copy()

        df["period"] = df["period"].astype(str).str.strip()
        df["campaign"] = df["campaign"].astype(str).str.strip()

        for col in ["investment_m", "investment_pct", "rsv_m", "roi"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        campaign_order = ["HW", "IFL", "Kt", "Others", "Total"]
        period_order = ["H1 2025", "H2 2025"]

        if set(df["campaign"]).intersection(campaign_order):
            df["campaign"] = pd.Categorical(df["campaign"], categories=campaign_order, ordered=True)

        if set(df["period"]).intersection(period_order):
            df["period"] = pd.Categorical(df["period"], categories=period_order, ordered=True)

        df = df.sort_values(["period", "campaign"])
        campaign_roi_data[sheet_name] = df

    return campaign_roi_data

@st.cache_data
def load_channel_roi_data():
    """
    Load Channel Level RSV ROI data.

    Expected sheet name prefix:
    - ChannelROI

    Expected columns:
    - period
    - channel
    - platform
    - investment_k
    - investment_pct
    - rsv_k
    - roi
    """
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    channel_roi_data = {}
    required_cols = ["period", "channel", "platform", "investment_k", "investment_pct", "rsv_k", "roi"]

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("channelroi"):
            continue

        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        if not all(col in df.columns for col in required_cols):
            continue

        df = df[required_cols].copy()
        df = df.dropna(subset=["period", "channel", "platform"]).copy()

        df["period"] = df["period"].astype(str).str.strip()
        df["channel"] = df["channel"].astype(str).str.strip()
        df["platform"] = df["platform"].astype(str).str.strip()

        for col in ["investment_k", "investment_pct", "rsv_k", "roi"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        period_order = ["H1 2025", "H2 2025"]
        if set(df["period"]).intersection(period_order):
            df["period"] = pd.Categorical(df["period"], categories=period_order, ordered=True)

        channel_roi_data[sheet_name] = df.sort_values(["period", "channel", "platform"])

    return channel_roi_data


@st.cache_data
def load_cross_synergy_data():
    file_path = "summary_gemini.xlsx"
    workbook = pd.read_excel(file_path, sheet_name=None)

    cross_synergy_data = {}

    for sheet_name, df in workbook.items():
        if not str(sheet_name).strip().lower().startswith("crosssynergy"):
            continue

        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()

        if df.shape[1] < 2:
            continue

        from_col = df.columns[0]
        df = df.rename(columns={from_col: "from_channel"})
        df["from_channel"] = df["from_channel"].astype(str).str.strip()

        value_cols = [col for col in df.columns if col != "from_channel"]
        for col in value_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df = df.dropna(subset=["from_channel"]).copy()
        cross_synergy_data[sheet_name] = df

    return cross_synergy_data


def build_combined_campaign_df(campaign_data: dict) -> pd.DataFrame:
    return pd.concat(list(campaign_data.values()), ignore_index=True)

# --------------------------------------------------
# CHART BUILDERS
# --------------------------------------------------
def create_media_yoy_roi_chart(df: pd.DataFrame):
    group_order = ["TM", "NM", "RM", "NR"]
    year_order = ["2023", "2024", "2025"]

    plot_df = df.copy()
    plot_df["year"] = plot_df["year"].astype(str)
    plot_df["media group"] = pd.Categorical(plot_df["media group"], categories=group_order, ordered=True)
    plot_df["year"] = pd.Categorical(plot_df["year"], categories=year_order, ordered=True)
    plot_df = plot_df.sort_values(["media group", "year"])

    roi_long = pd.concat([
        plot_df[["media group", "year", "roi st"]].rename(columns={"roi st": "value"}).assign(component="ST"),
        plot_df[["media group", "year", "roi lt"]].rename(columns={"roi lt": "value"}).assign(component="LT"),
    ])

    roi_long["label"] = roi_long["value"].apply(lambda v: f"{v:.1f}" if pd.notna(v) and v > 0 else "")

    fig = px.bar(
        roi_long,
        x="value",
        y="year",
        color="component",
        facet_row="media group",
        orientation="h",
        barmode="stack",
        text="label",
        category_orders={"media group": group_order, "year": year_order[::-1]},
        color_discrete_map={"ST": "#1A0DAB", "LT": "#9E9E9E"},
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
    )

    for trace in fig.data:
        if trace.name == "ST":
            trace.textfont = dict(color="white", size=11)
        else:
            trace.textfont = dict(color="#222222", size=11)

    fig.update_layout(
        template="plotly_white",
        height=430,
        margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
        title=dict(text="Total RSV ROIs", x=0.5, font=dict(size=15)),
        showlegend=False,
    )

    fig.update_yaxes(
        matches=None,
        showgrid=False,
        title_text=None,
        showticklabels=False
)
    fig.update_yaxes(showticklabels=True)
    fig.update_xaxes(showgrid=False, zeroline=False, title_text=None)

    fig.for_each_annotation(lambda a: a.update(text="") if "media group=" in a.text else None)

    return fig

def create_media_yoy_rsv_chart(df: pd.DataFrame):
    group_order = ["TM", "NM", "RM", "NR"]
    year_order = ["2023", "2024", "2025"]

    plot_df = df.copy()
    plot_df["year"] = plot_df["year"].astype(str)
    plot_df["media group"] = pd.Categorical(plot_df["media group"], categories=group_order, ordered=True)
    plot_df["year"] = pd.Categorical(plot_df["year"], categories=year_order, ordered=True)
    plot_df = plot_df.sort_values(["media group", "year"])

    rsv_long = pd.concat([
        plot_df[["media group", "year", "rsv st"]].rename(columns={"rsv st": "value"}).assign(component="ST"),
        plot_df[["media group", "year", "rsv lt"]].rename(columns={"rsv lt": "value"}).assign(component="LT"),
    ])

    rsv_long["label"] = rsv_long["value"].apply(lambda v: f"${v:.1f}M" if pd.notna(v) and v > 0 else "")

    fig = px.bar(
        rsv_long,
        x="value",
        y="year",
        color="component",
        facet_row="media group",
        orientation="h",
        barmode="stack",
        text="label",
        category_orders={"media group": group_order, "year": year_order[::-1]},
        color_discrete_map={"ST": "#1A0DAB", "LT": "#9E9E9E"},
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
    )

    for trace in fig.data:
        if trace.name == "ST":
            trace.textfont = dict(color="white", size=11)
        else:
            trace.textfont = dict(color="#222222", size=11)

    fig.update_layout(
        template="plotly_white",
        height=430,
        margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
        title=dict(text="RSV Contribution", x=0.5, font=dict(size=15)),
        showlegend=False,
    )

    fig.update_yaxes(
        matches=None,
        showgrid=False,
        title_text=None,
        showticklabels=False
)
    fig.update_xaxes(showgrid=False, zeroline=False, title_text=None)

    fig.for_each_annotation(lambda a: a.update(text="") if "media group=" in a.text else None)

    return fig

def create_media_yoy_spend_chart(df: pd.DataFrame):
    group_order = ["TM", "NM", "RM", "NR"]
    year_order = ["2023", "2024", "2025"]

    plot_df = df.copy()
    plot_df["year"] = plot_df["year"].astype(str)
    plot_df["media group"] = pd.Categorical(plot_df["media group"], categories=group_order, ordered=True)
    plot_df["year"] = pd.Categorical(plot_df["year"], categories=year_order, ordered=True)
    plot_df = plot_df.sort_values(["media group", "year"])

    fig = px.bar(
        plot_df,
        x="spend",
        y="year",
        facet_row="media group",
        orientation="h",
        text=plot_df["spend"].map(lambda x: f"${x:.1f}M"),
        category_orders={"media group": group_order, "year": year_order[::-1]},
    )

    fig.update_traces(
        marker_color="#1A0DAB",
        textposition="inside",
        textfont=dict(color="white", size=9)
    )

    fig.update_layout(
        template="plotly_white",
        height=430,
        margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
        title=dict(text="Media Spend", x=0.5, font=dict(size=15)),
        showlegend=False,
    )

    fig.update_yaxes(
        matches=None,
        showgrid=False,
        title_text=None,
        showticklabels=False
)
    fig.update_xaxes(showgrid=False, zeroline=False, title_text=None)

    fig.for_each_annotation(lambda a: a.update(text="") if "media group=" in a.text else None)

    return fig

def create_bubble_chart(df: pd.DataFrame, campaign_name: str):
    import math
    import plotly.express as px
    import plotly.graph_objects as go

    plot_df = df.copy().reset_index(drop=True)

    # -----------------------------
    # Basic ranges for normalization
    # -----------------------------
    x_min, x_max = plot_df["xvalues"].min(), plot_df["xvalues"].max()
    y_min, y_max = plot_df["yvalues"].min(), plot_df["yvalues"].max()

    x_range = max(x_max - x_min, 1e-9)
    y_range = max(y_max - y_min, 1e-9)

    max_size_val = max(plot_df["size"].max(), 1e-9)

    # -----------------------------
    # Deterministic channel colors
    # -----------------------------
    palette = px.colors.qualitative.Safe + px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
    channels = plot_df["channel"].dropna().unique().tolist()
    color_map = {ch: palette[i % len(palette)] for i, ch in enumerate(channels)}

    # -----------------------------
    # Crowding detection
    # -----------------------------
    # Bubble radius proxy in normalized chart space.
    # Tune these two values if needed.
    radius_scale = 0.06
    padding = 0.015

    normalized_radii = []
    for s in plot_df["size"]:
        r = math.sqrt(float(s) / max_size_val) * radius_scale
        normalized_radii.append(r)

    crowded = [False] * len(plot_df)

    for i in range(len(plot_df)):
        xi = plot_df.loc[i, "xvalues"]
        yi = plot_df.loc[i, "yvalues"]
        ri = normalized_radii[i]

        for j in range(len(plot_df)):
            if i == j:
                continue

            xj = plot_df.loc[j, "xvalues"]
            yj = plot_df.loc[j, "yvalues"]
            rj = normalized_radii[j]

            dx = (xi - xj) / x_range
            dy = (yi - yj) / y_range
            dist = math.sqrt(dx * dx + dy * dy)

            # If centers are close relative to bubble radii, mark crowded
            if dist < (ri + rj + padding):
                crowded[i] = True
                break

    plot_df["crowded"] = crowded

    # -----------------------------
    # Base bubble chart (no text yet)
    # -----------------------------
    fig = px.scatter(
        plot_df,
        x="xvalues",
        y="yvalues",
        size="size",
        color="channel",
        hover_name="channel",
        color_discrete_map=color_map,
        size_max=52,
        title=CAMPAIGN_INSIGHT,
    )

    fig.update_traces(
        mode="markers",
        marker=dict(opacity=0.72, line=dict(width=1, color="white")),
        showlegend=False
    )

    # -----------------------------
    # Add inside labels for uncrowded points
    # -----------------------------
    inside_df = plot_df[~plot_df["crowded"]].copy()

    if not inside_df.empty:
        fig.add_trace(
            go.Scatter(
                x=inside_df["xvalues"],
                y=inside_df["yvalues"],
                mode="text",
                text=inside_df["channel"],
                textposition="middle center",
                textfont=dict(size=11, color="#222222"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # -----------------------------
    # Add leader-line labels for crowded points
    # -----------------------------
    crowded_df = plot_df[plot_df["crowded"]].copy()

    # Stagger directions automatically
    offset_cycle = [
        (35, -18),
        (42, 0),
        (35, 18),
        (-35, -18),
        (-42, 0),
        (-35, 18),
        (24, -30),
        (-24, 30),
    ]

    for idx, row in crowded_df.reset_index(drop=True).iterrows():
        ax, ay = offset_cycle[idx % len(offset_cycle)]

        fig.add_annotation(
            x=row["xvalues"],
            y=row["yvalues"],
            text=row["channel"],
            showarrow=True,
            arrowhead=0,
            arrowwidth=1,
            arrowcolor="#666666",
            ax=ax,
            ay=ay,
            font=dict(size=11, color="#222222"),
            bgcolor="rgba(255,255,255,0.0)",
            borderpad=1,
        )

    # -----------------------------
    # Layout
    # -----------------------------
    fig.update_layout(
        template="plotly_white",
        height=370,
        margin=dict(l=10, r=10, t=50, b=10),
        title=dict(
            font=dict(size=16),
            x=0.0,
            xanchor="left"
        ),
        xaxis_title="Total ROI",
        yaxis_title="RSV Contribution",
        showlegend=False,
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )

    return fig


def create_weekly_sales_area_chart(df: pd.DataFrame, sheet_name: str):
    component_order = ["base", "promotions", "national media", "retail media", "national recruitment"]
    available_components = [col for col in component_order if col in df.columns]

    if not available_components:
        raise ValueError("No valid decomposition columns found.")

    plot_df = df[["week"] + available_components].melt(
        id_vars="week",
        value_vars=available_components,
        var_name="component",
        value_name="rsv"
    )

    # Force visual order to match PPT
    plot_df["component"] = pd.Categorical(
        plot_df["component"],
        categories=component_order,
        ordered=True
    )

    color_map = {
    "base": "#B3B3B3",
    "promotions": "#6F6AE6",
    "national media": "#0B1FD1",
    "retail media": "#F26C6C",
    "national recruitment": "#1FD3C3",
    }

    fig = px.area(
        plot_df.sort_values(["week", "component"]),
        x="week",
        y="rsv",
        color="component",
        category_orders={"component": component_order},
        color_discrete_map=color_map,
    )

    # -----------------------------------
    # Axis formatting
    # -----------------------------------
    fig.update_yaxes(
        title="RSV"
    )

    fig.update_xaxes(
        title="",
        tickangle=-45
    )

    # -----------------------------------
    # Half-year markers
    # Adjust these dates if needed
    # -----------------------------------
    marker_dates = [
        pd.Timestamp("2024-07-01"),  # H2 24 start
        pd.Timestamp("2025-01-01"),  # H1 25 start
        pd.Timestamp("2025-07-01"),  # H2 25 start
        pd.Timestamp("2025-12-31"),  # end marker
    ]
    marker_labels = [
        ("H2 24", pd.Timestamp("2024-10-01")),
        ("H1 25", pd.Timestamp("2025-04-01")),
        ("H2 25", pd.Timestamp("2025-10-01")),
    ]

    y_max = plot_df["rsv"].groupby(plot_df["week"]).sum().max()
    top_y = y_max * 1.08

    # vertical marker lines
    for dt in marker_dates:
        fig.add_shape(
            type="line",
            x0=dt,
            x1=dt,
            y0=y_max * 0.93,
            y1=top_y,
            line=dict(color="#3A3A3A", width=1, dash="dot")
        )

    # top horizontal dotted guide
    fig.add_shape(
        type="line",
        x0=marker_dates[0],
        x1=marker_dates[-1],
        y0=top_y,
        y1=top_y,
        line=dict(color="#3A3A3A", width=1, dash="dot")
    )

    # labels
    for label, xpos in marker_labels:
        fig.add_annotation(
            x=xpos,
            y=top_y * 0.995,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=12, color="#333333"),
            yanchor="top"
        )

    # -----------------------------------
    # Layout
    # -----------------------------------
    fig.update_layout(
        template="plotly_white",
        height=430,
        margin=dict(l=10, r=10, t=55, b=10),
        title=dict(
            text="",
            font=dict(size=16),
            x=0.0,
            xanchor="left"
        ),
        legend=dict(
            title="",
            orientation="h",
            y=1.06,
            x=0.12
        ),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
        hovermode="x unified",
    )

    return fig


def create_rsv_waterfall_chart(df: pd.DataFrame, sheet_name: str):
    if "variables" not in df.columns or "values" not in df.columns:
        raise ValueError("Columns 'variables' and 'values' are required.")

    waterfall_df = df[["variables", "values"]].dropna(subset=["variables", "values"]).copy()
    x_vals = waterfall_df["variables"].tolist()
    y_vals = waterfall_df["values"].tolist()

    if len(x_vals) < 2:
        raise ValueError("Not enough data for waterfall chart.")

    measure = ["total" if i in (0, len(x_vals) - 1) else "relative" for i in range(len(x_vals))]

    fig = go.Figure(go.Waterfall(
        name="RSV Contribution",
        orientation="v",
        measure=measure,
        x=x_vals,
        y=y_vals,
        text=[f"{v:,.1f}" for v in y_vals],
        textposition="outside",
        connector={"line": {"color": "rgba(255,255,255,0.35)"}},
        increasing={"marker": {"color": "#00C853"}},
        decreasing={"marker": {"color": "#FF1744"}},
        totals={"marker": {"color": "#1A0DAB"}},
    ))

    fig.update_layout(
        template="plotly_white",
        height=260,
        margin=dict(l=10, r=10, t=55, b=10),
        title=dict(
            text=RSV_SPLIT_INSIGHT,
            font=dict(size=16),
            x=0.0,
            xanchor="left"
        ),
        xaxis_title="Driver",
        yaxis_title="Values",
        showlegend=False,
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )

    return fig


def create_rsv_stacked_bar_chart(df: pd.DataFrame, sheet_name: str):
    if "year" not in df.columns:
        raise ValueError("Column 'year' is required.")

    # Order matching PPT legend as closely as possible
    component_order = [
        "promotions",
        "national media",
        "retail media",
        "competition",
        "national recruitment",
        "baseline",
    ]

    available_components = [col for col in component_order if col in df.columns]
    if not available_components:
        raise ValueError("No valid driver-share columns found.")

    stacked_df = df[["year"] + available_components].dropna(subset=["year"]).copy()

    plot_df = stacked_df.melt(
        id_vars="year",
        value_vars=available_components,
        var_name="component",
        value_name="share"
    ).dropna(subset=["share"])

    plot_df["year"] = plot_df["year"].astype(int).astype(str)
    plot_df["share"] = pd.to_numeric(plot_df["share"], errors="coerce")

    # If your values are 0-1 fractions, labels should show %
    plot_df["label"] = plot_df["share"].apply(
        lambda x: f"{x*100:.1f}%" if pd.notna(x) and x > 0 else ""
    )

    color_map = {
        "baseline": "#B3B3B3",
        "promotions": "#7A6AF0",
        "national media": "#0B1FD1",
        "retail media": "#F26C6C",
        "competition": "#10B050",
        "national recruitment": "#20CFC3",
    }

    fig = px.bar(
        plot_df,
        x="share",
        y="year",
        color="component",
        orientation="h",
        text="label",
        category_orders={
            "component": component_order,
            "year": ["2025", "2024"]
        },
        color_discrete_map=color_map,
        title="RSV Contribution Share by Drivers",
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle"
    )

    fig.update_layout(
        template="plotly_white",
        height=190,
        margin=dict(l=10, r=10, t=60, b=10),
        title=dict(font=dict(size=16), x=0.5, xanchor="center"),
        xaxis_title="",
        yaxis_title="",
        barmode="stack",
        legend_title="",
        legend=dict(
            orientation="h",
            y=1.35,
            x=0.05,
            font=dict(size=11)
        ),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )

    # IMPORTANT: keep range 0-1 because your data is in fraction format
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[0, 1]
    )

    fig.update_yaxes(showgrid=False)

    return fig


def create_weekly_media_spends_chart(line_df: pd.DataFrame, spend_df: pd.DataFrame, sheet_name: str):
    merged_df = pd.merge(line_df, spend_df, on="date", how="outer").sort_values("date")
    merged_df["value"] = merged_df["value"].ffill()

    spend_cols = [col for col in ["national media", "retail media", "national recruitment"] if col in merged_df.columns]
    for col in spend_cols:
        merged_df[col] = merged_df[col].fillna(0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if "national media" in merged_df.columns:
        fig.add_trace(
            go.Scatter(
                x=merged_df["date"],
                y=merged_df["national media"],
                mode="lines",
                name="NM",
                stackgroup="one",
                line=dict(width=0.5),
            ),
            secondary_y=False,
        )

    if "retail media" in merged_df.columns:
        fig.add_trace(
            go.Scatter(
                x=merged_df["date"],
                y=merged_df["retail media"],
                mode="lines",
                name="RM",
                stackgroup="one",
                line=dict(width=0.5),
            ),
            secondary_y=False,
        )

    if "national recruitment" in merged_df.columns:
        fig.add_trace(
            go.Scatter(
                x=merged_df["date"],
                y=merged_df["national recruitment"],
                mode="lines",
                name="NR",
                stackgroup="one",
                line=dict(width=0.5),
            ),
            secondary_y=False,
        )

    fig.add_trace(
        go.Scatter(
            x=merged_df["date"],
            y=merged_df["value"],
            mode="lines",
            name="Total RSV",
            line=dict(width=3),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_white",
        height=430,
        margin=dict(l=10, r=10, t=50, b=10),
        title=dict(
            text=WEEKLY_MEDIA_INSIGHT,
            font=dict(size=16),
            x=0.0,
            xanchor="left"
        ),
        legend_title="Series",
        hovermode="x unified",
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )

    fig.update_xaxes(title_text="Week")
    fig.update_yaxes(title_text="Spends", secondary_y=False)
    fig.update_yaxes(title_text="Total RSV", secondary_y=True)

    return fig


def create_media_yoy_dashboard(df: pd.DataFrame, sheet_name: str):
    group_order = ["TM", "NM", "RM", "NR"]
    year_order = ["2023", "2024", "2025"]

    blue = "#1A0DAB"
    gray = "#9E9E9E"
    dark_text = "#222222"
    bg = "#F7F8FA"

    fig = make_subplots(
        rows=4,
        cols=3,
        shared_xaxes=False,
        shared_yaxes=False,
        horizontal_spacing=0.12,
        vertical_spacing=0.12,
        subplot_titles=("", "", "", "", "", "", "", "", "", "", "", "")
    )

    roi_max = max(
        (df["roi st"].fillna(0) + df["roi lt"].fillna(0)).max(),
        df["roitotal"].fillna(0).max()
    )
    rsv_max = max(
        (df["rsv st"].fillna(0) + df["rsv lt"].fillna(0)).max(),
        df["rsv total"].fillna(0).max()
    )
    spend_max = df["spend"].fillna(0).max()

    for row_idx, media_group in enumerate(group_order, start=1):
        sub_df = df[df["media group"] == media_group].copy()
        sub_df["year"] = sub_df["year"].astype(str).str.strip()
        sub_df["year"] = pd.Categorical(sub_df["year"], categories=year_order, ordered=True)
        sub_df = sub_df.sort_values("year")

        if sub_df.empty:
            continue

        y_vals = sub_df["year"].astype(str).tolist()

        # -------------------
        # ROI column
        # -------------------
        fig.add_trace(
            go.Bar(
                x=sub_df["roi st"].fillna(0),
                y=y_vals,
                orientation="h",
                marker=dict(color=blue),
                width=0.5,
                name="ST" if row_idx == 1 else None,
                showlegend=(row_idx == 1),
                hovertemplate="<b>%{y}</b><br>ROI ST: %{x:.2f}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                x=sub_df["roi lt"].fillna(0),
                y=y_vals,
                orientation="h",
                marker=dict(color=gray),
                width=0.5,
                name="LT" if row_idx == 1 else None,
                showlegend=(row_idx == 1),
                hovertemplate="<b>%{y}</b><br>ROI LT: %{x:.2f}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )

        for _, r in sub_df.iterrows():
            fig.add_annotation(
                x=float(r["roitotal"]) + 0.05,
                y=str(r["year"]),
                xref=f"x{(row_idx - 1) * 3 + 1}",
                yref=f"y{(row_idx - 1) * 3 + 1}",
                text=f"<b>{r['roitotal']:.1f}</b>",
                showarrow=False,
                font=dict(size=9, color=dark_text),
                xanchor="left",
            )

        # -------------------
        # RSV column
        # -------------------
        fig.add_trace(
            go.Bar(
                x=sub_df["rsv st"].fillna(0),
                y=y_vals,
                orientation="h",
                marker=dict(color=blue),
                width=0.5,
                showlegend=False,
                hovertemplate="<b>%{y}</b><br>RSV ST: $%{x:.1f}M<extra></extra>",
            ),
            row=row_idx,
            col=2,
        )

        fig.add_trace(
            go.Bar(
                x=sub_df["rsv lt"].fillna(0),
                y=y_vals,
                orientation="h",
                marker=dict(color=gray),
                width=0.5,
                showlegend=False,
                hovertemplate="<b>%{y}</b><br>RSV LT: $%{x:.1f}M<extra></extra>",
            ),
            row=row_idx,
            col=2,
        )

        for _, r in sub_df.iterrows():
            fig.add_annotation(
                x=float(r["rsv total"]) + 0.35,
                y=str(r["year"]),
                xref=f"x{(row_idx - 1) * 3 + 2}",
                yref=f"y{(row_idx - 1) * 3 + 2}",
                text=f"${r['rsv total']:.1f}M",
                showarrow=False,
                font=dict(size=9, color=dark_text),
                xanchor="left",
            )

        # -------------------
        # Spend column
        # -------------------
        fig.add_trace(
            go.Bar(
                x=sub_df["spend"].fillna(0),
                y=y_vals,
                orientation="h",
                marker=dict(color=blue),
                width=0.5,
                text=[f"${v:.1f}M" for v in sub_df["spend"].fillna(0)],
                textposition="inside",
                textfont=dict(color="white", size=9),
                showlegend=False,
                hovertemplate="<b>%{y}</b><br>Spend: $%{x:.1f}M<extra></extra>",
            ),
            row=row_idx,
            col=3,
        )

        # Row label
        fig.add_annotation(
            x=-0.18,
            y=0.90 - (row_idx - 1) * 0.245,
            xref="paper",
            yref="paper",
            text=f"<b>{media_group}</b>",
            showarrow=False,
            font=dict(size=11, color=dark_text),
            align="left",
        )

    # Column headers
    fig.add_annotation(
        x=0.16, y=1.05, xref="paper", yref="paper",
        text="<b>Total RSV ROIs</b>",
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="black",
        borderpad=8
    )
    fig.add_annotation(
        x=0.50, y=1.05, xref="paper", yref="paper",
        text="<b>RSV Contribution</b>",
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="black",
        borderpad=8
    )
    fig.add_annotation(
        x=0.84, y=1.05, xref="paper", yref="paper",
        text="<b>Media Spend</b>",
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="black",
        borderpad=8
    )

    fig.update_layout(
        template="plotly_white",
        barmode="stack",
        height=560,
        margin=dict(l=90, r=25, t=65, b=20),
        title=dict(
            text=f"Changes in Media Investments, RSV and ROI YoY — {sheet_name}",
            font=dict(size=19),
        ),
        legend=dict(
            orientation="h",
            y=1.08,
            x=0.0
        ),
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font=dict(color=dark_text),
    )

    for row_idx in range(1, 5):
        fig.update_xaxes(
            range=[0, max(1.8, roi_max * 1.35)],
            showgrid=False,
            zeroline=False,
            row=row_idx,
            col=1,
        )
        fig.update_xaxes(
            range=[0, max(5, rsv_max * 1.35)],
            showgrid=False,
            zeroline=False,
            row=row_idx,
            col=2,
        )
        fig.update_xaxes(
            range=[0, max(5, spend_max * 1.35)],
            showgrid=False,
            zeroline=False,
            row=row_idx,
            col=3,
        )

        fig.update_yaxes(
            type="category",
            categoryorder="array",
            categoryarray=year_order[::-1],
            row=row_idx,
            col=1,
        )
        fig.update_yaxes(
            type="category",
            categoryorder="array",
            categoryarray=year_order[::-1],
            row=row_idx,
            col=2,
        )
        fig.update_yaxes(
            type="category",
            categoryorder="array",
            categoryarray=year_order[::-1],
            row=row_idx,
            col=3,
        )

    return fig


def create_media_spend_mix_chart(main_df: pd.DataFrame, roi_df: pd.DataFrame, title_suffix: str = ""):
    half_year_order = [str(v) for v in main_df["half_year"].cat.categories if pd.notna(v)]

    campaign_order = [
        "Cuc/Savd",
        "Ecosystem",
        "Healthy Weight",
        "Iams For Life",
        "Kitten",
        "Others",
        "Total",
    ]
    available_campaigns = [c for c in campaign_order if c in main_df["campaign"].unique().tolist()]
    if not available_campaigns:
        available_campaigns = sorted(main_df["campaign"].dropna().unique().tolist())

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.72, 0.28],
    )

    for campaign in available_campaigns:
        campaign_df = main_df[main_df["campaign"] == campaign].copy()
        campaign_df = campaign_df.sort_values("half_year")

        fig.add_trace(
            go.Bar(
                x=campaign_df["half_year"].astype(str),
                y=campaign_df["spend_value_m"],
                name=campaign,
                customdata=campaign_df[["spend_pct", "spend_value_m"]],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Campaign: " + campaign + "<br>"
                    "Spend: $%{customdata[1]:.1f}M<br>"
                    "Mix: %{customdata[0]:.0f}%<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

    for _, r in main_df.iterrows():
        if pd.isna(r["spend_value_m"]) or r["spend_value_m"] <= 0:
            continue

        if pd.notna(r["spend_pct"]) and r["spend_pct"] >= 5:
            fig.add_annotation(
                x=str(r["half_year"]),
                y=float(r["spend_value_m"]),
                text=f"{r['spend_pct']:.0f}%, ${r['spend_value_m']:.1f}M",
                showarrow=False,
                font=dict(size=10, color="white"),
                row=1,
                col=1,
            )

    roi_df_plot = roi_df.copy().sort_values("half_year")

    fig.add_trace(
        go.Scatter(
            x=roi_df_plot["half_year"].astype(str),
            y=roi_df_plot["roi"],
            mode="lines+markers+text",
            name="RSV ROI",
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in roi_df_plot["roi"]],
            textposition="top center",
            line=dict(width=3, color="red"),
            marker=dict(size=8, color="red"),
            hovertemplate="<b>%{x}</b><br>ROI: %{y:.2f}<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        template="plotly_white",
        height=520,
        barmode="stack",
        margin=dict(l=20, r=20, t=45, b=10),
        title=dict(
            text=MEDIA_SPEND_MIX_INSIGHT,
            font=dict(size=16),
            x=0.0,
            xanchor="left",
        ),
        legend=dict(
            orientation="h",
            y=0.93,
            x=0.0,
            title="Campaign"
        ),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )

    fig.update_yaxes(title_text="Media Spends ($M)", row=1, col=1)
    fig.update_yaxes(title_text="RSV ROI", row=2, col=1)

    fig.update_xaxes(categoryorder="array", categoryarray=half_year_order, row=1, col=1)
    fig.update_xaxes(categoryorder="array", categoryarray=half_year_order, row=2, col=1)

    return fig


def safe_metric(series, mode="mean"):
    if series is None or len(series) == 0:
        return "0"
    if mode == "mean":
        return f"{series.mean():,.2f}"
    if mode == "sum":
        return f"{series.sum():,.2f}"
    if mode == "count":
        return f"{series.nunique():,}"
    return "0"

def render_channel_roi_table(df: pd.DataFrame, period_label: str, header_color: str, body_color: str, group_color: str):
    display_df = prepare_channel_roi_display_table(df)

    channel_col = display_df["channel_display"].tolist()
    platform_col = display_df["platform"].tolist()
    invest_col = display_df["Investment ($ Thousand)"].tolist()
    rsv_col = display_df["RSV ($ Thousand)"].tolist()
    roi_col = display_df["RSV ROI"].tolist()

    font_colors_channel = [group_color if str(v).strip() != "" else "rgba(0,0,0,0)" for v in channel_col]
    font_colors_other = ["#111111"] * len(display_df)

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[120, 110, 170, 140, 90],
                header=dict(
                    values=[
                        "<b>Channel</b>",
                        "<b>Platform</b>",
                        "<b>Investment<br>($ Thousand)</b>",
                        "<b>RSV<br>($ Thousand)</b>",
                        "<b>RSV ROI</b>",
                    ],
                    fill_color=header_color,
                    font=dict(color="white", size=11),
                    align="center",
                    height=42,
                ),
                cells=dict(
                    values=[channel_col, platform_col, invest_col, rsv_col, roi_col],
                    fill_color=body_color,
                    font=dict(
                        color=[font_colors_channel, font_colors_other, font_colors_other, font_colors_other, font_colors_other],
                        size=10
                    ),
                    align="center",
                    height=26,
                ),
            )
        ]
    )

    fig.update_layout(
        template=None,
        height=490,
        margin=dict(l=0, r=0, t=36, b=0),
        title=dict(
            text=f"<b>{period_label}</b>",
            x=0.5,
            xanchor="center",
            font=dict(color="white", size=15),
        ),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )
    return fig

def render_campaign_roi_table(df: pd.DataFrame, header_color: str, body_color: str):
    display_df = prepare_campaign_roi_display_table(df)

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[140, 165, 115, 125],
                header=dict(
                    values=[f"<b>{c}</b>" for c in display_df.columns],
                    fill_color=header_color,
                    font=dict(color="white", size=13),
                    align="center",
                    height=42,
                ),
                cells=dict(
                    values=[display_df[col] for col in display_df.columns],
                    fill_color=body_color,
                    font=dict(color="black", size=12),
                    align="center",
                    height=38,
                ),
            )
        ]
    )

    fig.update_layout(
        template=None,
        height=320,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )
    return fig


def create_cross_synergy_heatmap(df: pd.DataFrame, sheet_name: str):
    """
    Build color-only heatmap for cross synergies.
    No numbers are displayed inside cells.
    """
    plot_df = df.copy()
    plot_df = plot_df.set_index("from_channel")

    fig = go.Figure(
        data=go.Heatmap(
            z=plot_df.values,
            x=plot_df.columns.tolist(),
            y=plot_df.index.tolist(),
            colorscale=[
                [0.0, "#F4F6F8"],
                [0.2, "#D8E4F2"],
                [0.4, "#B8CCE4"],
                [0.6, "#8FA9C4"],
                [0.8, "#4F7192"],
                [1.0, "#1F4E79"],
            ],
            showscale=False,
            hovertemplate="FROM: %{y}<br>TO: %{x}<br>Synergy: %{z:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        margin=dict(l=20, r=20, t=55, b=10),
        title=dict(
            text=CROSS_SYNERGY_INSIGHT,
            font=dict(size=16),
            x=0.0,
            xanchor="left",
        ),
        xaxis=dict(
            title="TO",
            side="top",
            tickangle=0,
        ),
        yaxis=dict(
            title="FROM",
            autorange="reversed",
        ),
        paper_bgcolor="#F7F8FA",
        plot_bgcolor="#F7F8FA",
        font=dict(color="#222222"),
    )

    return fig

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
try:
    campaign_data = load_campaign_data()
    combined_campaign_df = build_combined_campaign_df(campaign_data)
    weekly_sales_data = load_weekly_sales_data()
    rsv_split_data = load_rsv_split_data()
    weekly_media_data = load_weekly_media_spends_data()
    media_yoy_data = load_media_yoy_data()
    media_spend_mix_data = load_media_spend_mix_data()
    campaign_roi_data = load_campaign_roi_data()
    channel_roi_data = load_channel_roi_data()
    cross_synergy_data = load_cross_synergy_data()
    
except Exception as e:
    st.error(f"Data could not be loaded: {e}")
    st.stop()

hero_img_base64 = get_base64_image("Blue Page.jpg")
logos_img_base64 = get_base64_image("Blue Page.jpg")
# --------------------------------------------------
# TOP NAVIGATION
# --------------------------------------------------
tabs = st.tabs([
    "Home",
    "Executive Summary",
    "Weekly Sales Decomposition",
    "RSV Contribution Split",
    "Weekly Media Spends",
    "Media RSV & ROI",
    "NM Channel Mix",
    "Campaign/Channel Level RSV ROI",
    "Cross Synergies",
    "Campaign"
])

(
    home_tab,
    executive_summary_tab,
    weekly_sales_tab,
    rsv_split_tab,
    weekly_media_tab,
    media_yoy_tab,
    mix_yoy_tab,
    campaign_roi_tab,
    cross_synergies_tab,
    campaign_tab
) = tabs


# --------------------------------------------------
# HOME TAB
# --------------------------------------------------
with home_tab:
    components.html(
        f"""
        <div style="
            position: relative;
            width: 100%;
            height: 80vh;
            overflow: hidden;
            border-radius: 8px;
            font-family: Arial, sans-serif;
        ">
            <img
                src="data:image/png;base64,{hero_img_base64}"
                style="
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    object-position: center top;
                    display: block;
                "
            />

            <div style="
                position: absolute;
                inset: 0;
                background: linear-gradient(
                    to right,
                    rgba(0, 0, 0, 0.78) 0%,
                    rgba(0, 0, 0, 0.42) 38%,
                    rgba(0, 0, 0, 0.05) 75%
                );
            "></div>

            <div style="
                position: absolute;
                top: 10%;
                left: 4.5%;
                color: white;
                max-width: 620px;
                z-index: 5;
            ">
                <div style="
                    font-size: 52px;
                    font-weight: 800;
                    line-height: 1;
                    margin-bottom: 4px;
                    color: white;
                ">
                    Client
                </div>

                <div style="
                    font-size: 28px;
                    font-weight: 400;
                    margin-bottom: 64px;
                    color: white;
                ">
                    Brand
                </div>

                <div style="
                    font-size: 64px;
                    font-weight: 800;
                    line-height: 1.05;
                    margin-bottom: 20px;
                    color: white;
                ">
                    Product Name
                </div>

                <div style="
                    font-size: 28px;
                    font-weight: 400;
                    color: white;
                ">
                    Marketing Mix Modeling
                </div>
            </div>


        </div>
        """,
        height=760,
        scrolling=False,
    )

# --------------------------------------------------
# EXECUTIVE SUMMARY TAB
# --------------------------------------------------
with executive_summary_tab:
    st.markdown('<div class="hero-title">Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">High-level performance overview for leadership review</div>',
        unsafe_allow_html=True,
    )

    # For now these are static values to match the design.
    # Later we can connect them to your Excel data dynamically.
    st.markdown(
        """
        <div class="exec-summary-meta">
            Brand: <b>Client Brand</b> · Market: <b>US</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_cols = st.columns(6, gap="large")

    kpi_data = [
        ("Total Spend", "$321.98M"),
        ("Volume<br>Contribution", "97.87M"),
        ("NSV<br>Contribution", "$1.22B"),
        ("Media<br>Spending", "$742.52M"),
        # ("GSV<br>Contribution", "$1.51B"),
        # ("RSV<br>Contribution", "$2.03B"),
    ]

    for col, (title, value) in zip(kpi_cols, kpi_data):
        with col:
            render_kpi_card(title, value)
# --------------------------------------------------
# CAMPAIGN TAB
# --------------------------------------------------
with campaign_tab:
    campaign_options = list(campaign_data.keys())

    campaign_label_map = {
        name: name.replace("_Bubble chart", "").replace("_", " ").title()
        for name in campaign_options
    }
    reverse_campaign_map = {v: k for k, v in campaign_label_map.items()}
    display_options = list(campaign_label_map.values())

    # default selected campaign
    
    selected_campaign_label = st.session_state.get(
        "campaign_selector_tabs",
        display_options[0] if display_options else None
    )

    # top row only
    title_col, campaign_switch_col, filter_col = st.columns([1.2, 1.2, 1.0])

    with title_col:
        st.markdown('<div class="hero-title">Campaign</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-subtitle">Interactive bubble-chart view of channel performance</div>',
            unsafe_allow_html=True,
        )

    with campaign_switch_col:
        selected_campaign_label = st.segmented_control(
            "Campaign selector",
            options=display_options,
            default=selected_campaign_label,
            key="campaign_selector_tabs",
            label_visibility="collapsed"
        )

    selected_campaign = reverse_campaign_map[selected_campaign_label]
    filtered_df = campaign_data[selected_campaign].copy()
    channel_options = sorted(filtered_df["channel"].dropna().unique())

    with filter_col:
        current_selected = st.session_state.get("campaign_channel_filter", channel_options)
        if not set(current_selected).issubset(set(channel_options)):
            current_selected = channel_options

        button_label = f"Choose channels ({len(current_selected)}/{len(channel_options)})"
        st.markdown(
            '<div style="height: 0.15rem;"></div>',
            unsafe_allow_html=True,
        )
        with st.popover(button_label):
            selected_channels = st.multiselect(
                "Channel selector",
                options=channel_options,
                default=current_selected,
                key="campaign_channel_filter",
                label_visibility="collapsed"
            )

    if selected_channels:
        filtered_df = filtered_df[filtered_df["channel"].isin(selected_channels)]

    # chart
    if filtered_df.empty:
        st.warning("No data available for the selected campaign/channel filter.")
    else:
        st.plotly_chart(
            create_bubble_chart(filtered_df, selected_campaign),
            use_container_width=True
        )



# --------------------------------------------------
# WEEKLY SALES DECOMPOSITION TAB
# --------------------------------------------------
with weekly_sales_tab:
    if not weekly_sales_data:
        st.warning("No Weekly Sales sheets found. Use sheet names starting with 'WeeklySales'.")
    else:
        weekly_sheet_options = list(weekly_sales_data.keys())

        weekly_label_map = {
            name: name.replace("WeeklySales_", "Weekly Sales ").replace("_", " ").title()
            for name in weekly_sheet_options
        }
        reverse_weekly_map = {v: k for k, v in weekly_label_map.items()}
        display_weekly_options = list(weekly_label_map.values())

        top_title_col, top_switch_col, top_filter_col = st.columns([1.2, 1.3, 1.1])

        with top_title_col:
            st.markdown('<div class="hero-title">Weekly Sales Decomposition</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-subtitle">Weekly decomposition of RSV across key business drivers</div>',
                unsafe_allow_html=True,
            )

        with top_switch_col:
            selected_weekly_label = st.segmented_control(
                "Weekly sales selector",
                options=display_weekly_options,
                default=display_weekly_options[0] if display_weekly_options else None,
                key="weekly_sales_selector_tabs",
                label_visibility="collapsed"
            )

        selected_weekly_sheet = reverse_weekly_map[selected_weekly_label]
        weekly_df = weekly_sales_data[selected_weekly_sheet].copy()

        available_components = [
            col for col in ["base", "promotions", "national media", "national recruitment", "retail media"]
            if col in weekly_df.columns
        ]

        with top_filter_col:
            current_components = st.session_state.get("weekly_sales_components", available_components)
            if not set(current_components).issubset(set(available_components)):
                current_components = available_components

            button_label = f"Choose components ({len(current_components)}/{len(available_components)})"

            st.markdown('<div style="height: 0.1rem;"></div>', unsafe_allow_html=True)
            with st.popover(button_label):
                selected_components = st.multiselect(
                    "Components selector",
                    options=available_components,
                    default=current_components,
                    key="weekly_sales_components",
                    label_visibility="collapsed"
                )

        weekly_filtered_df = (
            weekly_df[["week"] + selected_components].copy()
            if selected_components else weekly_df[["week"]].copy()
        )

        if len(selected_components) == 0:
            st.warning("Please select at least one component to display the chart.")
        else:
            st.markdown(
                f"""
                <div style="
                    font-size: 1.0rem;
                    font-weight: 700;
                    color: #333333;
                    margin-bottom: 0.3rem;
                ">
                    {WEEKLY_SALES_INSIGHT}

                """,
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                create_weekly_sales_area_chart(weekly_filtered_df, selected_weekly_sheet),
                use_container_width=True
            )



# --------------------------------------------------
# RSV CONTRIBUTION SPLIT TAB
# --------------------------------------------------
# --------------------------------------------------
# RSV CONTRIBUTION SPLIT TAB
# --------------------------------------------------
with rsv_split_tab:
    if not rsv_split_data:
        st.warning("No RSV Contribution sheets found. Use sheet names starting with 'RSVContribution'.")
    else:
        rsv_sheet_options = list(rsv_split_data.keys())

        rsv_label_map = {
            name: name.replace("RSVContribution", "RSV Contribution ").replace("_", " ").strip().title()
            for name in rsv_sheet_options
        }
        reverse_rsv_map = {v: k for k, v in rsv_label_map.items()}
        display_rsv_options = list(rsv_label_map.values())

        top_title_col, top_switch_col = st.columns([1.25, 1.75])

        with top_title_col:
            st.markdown('<div class="hero-title">RSV Contribution Split</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-subtitle">Waterfall and contribution-share view of RSV drivers</div>',
                unsafe_allow_html=True,
            )

        with top_switch_col:
            selected_rsv_label = st.segmented_control(
                "RSV contribution selector",
                options=display_rsv_options,
                default=display_rsv_options[0] if display_rsv_options else None,
                key="rsv_split_selector_tabs",
                label_visibility="collapsed"
            )

        selected_rsv_sheet = reverse_rsv_map[selected_rsv_label]
        rsv_df = rsv_split_data[selected_rsv_sheet].copy()

        # Build AI context for the currently selected RSV sheet
        st.session_state["rsv_ai_context"] = build_rsv_split_context(
            rsv_df,
            selected_sheet=selected_rsv_sheet
        )

        # Reset AI chat when user changes RSV sheet
        reset_rsv_ai_chat_if_sheet_changed(selected_rsv_sheet)

        try:
            st.plotly_chart(
                create_rsv_waterfall_chart(rsv_df, selected_rsv_sheet),
                use_container_width=True,
                key=f"rsv_waterfall_{selected_rsv_sheet}"
            )
            st.plotly_chart(
                create_rsv_stacked_bar_chart(rsv_df, selected_rsv_sheet),
                use_container_width=True,
                key=f"rsv_stacked_{selected_rsv_sheet}"
            )

            render_rsv_ai_chat_compact()

        except Exception as chart_error:
            st.error(f"Could not render RSV Contribution charts: {chart_error}")
# --------------------------------------------------
# WEEKLY MEDIA SPENDS TAB
# --------------------------------------------------
with weekly_media_tab:
    if not weekly_media_data:
        st.warning("No valid Weekly Media Spends sheet could be parsed. Check headers: 'date', 'value', 'national media', 'retail media'.")
    else:
        media_sheet_options = list(weekly_media_data.keys())

        media_label_map = {
            name: name.replace("WeeklyMediaSpends", "Weekly Media Spends ").replace("_", " ").strip().title()
            for name in media_sheet_options
        }
        reverse_media_map = {v: k for k, v in media_label_map.items()}
        display_media_options = list(media_label_map.values())

        top_title_col, top_switch_col = st.columns([1.25, 1.75])

        with top_title_col:
            st.markdown('<div class="hero-title">Weekly Media Spends</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-subtitle">Weekly media spend landscape with total RSV overlay</div>',
                unsafe_allow_html=True,
            )

        with top_switch_col:
            selected_media_label = st.segmented_control(
                "Weekly media selector",
                options=display_media_options,
                default=display_media_options[0] if display_media_options else None,
                key="weekly_media_selector_tabs",
                label_visibility="collapsed"
            )

        selected_media_sheet = reverse_media_map[selected_media_label]
        selected_media_data = weekly_media_data[selected_media_sheet]
        line_df = selected_media_data["line_df"].copy()
        spend_df = selected_media_data["spend_df"].copy()

        try:
            st.plotly_chart(
                create_weekly_media_spends_chart(line_df, spend_df, selected_media_sheet),
                use_container_width=True
            )
        except Exception as chart_error:
            st.error(f"Could not render Weekly Media Spends chart: {chart_error}")


# --------------------------------------------------
# MEDIA INV, RSV, ROI YOY TAB
# --------------------------------------------------
with media_yoy_tab:
    if not media_yoy_data:
        st.warning("No Media YoY sheets found. Use sheet names starting with 'MediaInvRSVROIYoY'.")
    else:
        media_yoy_sheet_options = list(media_yoy_data.keys())

        media_yoy_label_map = {
            name: name.replace("MediaInvRSVROIYoY", "Media YoY ").replace("_", " ").strip().title()
            for name in media_yoy_sheet_options
        }
        reverse_media_yoy_map = {v: k for k, v in media_yoy_label_map.items()}
        display_media_yoy_options = list(media_yoy_label_map.values())

        top_title_col, top_switch_col = st.columns([1.25, 1.75])

        with top_title_col:
            st.markdown('<div class="hero-title">Media RSV & ROI</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-subtitle">Changes in media investments, RSV, and ROI across years</div>',
                unsafe_allow_html=True,
            )

        with top_switch_col:
            selected_media_yoy_label = st.segmented_control(
                "Media YoY selector",
                options=display_media_yoy_options,
                default=display_media_yoy_options[0] if display_media_yoy_options else None,
                key="media_yoy_selector_tabs",
                label_visibility="collapsed"
            )

        selected_media_yoy_sheet = reverse_media_yoy_map[selected_media_yoy_label]
        media_yoy_df = media_yoy_data[selected_media_yoy_sheet].copy()
        st.markdown(
            f"""
            <div style="
                font-size: 0.95rem;
                font-weight: 600;
                color: #333333;
                line-height: 1.35;
                margin-top: 0.2rem;
                margin-bottom: 0.55rem;
            ">
                {MEDIA_YOY_INSIGHT}
            """,
                unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="display:flex; gap:22px; align-items:center; margin-bottom:8px; padding-left:10px; color:#222222; font-size:14px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:14px; height:14px; background:#1A0DAB;"></div>
                    <span>ST</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="width:14px; height:14px; background:#9E9E9E;"></div>
                    <span>LT</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([1, 1, 1])

        try:
            with c1:
                st.plotly_chart(
                    create_media_yoy_roi_chart(media_yoy_df),
                    use_container_width=True
                )

            with c2:
                st.plotly_chart(
                    create_media_yoy_rsv_chart(media_yoy_df),
                    use_container_width=True
                )

            with c3:
                st.plotly_chart(
                    create_media_yoy_spend_chart(media_yoy_df),
                    use_container_width=True
                )

        except Exception as chart_error:
            st.error(f"Could not render Media YoY chart: {chart_error}")




# --------------------------------------------------
# MEDIA SPEND MIX TAB
# --------------------------------------------------
with mix_yoy_tab:
    if not media_spend_mix_data:
        st.warning(
            "Media Spend Mix data not found. "
            "Expected sheets: 'MediaSpendMix_Main' and 'MediaSpendMix_ROI'."
        )
    else:
        top_title_col, top_switch_col = st.columns([1.25, 1.75])

        with top_title_col:
            st.markdown(
                '<div class="hero-title">NM Channel Mix</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="hero-subtitle">Campaign-level spend mix with ROI trend across half-years</div>',
                unsafe_allow_html=True,
            )

        with top_switch_col:
            mix_view_options = ["Main View"]
            selected_mix_view = st.segmented_control(
                "Media Spend Mix selector",
                options=mix_view_options,
                default=mix_view_options[0],
                key="mix_yoy_selector_tabs",
                label_visibility="collapsed"
            )

        try:
            fig = create_media_spend_mix_chart(
                media_spend_mix_data["main"],
                media_spend_mix_data["roi"],
                title_suffix=""
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as chart_error:
            st.error(f"Could not render Media Spend Mix chart: {chart_error}")



# --------------------------------------------------
# CAMPAIGN ROI TAB
# --------------------------------------------------
with campaign_roi_tab:
    combined_roi_views = {}
    combined_roi_views.update(campaign_roi_data if campaign_roi_data else {})
    combined_roi_views.update(channel_roi_data if channel_roi_data else {})

    if not combined_roi_views:
        st.warning("No Campaign ROI or Channel ROI sheets found. Use sheet names starting with 'CampaignROI' or 'ChannelROI'.")
    else:
        roi_view_options = list(combined_roi_views.keys())

        roi_view_label_map = {
            name: name.replace("CampaignROI_", "Campaign ROI ").replace("ChannelROI_", "Channel ROI ").replace("_", " ").title()
            for name in roi_view_options
        }
        reverse_roi_view_map = {v: k for k, v in roi_view_label_map.items()}
        display_roi_view_options = list(roi_view_label_map.values())

        # page title
        st.markdown('<div class="hero-title">Campaign/Channel Level RSV ROI</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-subtitle">Campaign-level RSV ROI comparison across periods</div>',
            unsafe_allow_html=True,
        )

        # default selected view
        selected_roi_view_label = st.session_state.get(
            "campaign_roi_selector_tabs",
            display_roi_view_options[0] if display_roi_view_options else None
        )
        selected_roi_sheet = reverse_roi_view_map[selected_roi_view_label]

        insight_text = (
            CAMPAIGN_ROI_INSIGHT
            if selected_roi_sheet.lower().startswith("campaignroi")
            else "Channel-level view compares platform contribution within each brand/channel grouping across the selected periods."
        )

        # insight moved above selector
        st.markdown(
            f"""
            <div style="
                font-size: 1.0rem;
                font-weight: 700;
                color: #333333;
                line-height: 1.35;
                margin-top: 0.1rem;
                margin-bottom: 0.45rem;
            ">
                {insight_text}
            """,
            unsafe_allow_html=True,
        )

        # selector row
        selected_roi_view_label = st.segmented_control(
            "Campaign ROI selector",
            options=display_roi_view_options,
            default=selected_roi_view_label,
            key="campaign_roi_selector_tabs",
            label_visibility="collapsed"
        )

        selected_roi_sheet = reverse_roi_view_map[selected_roi_view_label]
        selected_df = combined_roi_views[selected_roi_sheet].copy()

        period_options = selected_df["period"].dropna().astype(str).unique().tolist()

        left_controls_col, right_controls_col = st.columns(2)

        with left_controls_col:
            selected_left_period = st.selectbox(
                "",
                options=period_options,
                index=0 if period_options else None,
                key="campaign_roi_left_period",
                label_visibility="collapsed"
            )

        with right_controls_col:
            selected_right_period = st.selectbox(
                "",
                options=period_options,
                index=1 if len(period_options) > 1 else 0,
                key="campaign_roi_right_period",
                label_visibility="collapsed"
            )

        left_df = selected_df[selected_df["period"].astype(str) == selected_left_period].copy()
        right_df = selected_df[selected_df["period"].astype(str) == selected_right_period].copy()

        left_table_col, right_table_col = st.columns(2)

        if selected_roi_sheet.lower().startswith("campaignroi"):
            with left_table_col:
                left_fig = render_campaign_roi_table(
                    left_df,
                    header_color="#C0268C",
                    body_color="#E9D6E0"
                )
                st.plotly_chart(left_fig, use_container_width=True)

            with right_table_col:
                right_fig = render_campaign_roi_table(
                    right_df,
                    header_color="#7E3AAF",
                    body_color="#DCCAE8"
                )
                st.plotly_chart(right_fig, use_container_width=True)

        else:
            with left_table_col:
                left_fig = render_channel_roi_table(
                    left_df,
                    selected_left_period,
                    header_color="#C0268C",
                    body_color="#E9D6E0",
                    group_color="#C0268C",
                )
                st.plotly_chart(left_fig, use_container_width=True)

            with right_table_col:
                right_fig = render_channel_roi_table(
                    right_df,
                    selected_right_period,
                    header_color="#7E3AAF",
                    body_color="#DCCAE8",
                    group_color="#7E3AAF",
                )
                st.plotly_chart(right_fig, use_container_width=True)



# --------------------------------------------------
# CROSS SYNERGIES TAB
# --------------------------------------------------
with cross_synergies_tab:
    if not cross_synergy_data:
        st.warning("No Cross Synergy sheets found. Use sheet names starting with 'CrossSynergy'.")
    else:
        cross_synergy_sheet_options = list(cross_synergy_data.keys())

        cross_label_map = {
            name: name.replace("CrossSynergy", "Cross Synergy ").replace("_", " ").strip().title()
            for name in cross_synergy_sheet_options
        }
        reverse_cross_map = {v: k for k, v in cross_label_map.items()}
        display_cross_options = list(cross_label_map.values())

        # -----------------------------------------
        # Top row: title + selector
        # -----------------------------------------
        top_title_col, top_switch_col = st.columns([1.25, 1.75])

        with top_title_col:
            st.markdown('<div class="hero-title">Cross Synergies</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="hero-subtitle">Channel interaction heatmap showing relative synergy strength</div>',
                unsafe_allow_html=True,
            )

        with top_switch_col:
            selected_cross_label = st.segmented_control(
                "Cross Synergy selector",
                options=display_cross_options,
                default=display_cross_options[0] if display_cross_options else None,
                key="cross_synergy_selector_tabs",
                label_visibility="collapsed"
            )

        selected_cross_sheet = reverse_cross_map[selected_cross_label]
        cross_synergy_df = cross_synergy_data[selected_cross_sheet].copy()

        # -----------------------------------------
        # Main chart (full width)
        # -----------------------------------------
        try:
            fig = create_cross_synergy_heatmap(cross_synergy_df, selected_cross_sheet)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as chart_error:
            st.error(f"Could not render Cross Synergy chart: {chart_error}")


