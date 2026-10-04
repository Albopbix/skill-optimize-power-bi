
import streamlit as st
import pandas as pd
import numpy as np

from src.ai_chat.chat_engine import ChatEngine
from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Business Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM DESIGN
# ==========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
        transition: 0.2s ease;
    }

    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        padding: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# INITIALIZE SESSION STATE
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "chatbot_page" not in st.session_state:
    st.session_state["chatbot_page"] = "Overview"

if "chat_question" not in st.session_state:
    st.session_state["chat_question"] = ""

if "chat_dataset_signature" not in st.session_state:
    st.session_state["chat_dataset_signature"] = None


# ==========================================================
# PAGE HEADER
# ==========================================================

page_header(
    "🤖 AI Business Chatbot",
    "Explore your data, ask questions in natural language, "
    "and discover useful business insights."
)


# ==========================================================
# CHECK DATASET
# ==========================================================

if "dataset" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.info("Go to Upload Dataset, upload a CSV or Excel file, "
            "and return to the AI Business Chatbot.")
    page_footer()
    st.stop()

df = st.session_state["dataset"]

if not isinstance(df, pd.DataFrame):
    st.error("The loaded dataset is not a valid pandas DataFrame.")
    page_footer()
    st.stop()

if df.empty:
    st.warning("Your dataset contains no rows.")
    page_footer()
    st.stop()


# ==========================================================
# RESET CHAT WHEN DATASET CHANGES
# ==========================================================

dataset_signature = (
    len(df),
    len(df.columns),
    tuple(str(column) for column in df.columns),
)

if (
    st.session_state["chat_dataset_signature"]
    != dataset_signature
):
    st.session_state["chat_history"] = []
    st.session_state["chat_dataset_signature"] = dataset_signature


# ==========================================================
# DATA PREPARATION
# ==========================================================

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

categorical_cols = df.select_dtypes(
    include=["object", "category", "bool", "string"]
).columns.tolist()

datetime_cols = df.select_dtypes(
    include=["datetime", "datetimetz"]
).columns.tolist()

missing_cells = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())
memory_mb = float(
    df.memory_usage(index=True, deep=True).sum() / (1024 ** 2)
)

engine = ChatEngine()


# ==========================================================
# REUSABLE CHAT FUNCTION
# ==========================================================

def ask_chatbot(question):
    """Ask the existing ChatEngine and store the conversation."""

    question = question.strip()

    if not question:
        st.warning("Please enter a question.")
        return

    st.session_state["chat_history"].append(
        ("You", question)
    )

    try:
        with st.spinner("🤖 Analyzing your dataset..."):
            answer = engine.ask(df, question)

        if answer is None:
            answer = "The AI engine returned an empty response."

        st.session_state["chat_history"].append(
            ("AI", str(answer))
        )

    except Exception as error:
        st.session_state["chat_history"].append(
            (
                "AI",
                "I couldn't process that question. "
                "Please try rephrasing it or check your AI configuration. "
                f"Technical details: {error}",
            )
        )


# ==========================================================
# NAVIGATION DEFINITIONS
# ==========================================================

nav_items = [
    ("Overview", "🏠 Overview"),
    ("Chat", "💬 Chat"),
    ("Data Insights", "📊 Data Insights"),
    ("Data Preview", "🗂️ Data Preview"),
    ("Help", "❓ Help"),
]


# ==========================================================
# MAIN PAGE CONTENT
# ==========================================================

current_page = st.session_state["chatbot_page"]


# ----------------------------------------------------------
# PAGE 1: OVERVIEW
# ----------------------------------------------------------

if current_page == "Overview":

    st.subheader("📊 Dataset Overview")

    st.success("✅ Dataset loaded successfully")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Rows", f"{len(df):,}")

    with c2:
        st.metric("Total Columns", f"{len(df.columns):,}")

    with c3:
        st.metric("Missing Cells", f"{missing_cells:,}")

    with c4:
        st.metric("Duplicate Rows", f"{duplicate_rows:,}")

    c5, c6, c7 = st.columns(3)

    with c5:
        st.metric("Numeric Columns", len(numeric_cols))

    with c6:
        st.metric("Categorical Columns", len(categorical_cols))

    with c7:
        st.metric("Dataset Memory", f"{memory_mb:.2f} MB")

    st.divider()

    st.subheader("🧠 What can your AI assistant do?")

    feature_cols = st.columns(3)

    with feature_cols[0]:
        st.markdown("### 🔍 Understand")
        st.write(
            "Ask about dataset structure, column meanings, "
            "data types, and statistical summaries."
        )

    with feature_cols[1]:
        st.markdown("### 📈 Analyze")
        st.write(
            "Explore missing values, distributions, "
            "correlations, and possible data-quality issues."
        )

    with feature_cols[2]:
        st.markdown("### 💡 Discover")
        st.write(
            "Investigate patterns and ask questions that "
            "support business and machine-learning workflows."
        )

    st.divider()

    st.subheader("🚀 Start with a question")

    starter_questions = [
        "How many rows and columns are in my dataset?",
        "Which columns have the most missing values?",
        "Summarize the numeric columns.",
        "What data preprocessing should I consider?",
    ]

    for i, prompt in enumerate(starter_questions):
        if st.button(
            f"💬 {prompt}",
            key=f"overview_prompt_{i}",
            use_container_width=True,
        ):
            st.session_state["chatbot_page"] = "Chat"
            st.session_state["chat_history"].append(
                ("You", prompt)
            )

            try:
                with st.spinner("🤖 Analyzing your dataset..."):
                    answer = engine.ask(df, prompt)

                st.session_state["chat_history"].append(
                    (
                        "AI",
                        str(answer) if answer is not None
                        else "The AI engine returned an empty response.",
                    )
                )

            except Exception as error:
                st.session_state["chat_history"].append(
                    (
                        "AI",
                        f"Unable to process the question: {error}",
                    )
                )

            st.rerun()


# ----------------------------------------------------------
# PAGE 2: CHAT
# ----------------------------------------------------------

elif current_page == "Chat":

    st.subheader("💬 Chat with Your Data")

    st.caption(
        "Ask questions about your loaded dataset in plain English."
    )

    with st.expander("💡 Suggested questions", expanded=True):

        prompt_options = [
            "How many rows are in my dataset?",
            "Which column has the most missing values?",
            "What are the numeric columns?",
            "Summarize my dataset.",
            "What preprocessing should I perform?",
            "Is this dataset suitable for prediction?",
            "Which columns have unusual values?",
            "Explain the relationships between numeric columns.",
        ]

        selected_prompt = st.selectbox(
            "Choose a question",
            prompt_options,
            key="suggested_chat_prompt",
        )

        if st.button(
            "Use Suggested Question",
            key="use_suggested_prompt",
        ):
            st.session_state["chat_question"] = selected_prompt
            st.rerun()

    with st.form("chat_question_form", clear_on_submit=True):

        question = st.text_input(
            "Ask a question about your dataset",
            placeholder="Example: Which columns have missing values?",
            key="chat_form_question",
        )

        ask = st.form_submit_button(
            "🤖 Ask AI",
            use_container_width=True,
        )

    if ask:
        if question.strip():
            ask_chatbot(question)
        else:
            st.warning("Please enter a question.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "🗑️ Clear Conversation",
            use_container_width=True,
        ):
            st.session_state["chat_history"] = []
            st.rerun()

    with c2:
        conversation_text = "\n\n".join(
            f"{sender}: {message}"
            for sender, message in st.session_state["chat_history"]
        )

        st.download_button(
            "📥 Export Conversation",
            data=conversation_text or "No conversation yet.",
            file_name="ai_chat_conversation.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.divider()

    st.subheader("📝 Conversation History")

    if not st.session_state["chat_history"]:
        st.info(
            "Your conversation will appear here. "
            "Start by asking a question above."
        )

    else:
        for sender, message in st.session_state["chat_history"]:

            if sender == "You":
                with st.chat_message("user"):
                    st.write(message)

            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message)


# ----------------------------------------------------------
# PAGE 3: DATA INSIGHTS
# ----------------------------------------------------------

elif current_page == "Data Insights":

    st.subheader("📊 Data Insights & Quality")

    st.write(
        "Explore statistical summaries and common data-quality "
        "issues before building a machine-learning model."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Missing Values",
            "Statistics",
            "Correlations",
            "Column Profiles",
        ]
    )

    # Missing values
    with tab1:

        missing_report = pd.DataFrame({
            "Column": df.columns.astype(str),
            "Missing Count": df.isna().sum().values,
            "Missing Percentage": (
                df.isna().mean().values * 100
            ).round(2),
            "Data Type": df.dtypes.astype(str).values,
        })

        missing_report = missing_report.sort_values(
            "Missing Count",
            ascending=False,
        )

        st.dataframe(
            missing_report,
            use_container_width=True,
            hide_index=True,
        )

        if missing_cells == 0:
            st.success("No missing values were detected.")
        else:
            st.warning(
                f"Found {missing_cells:,} missing cells. "
                "Review the affected columns before modeling."
            )

    # Numeric statistics
    with tab2:

        if numeric_cols:
            st.dataframe(
                df[numeric_cols].describe().T.round(3),
                use_container_width=True,
            )
        else:
            st.info("No numeric columns are available.")

    # Correlations
    with tab3:

        if len(numeric_cols) >= 2:

            correlation = df[numeric_cols].corr(
                numeric_only=True
            )

            st.dataframe(
                correlation.round(3),
                use_container_width=True,
            )

            try:
                import plotly.express as px

                fig = px.imshow(
                    correlation,
                    text_auto=".2f",
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title="Numeric Feature Correlation Matrix",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            except Exception as error:
                st.caption(
                    f"Correlation table is available; "
                    f"heatmap could not be displayed: {error}"
                )

        else:
            st.info(
                "At least two numeric columns are needed "
                "to calculate correlations."
            )

    # Column profiles
    with tab4:

        selected_column = st.selectbox(
            "Select a column",
            df.columns.tolist(),
            format_func=str,
        )

        series = df[selected_column]

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric("Data Type", str(series.dtype))

        with p2:
            st.metric("Unique Values", int(series.nunique()))

        with p3:
            st.metric("Missing Values", int(series.isna().sum()))

        st.markdown("**Most frequent values**")

        value_counts = (
            series.astype("string")
            .fillna("(Missing)")
            .value_counts()
            .head(10)
            .rename_axis("Value")
            .reset_index(name="Count")
        )

        st.dataframe(
            value_counts,
            use_container_width=True,
            hide_index=True,
        )


# ----------------------------------------------------------
# PAGE 4: DATA PREVIEW
# ----------------------------------------------------------

elif current_page == "Data Preview":

    st.subheader("🗂️ Data Explorer")

    st.write(
        "Inspect records, choose the columns to display, "
        "and download a copy of your dataset."
    )

    st.caption(
        f"Dataset dimensions: {len(df):,} rows × "
        f"{len(df.columns):,} columns"
    )

    selected_columns = st.multiselect(
        "Choose columns to display",
        options=df.columns.tolist(),
        default=df.columns.tolist(),
        format_func=str,
    )

    if selected_columns:

        preview_rows = st.slider(
            "Number of rows to preview",
            min_value=5,
            max_value=max(5, min(len(df), 500)),
            value=min(len(df), 50),
            step=5,
        )

        st.dataframe(
            df[selected_columns].head(preview_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "📥 Download Selected Columns as CSV",
            data=df[selected_columns].to_csv(index=False).encode("utf-8"),
            file_name="dataset_selected_columns.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:
        st.info("Select at least one column to preview the data.")

    st.divider()

    st.subheader("🔎 Dataset Structure")

    structure = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": df.dtypes.astype(str).values,
        "Non-null Values": df.notna().sum().values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values,
    })

    st.dataframe(
        structure,
        use_container_width=True,
        hide_index=True,
    )


# ----------------------------------------------------------
# PAGE 5: HELP
# ----------------------------------------------------------

elif current_page == "Help":

    st.subheader("❓ Help & Usage Guide")

    with st.expander("How do I start?", expanded=True):
        st.markdown(
            """
            1. Upload a dataset using the Upload Dataset page.
            2. Open the AI Business Chatbot.
            3. Select **Chat** from the navigation buttons.
            4. Enter a question about your dataset.
            5. Review the response and use Data Insights for
               additional statistical information.
            """
        )

    with st.expander("What questions can I ask?"):
        st.markdown(
            """
            - How many rows and columns are present?
            - Which columns contain missing values?
            - What are the distributions of numeric columns?
            - What preprocessing might be required?
            - Which numeric columns are correlated?
            - What should I investigate before training a model?
            """
        )

    with st.expander("How reliable are the answers?"):
        st.markdown(
            """
            AI responses can be incomplete or incorrect. Verify
            important conclusions against the actual dataset and
            statistical summaries. Correlation does not establish
            causation, and predictive suitability depends on the
            target variable, data quality, and modeling objective.
            """
        )

    with st.expander("Troubleshooting"):
        st.markdown(
            """
            - **No dataset:** Upload one before opening the chatbot.
            - **AI error:** Check the configuration and dependencies
              required by your existing ChatEngine.
            - **Unexpected result:** Rephrase the question and compare
              the response with the Data Insights page.
            - **Large dataset:** Use a smaller preview for easier
              inspection.
            """
        )


# ==========================================================
# AI INSIGHT
# ==========================================================

st.divider()

ai_insight(
    "The AI Business Chatbot combines natural-language questions "
    "with dataset exploration, statistical summaries, data-quality "
    "checks, and conversational history. Validate AI-generated "
    "conclusions against the underlying data."
)
# ==========================================================
# PREVIOUS / NEXT PAGE NAVIGATION
# ==========================================================

st.divider()
st.subheader("🧭 Page Navigation")

col_prev, col_home, col_next = st.columns(3)

with col_prev:
    if st.button("⬅️ Previous Page", use_container_width=True):
        st.switch_page("pages/9_Interactive_Dashboard.py")

with col_home:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/0_Home.py")

with col_next:
    if st.button("Next Page ➡️", use_container_width=True):
        st.switch_page("pages/12_Dataset_History.py")



# ==========================================================
# FOOTER
# ==========================================================

page_footer()
