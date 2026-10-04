
import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.database import Database
from src.ui.layout import page_header, ai_insight, page_footer


# ----------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------

st.set_page_config(
    page_title="Prediction History | NexDecision AI",
    page_icon="📜",
    layout="wide"
)

page_header(
    "📜 Prediction History",
    "Track, analyse, filter and export historical prediction activity."
)

st.caption(
    "Monitor prediction jobs, model usage, dataset activity "
    "and prediction workload over time."
)

st.markdown("---")


# ----------------------------------------------------
# CUSTOM STYLING
# ----------------------------------------------------

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.20);
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    .section-description {
        color: #888888;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------------------------------
# LOAD PREDICTION HISTORY
# ----------------------------------------------------

@st.cache_data(ttl=30, show_spinner=False)
def load_prediction_history():
    database = Database()
    records = database.get_predictions()

    columns = [
        "ID",
        "Model",
        "Filename",
        "Rows",
        "Prediction Time"
    ]

    return pd.DataFrame(records, columns=columns)


try:
    history_df = load_prediction_history()
except Exception as error:
    st.error(f"Unable to load prediction history: {error}")
    history_df = pd.DataFrame(
        columns=[
            "ID",
            "Model",
            "Filename",
            "Rows",
            "Prediction Time"
        ]
    )


# ----------------------------------------------------
# PREPARE DATA
# ----------------------------------------------------

if not history_df.empty:

    history_df["Rows"] = pd.to_numeric(
        history_df["Rows"],
        errors="coerce"
    )

    history_df["Prediction Time"] = pd.to_datetime(
        history_df["Prediction Time"],
        errors="coerce"
    )

    history_df["Model"] = (
        history_df["Model"]
        .fillna("Unknown")
        .astype(str)
    )

    history_df["Filename"] = (
        history_df["Filename"]
        .fillna("Unknown")
        .astype(str)
    )


# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("🔎 Prediction Filters")

if not history_df.empty:

    model_options = sorted(
        history_df["Model"].unique().tolist()
    )

    file_options = sorted(
        history_df["Filename"].unique().tolist()
    )

    selected_models = st.sidebar.multiselect(
        "Filter by model",
        options=model_options,
        default=model_options
    )

    selected_files = st.sidebar.multiselect(
        "Filter by dataset",
        options=file_options,
        default=file_options
    )

    search_text = st.sidebar.text_input(
        "Search records",
        placeholder="Search model, filename or ID..."
    )

    valid_dates = history_df[
        history_df["Prediction Time"].notna()
    ]["Prediction Time"]

    if not valid_dates.empty:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Prediction date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    else:
        date_range = None

    rows_values = history_df["Rows"].dropna()

    if not rows_values.empty:

        min_rows = int(rows_values.min())
        max_rows = int(rows_values.max())

        if min_rows < max_rows:
            selected_rows = st.sidebar.slider(
                "Dataset row count",
                min_value=min_rows,
                max_value=max_rows,
                value=(min_rows, max_rows)
            )
        else:
            selected_rows = (min_rows, max_rows)

    else:
        selected_rows = None

    if st.sidebar.button(
        "🔄 Refresh prediction history",
        use_container_width=True
    ):
        load_prediction_history.clear()
        st.rerun()

    st.sidebar.caption(
        "Filters apply to the records and charts on this page."
    )

else:

    selected_models = []
    selected_files = []
    search_text = ""
    date_range = None
    selected_rows = None


# ----------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------

filtered_df = history_df.copy()

if not history_df.empty:

    filtered_df = filtered_df[
        filtered_df["Model"].isin(selected_models)
        & filtered_df["Filename"].isin(selected_files)
    ]

    if search_text.strip():

        search = search_text.strip().lower()

        searchable = (
            filtered_df["Model"].str.lower().str.contains(
                search, na=False
            )
            | filtered_df["Filename"].str.lower().str.contains(
                search, na=False
            )
            | filtered_df["ID"].astype(str).str.contains(
                search, na=False
            )
        )

        filtered_df = filtered_df[searchable]

    if date_range and len(date_range) == 2:

        start_date, end_date = date_range

        prediction_dates = filtered_df["Prediction Time"].dt.date

        filtered_df = filtered_df[
            prediction_dates.isna()
            | (
                (prediction_dates >= start_date)
                & (prediction_dates <= end_date)
            )
        ]

    if selected_rows is not None:

        filtered_df = filtered_df[
            filtered_df["Rows"].isna()
            | (
                (filtered_df["Rows"] >= selected_rows[0])
                & (filtered_df["Rows"] <= selected_rows[1])
            )
        ]


# ----------------------------------------------------
# KPI SUMMARY
# ----------------------------------------------------

st.subheader("📈 Prediction Overview")

k1, k2, k3, k4 = st.columns(4)

total_predictions = len(filtered_df)

models_used = filtered_df["Model"].nunique()

datasets_used = filtered_df["Filename"].nunique()

total_rows = filtered_df["Rows"].sum()

with k1:
    st.metric(
        "Total Predictions",
        f"{total_predictions:,}"
    )

with k2:
    st.metric(
        "Models Used",
        f"{models_used:,}"
    )

with k3:
    st.metric(
        "Datasets Used",
        f"{datasets_used:,}"
    )

with k4:
    st.metric(
        "Total Rows Processed",
        f"{int(total_rows):,}"
        if pd.notna(total_rows)
        else "N/A"
    )

st.caption(
    f"Showing {total_predictions:,} of "
    f"{len(history_df):,} stored prediction records."
)

st.markdown("---")


# ----------------------------------------------------
# EMPTY STATE
# ----------------------------------------------------

if filtered_df.empty:

    if history_df.empty:
        st.info(
            "No prediction history is available yet. "
            "Run a prediction from the Prediction page first."
        )
    else:
        st.warning(
            "No records match the selected filters. "
            "Adjust the filters in the sidebar."
        )


# ----------------------------------------------------
# PREDICTION RECORDS
# ----------------------------------------------------

else:

    st.subheader("📋 Prediction Records")

    search_col, sort_col = st.columns([2, 1])

    with search_col:
        st.markdown(
            '<p class="section-description">'
            'Review historical prediction jobs and their metadata.'
            '</p>',
            unsafe_allow_html=True
        )

    with sort_col:
        sort_order = st.selectbox(
            "Sort records",
            [
                "Newest first",
                "Oldest first",
                "Largest dataset first",
                "Smallest dataset first"
            ]
        )

    display_df = filtered_df.copy()

    if sort_order == "Newest first":
        display_df = display_df.sort_values(
            "Prediction Time",
            ascending=False,
            na_position="last"
        )

    elif sort_order == "Oldest first":
        display_df = display_df.sort_values(
            "Prediction Time",
            ascending=True,
            na_position="last"
        )

    elif sort_order == "Largest dataset first":
        display_df = display_df.sort_values(
            "Rows",
            ascending=False,
            na_position="last"
        )

    else:
        display_df = display_df.sort_values(
            "Rows",
            ascending=True,
            na_position="last"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=350
    )

    csv_data = display_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Export Filtered History (CSV)",
        data=csv_data,
        file_name="nexdecision_prediction_history.csv",
        mime="text/csv",
        use_container_width=False
    )

    st.markdown("---")


    # ------------------------------------------------
    # PREDICTION ANALYTICS
    # ------------------------------------------------

    st.subheader("📊 Prediction Analytics")

    chart_left, chart_right = st.columns(2)

    model_count = (
        filtered_df["Model"]
        .value_counts()
        .rename_axis("Model")
        .reset_index(name="Predictions")
    )

    with chart_left:

        st.markdown("#### Predictions by Model")

        model_fig = px.bar(
            model_count,
            x="Model",
            y="Predictions",
            text="Predictions",
            color="Predictions",
            color_continuous_scale="Blues"
        )

        model_fig.update_layout(
            xaxis_title="Model",
            yaxis_title="Number of Predictions",
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        model_fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            model_fig,
            use_container_width=True
        )

    with chart_right:

        st.markdown("#### Model Usage Distribution")

        pie_fig = px.pie(
            model_count,
            names="Model",
            values="Predictions",
            hole=0.48
        )

        pie_fig.update_layout(
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )


    # ------------------------------------------------
    # DATASET ANALYTICS
    # ------------------------------------------------

    st.markdown("---")

    st.subheader("🗂️ Dataset Activity")

    dataset_count = (
        filtered_df["Filename"]
        .value_counts()
        .rename_axis("Dataset")
        .reset_index(name="Predictions")
    )

    dataset_left, dataset_right = st.columns(2)

    with dataset_left:

        st.markdown("#### Most Frequently Predicted Datasets")

        dataset_fig = px.bar(
            dataset_count.head(10).sort_values(
                "Predictions",
                ascending=True
            ),
            x="Predictions",
            y="Dataset",
            orientation="h",
            text="Predictions"
        )

        dataset_fig.update_layout(
            xaxis_title="Number of Predictions",
            yaxis_title="Dataset",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            dataset_fig,
            use_container_width=True
        )

    with dataset_right:

        st.markdown("#### Prediction Activity Over Time")

        time_df = filtered_df.dropna(
            subset=["Prediction Time"]
        ).copy()

        if not time_df.empty:

            time_df["Date"] = (
                time_df["Prediction Time"].dt.date
            )

            daily_count = (
                time_df.groupby("Date")
                .size()
                .reset_index(name="Predictions")
            )

            timeline_fig = px.line(
                daily_count,
                x="Date",
                y="Predictions",
                markers=True
            )

            timeline_fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Predictions",
                margin=dict(l=10, r=10, t=20, b=10)
            )

            st.plotly_chart(
                timeline_fig,
                use_container_width=True
            )

        else:
            st.info(
                "Valid prediction timestamps are not available "
                "for a timeline chart."
            )


    # ------------------------------------------------
    # RECORD DETAILS
    # ------------------------------------------------

    st.markdown("---")

    st.subheader("🔍 Inspect a Prediction Record")

    record_ids = filtered_df["ID"].tolist()

    model_names = (
        filtered_df.drop_duplicates("ID")
        .set_index("ID")["Model"]
        .to_dict()
    )

    selected_id = st.selectbox(
        "Select a prediction record",
        options=record_ids,
        format_func=lambda record_id: (
            f"{model_names.get(record_id, 'Unknown')} "
            f"(ID: {record_id})"
        )
    )

    selected_record = filtered_df[
        filtered_df["ID"] == selected_id
    ].iloc[0]

    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown("**Model**")
        st.write(selected_record["Model"])

    with d2:
        st.markdown("**Dataset**")
        st.write(selected_record["Filename"])

    with d3:
        st.markdown("**Rows Processed**")
        st.write(
            int(selected_record["Rows"])
            if pd.notna(selected_record["Rows"])
            else "Unknown"
        )

    st.markdown("**Prediction Time**")
    st.write(
        str(selected_record["Prediction Time"])
        if pd.notna(selected_record["Prediction Time"])
        else "Not recorded"
    )

    with st.expander("View complete record"):
        st.json(
            {
                key: (
                    str(value)
                    if pd.notna(value)
                    else None
                )
                for key, value in selected_record.to_dict().items()
            }
        )


# ----------------------------------------------------
# AI INSIGHT
# ----------------------------------------------------

st.markdown("---")

ai_insight(
    "Prediction History provides an audit trail of prediction jobs. "
    "Use the model and dataset charts to understand usage patterns. "
    "This history describes recorded activity; it does not by itself "
    "measure prediction accuracy or business impact."
)


# ----------------------------------------------------
# PAGE NAVIGATION
# ----------------------------------------------------

st.markdown("---")

st.subheader("🧭 Continue Exploring NexDecision AI")

prev_col, home_col, next_col = st.columns(3)

with prev_col:
    if st.button(
        "⬅️ Model History",
        use_container_width=True
    ):
        st.switch_page("pages/13_Model_History.py")

with home_col:
    if st.button(
        "🏠 Home",
        use_container_width=True
    ):
        st.switch_page("pages/0_Home.py")

with next_col:
    if st.button(
        "➡️ AI Anomaly Detection",
        use_container_width=True
    ):
        st.switch_page("pages/17_AI_Anomaly_Detection.py")


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

page_footer()
