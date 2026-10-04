import streamlit as st
import pandas as pd
import textwrap

from src.ui.layout import (
    page_header,
    ai_insight,
    page_footer
)

from src.business_copilot.copilot_engine import BusinessCopilot


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Business Copilot | Nex Decision AI",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown(
    textwrap.dedent(
        """
        <style>

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .copilot-hero {
            padding: 30px;
            border-radius: 20px;
            background: linear-gradient(
                135deg,
                rgba(37,99,235,0.18),
                rgba(124,58,237,0.15)
            );
            border: 1px solid rgba(148,163,184,0.18);
            margin-bottom: 24px;
        }

        .copilot-title {
            font-size: 34px;
            font-weight: 850;
            margin-bottom: 8px;
        }

        .copilot-subtitle {
            font-size: 16px;
            color: #94a3b8;
            line-height: 1.6;
        }

        .dataset-badge {
            display: inline-block;
            margin-top: 14px;
            padding: 7px 14px;
            border-radius: 20px;
            background: rgba(59,130,246,0.12);
            border: 1px solid rgba(59,130,246,0.25);
            color: #bfdbfe;
            font-size: 13px;
        }

        .decision-card {
            padding: 22px;
            border-radius: 16px;
            background: rgba(15,23,42,0.45);
            border: 1px solid rgba(148,163,184,0.14);
            min-height: 145px;
        }

        .decision-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }

        .decision-title {
            font-size: 15px;
            font-weight: 750;
            margin-bottom: 7px;
        }

        .decision-text {
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.55;
        }

        .score-card {
            padding: 25px;
            border-radius: 18px;
            background: rgba(15,23,42,0.48);
            border: 1px solid rgba(148,163,184,0.15);
            text-align: center;
        }

        .score-value {
            font-size: 48px;
            font-weight: 850;
        }

        .score-label {
            color: #94a3b8;
            font-size: 13px;
        }

        .recommendation-card {
            padding: 17px 20px;
            border-radius: 13px;
            background: rgba(30,41,59,0.48);
            border-left: 4px solid #6366f1;
            margin-bottom: 10px;
        }

        .risk-card {
            padding: 17px 20px;
            border-radius: 13px;
            background: rgba(127,29,29,0.14);
            border-left: 4px solid #ef4444;
            margin-bottom: 10px;
        }

        .opportunity-card {
            padding: 17px 20px;
            border-radius: 13px;
            background: rgba(20,83,45,0.14);
            border-left: 4px solid #22c55e;
            margin-bottom: 10px;
        }

        .action-card {
            padding: 22px;
            border-radius: 16px;
            background: linear-gradient(
                135deg,
                rgba(37,99,235,0.14),
                rgba(99,102,241,0.10)
            );
            border: 1px solid rgba(99,102,241,0.25);
        }

        .action-title {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 8px;
        }

        .action-text {
            font-size: 19px;
            font-weight: 750;
            line-height: 1.4;
        }

        .question-card {
            padding: 13px 16px;
            border-radius: 11px;
            background: rgba(30,41,59,0.40);
            border: 1px solid rgba(148,163,184,0.12);
            margin-bottom: 8px;
        }

        .section-title {
            font-size: 21px;
            font-weight: 780;
            margin-top: 20px;
            margin-bottom: 14px;
        }

        </style>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

page_header(
    "🤖 AI Business Copilot",
    "Turn your dataset into business questions, insights, risks and actionable decisions."
)


# =========================================================
# CHECK DATASET
# =========================================================

if "dataset" not in st.session_state:

    st.warning(
        "📂 Please upload a dataset first."
    )

    st.info(
        "Go to **Upload Dataset** and upload your business dataset."
    )

    if st.button(
        "📂 Go to Upload Dataset"
    ):
        st.switch_page(
            "pages/1_Upload_Dataset.py"
        )

    st.stop()


# =========================================================
# LOAD DATASET
# =========================================================

df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Uploaded Dataset"
)


if df is None or df.empty:

    st.error(
        "❌ The current dataset is empty or unavailable."
    )

    st.stop()


# =========================================================
# COPILOT HERO
# =========================================================

st.markdown(
    textwrap.dedent(
        f"""
        <div class="copilot-hero">
            <div class="copilot-title">
                🧠 Decision Intelligence Center
            </div>
            <div class="copilot-subtitle">
                Nex Decision AI connects your dataset with
                business reasoning to identify risks,
                opportunities and actionable decisions.
            </div>
            <div class="dataset-badge">
                📄 Active Dataset: {filename}
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# INITIALIZE COPILOT
# =========================================================

try:

    copilot = BusinessCopilot(df)

    summary = copilot.executive_summary()

    raw_score = copilot.business_score()

except Exception as e:

    st.error(
        "⚠️ The AI Business Copilot could not analyze this dataset."
    )

    with st.expander(
        "Technical details"
    ):

        st.write(str(e))

    st.stop()


# =========================================================
# BUSINESS SCORE
# =========================================================

try:

    score = float(raw_score)

except Exception:

    score = 0


score = max(
    0,
    min(
        100,
        score
    )
)


if score >= 90:

    score_status = "Excellent"
    score_message = (
        "The dataset is in strong condition for decision workflows."
    )

elif score >= 75:

    score_status = "Good"
    score_message = (
        "The dataset is generally suitable for business analysis."
    )

elif score >= 60:

    score_status = "Moderate"
    score_message = (
        "Some improvements may be required before advanced modeling."
    )

else:

    score_status = "Needs Attention"
    score_message = (
        "Important data issues should be addressed before major decisions."
    )


# =========================================================
# DECISION SNAPSHOT
# =========================================================

st.markdown(
    '<div class="section-title">🎯 Executive Decision Snapshot</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="score-card">
                <div class="score-value">
                    {score:.0f}
                </div>
                <div class="score-label">
                    BUSINESS HEALTH SCORE
                </div>
                <br>
                <strong>{score_status}</strong>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="decision-card">
                <div class="decision-icon">🧠</div>
                <div class="decision-title">
                    AI Assessment
                </div>
                <div class="decision-text">
                    {score_message}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="decision-card">
                <div class="decision-icon">📌</div>
                <div class="decision-title">
                    Active Decision Context
                </div>
                <div class="decision-text">
                    Nex Decision AI is using
                    <strong>{filename}</strong>
                    as the current business context.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


st.progress(
    score / 100
)


# =========================================================
# AI RECOMMENDATIONS
# =========================================================

st.markdown(
    '<div class="section-title">🤖 AI Recommended Actions</div>',
    unsafe_allow_html=True
)

try:

    recommendations = copilot.recommendations()

except Exception:

    recommendations = []


if recommendations:

    for recommendation in recommendations:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="recommendation-card">
                    💡 <strong>Recommendation</strong><br>
                    {recommendation}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

else:

    st.info(
        "No additional recommendations were generated."
    )


# =========================================================
# PRIORITY ACTION
# =========================================================

st.markdown(
    '<div class="section-title">⚡ Recommended Next Action</div>',
    unsafe_allow_html=True
)


if score < 60:

    next_action = (
        "Improve data quality before building predictive models."
    )

elif score < 75:

    next_action = (
        "Investigate missing values and duplicate records."
    )

elif score < 90:

    next_action = (
        "Move into AutoML or forecasting to discover predictive patterns."
    )

else:

    next_action = (
        "Proceed to predictive modeling and business decision analysis."
    )


st.markdown(
    textwrap.dedent(
        f"""
        <div class="action-card">
            <div class="action-title">
                NEX DECISION AI RECOMMENDATION
            </div>
            <div class="action-text">
                ⚡ {next_action}
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# BUSINESS RISKS
# =========================================================

st.markdown(
    '<div class="section-title">🚨 Business Risk Signals</div>',
    unsafe_allow_html=True
)

risks = []


if summary.get("Missing", 0) > 0:

    risks.append(
        "Missing values may reduce the reliability of downstream analysis."
    )


if summary.get("Duplicates", 0) > 0:

    risks.append(
        "Duplicate records may distort patterns and model training."
    )


if len(df) < 100:

    risks.append(
        "The dataset contains relatively few records for reliable predictive modeling."
    )


if len(df.columns) < 5:

    risks.append(
        "The dataset has a limited number of available features."
    )


if risks:

    for risk in risks:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="risk-card">
                    🚨 {risk}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

else:

    st.success(
        "🟢 No major business risk signals detected."
    )


# =========================================================
# BUSINESS OPPORTUNITIES
# =========================================================

st.markdown(
    '<div class="section-title">🚀 AI Opportunity Areas</div>',
    unsafe_allow_html=True
)


opportunities = [
    (
        "📈 Predictive Analytics",
        "Use historical patterns to estimate future outcomes."
    ),
    (
        "👥 Customer Intelligence",
        "Identify customer behaviour and segmentation opportunities."
    ),
    (
        "⏳ Forecasting",
        "Detect trends and estimate future business movement."
    ),
    (
        "🚨 Anomaly Detection",
        "Identify unusual records and potentially important exceptions."
    ),
    (
        "📊 Executive Intelligence",
        "Convert analytical results into decision-ready dashboards."
    ),
    (
        "⚙️ Automation",
        "Reduce repetitive analysis and reporting work."
    )
]


opportunity_cols = st.columns(3)

for index, (title, description) in enumerate(
    opportunities
):

    with opportunity_cols[
        index % 3
    ]:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="opportunity-card">
                    <strong>{title}</strong>
                    <br><br>
                    <span style="color:#94a3b8;">
                        {description}
                    </span>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


# =========================================================
# BUSINESS QUESTION CENTER
# =========================================================

st.markdown(
    '<div class="section-title">🎯 Business Question Center</div>',
    unsafe_allow_html=True
)

st.caption(
    "Ask questions in business language. "
    "The Copilot will use the active dataset as context."
)


question_categories = {

    "📊 Understand the Business": [
        "Summarize the most important findings",
        "What are the most important patterns?",
        "What should an executive know about this dataset?"
    ],

    "🚨 Find Problems": [
        "What are the biggest risks?",
        "What problems exist in this dataset?",
        "Which areas need immediate attention?"
    ],

    "🚀 Find Opportunities": [
        "Where are the biggest opportunities?",
        "What business improvements do you recommend?",
        "How can this dataset create business value?"
    ],

    "🤖 Machine Learning": [
        "How ready is this dataset for machine learning?",
        "What prediction problems can be solved?",
        "Which machine learning approach should be considered?"
    ]

}


category = st.selectbox(
    "Choose a decision area",
    list(question_categories.keys())
)


selected_question = st.selectbox(
    "Choose a business question",
    [""] + question_categories[category]
)


custom_question = st.text_input(
    "Or ask your own question",
    placeholder="Example: Which areas of the business need attention?"
)


question = (
    custom_question.strip()
    if custom_question.strip()
    else selected_question
)


# =========================================================
# AI CHAT
# =========================================================

if question:

    with st.spinner(
        "🤖 Nex Decision AI is reasoning over your dataset..."
    ):

        try:

            answer = copilot.ask(
                question
            )

            st.markdown(
                '<div class="section-title">🧠 Copilot Decision</div>',
                unsafe_allow_html=True
            )

            if hasattr(
                answer,
                "shape"
            ):

                st.dataframe(
                    answer,
                    width="stretch",
                    hide_index=True
                )

            elif isinstance(
                answer,
                list
            ):

                for item in answer:

                    st.markdown(
                        textwrap.dedent(
                            f"""
                            <div class="recommendation-card">
                                💡 {item}
                            </div>
                            """
                        ),
                        unsafe_allow_html=True
                    )

            elif isinstance(
                answer,
                tuple
            ):

                st.write(answer)

            else:

                st.info(
                    str(answer)
                )

        except Exception as e:

            st.warning(
                "Nex Decision AI could not generate a response "
                "for this question using the current dataset."
            )

            with st.expander(
                "Technical details"
            ):

                st.write(str(e))


# =========================================================
# AI INSIGHT
# =========================================================

ai_insight(
    "The Business Copilot converts dataset intelligence "
    "into business-oriented questions, risks, opportunities "
    "and recommended actions. Use it as the decision layer "
    "before moving into predictive modeling."
)


# =========================================================
# NAVIGATION
# =========================================================

st.divider()

previous_col, center_col, next_col = st.columns(
    [1, 2, 1]
)

with previous_col:

    if st.button(
        "⬅️ Previous",
        width="stretch"
    ):

        st.switch_page(
            "pages/2_Dataset_Intelligence.py"
        )

with center_col:

    st.markdown(
        '<div style="text-align:center;color:#64748b;font-size:12px;">Step 3 of the intelligence workflow</div>',
        unsafe_allow_html=True
    )

with next_col:

    if st.button(
        "Next ➡️",
        width="stretch"
    ):

        st.switch_page(
            "pages/4_Executive_Dashboard.py"
        )


# =========================================================
# FOOTER
# =========================================================

page_footer()