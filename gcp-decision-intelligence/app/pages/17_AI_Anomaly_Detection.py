
import streamlit as st
import pandas as pd
import plotly.express as px

from src.anomaly_detection.anomaly_detector import AnomalyDetector
from src.ui.layout import page_header, ai_insight, page_footer


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Anomaly Detection | NexDecision AI",
    page_icon="🚨",
    layout="wide"
)

page_header(
    "🚨 AI Anomaly Detection",
    "Discover unusual patterns, investigate suspicious records, "
    "and export findings for further analysis."
)

st.caption(
    "Identify records that differ from the patterns in your dataset. "
    "An anomaly is a signal to investigate, not proof of fraud or an error."
)

st.markdown("---")


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.20);
        padding: 16px;
        border-radius: 12px;
    }

    .section-description {
        color: #888888;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# CHECK DATASET
# --------------------------------------------------

if "dataset" not in st.session_state:
    st.warning(
        "⚠️ No dataset found. Upload a dataset before running "
        "anomaly detection."
    )

    if st.button("🏠 Go to Home"):
        st.switch_page("pages/0_Home.py")

    st.stop()

df = st.session_state["dataset"]

if not isinstance(df, pd.DataFrame) or df.empty:
    st.error(
        "The current dataset is empty or invalid. "
        "Upload a non-empty dataset and try again."
    )
    st.stop()

st.success("✅ Dataset loaded successfully")


# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

st.subheader("📊 Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📄 Total Rows", f"{len(df):,}")

with c2:
    st.metric("📊 Total Columns", f"{len(df.columns):,}")

with c3:
    st.metric(
        "⚠️ Missing Values",
        f"{int(df.isna().sum().sum()):,}"
    )

with c4:
    st.metric(
        "🔁 Duplicate Rows",
        f"{int(df.duplicated().sum()):,}"
    )

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

st.caption(
    f"Numeric features available: {len(numeric_columns)}"
)

st.markdown("---")


# --------------------------------------------------
# RUN ANOMALY DETECTION
# --------------------------------------------------

st.subheader("🔍 Detection Engine")

st.markdown(
    '<p class="section-description">'
    'Run the existing anomaly detector against the current dataset.'
    '</p>',
    unsafe_allow_html=True
)

run_detection = st.button(
    "🚀 Run Anomaly Detection",
    type="primary",
    use_container_width=False
)

if run_detection:
    try:
        with st.spinner("Analysing data for unusual patterns..."):
            detector = AnomalyDetector()
            result = detector.detect(df.copy())

        if result is None:
            st.session_state.pop(
                "anomaly_detection_result",
                None
            )
            st.error(
                "The detector could not produce a result. "
                "Check that your dataset contains usable numeric columns."
            )

        elif not isinstance(result, pd.DataFrame):
            st.session_state.pop(
                "anomaly_detection_result",
                None
            )
            st.error(
                "The detector returned an unexpected result format. "
                "Expected a pandas DataFrame."
            )

        elif "Anomaly" not in result.columns:
            st.session_state.pop(
                "anomaly_detection_result",
                None
            )
            st.error(
                "The detector output does not contain the required "
                "'Anomaly' column. Check anomaly_detector.py."
            )

        elif result.empty:
            st.session_state["anomaly_detection_result"] = result
            st.info("The detector returned no records.")

        else:
            st.session_state["anomaly_detection_result"] = result
            st.success("✅ Anomaly detection completed.")

    except Exception as error:
        st.error(f"Anomaly detection failed: {error}")


# --------------------------------------------------
# LOAD LATEST RESULTS
# --------------------------------------------------

if "anomaly_detection_result" not in st.session_state:
    st.info(
        "Select **Run Anomaly Detection** to analyse your dataset."
    )
    st.stop()

result = st.session_state["anomaly_detection_result"].copy()

if result.empty:
    st.info("No records were returned by the detector.")
    st.stop()

if "Anomaly" not in result.columns:
    st.error(
        "The saved detection result is missing the Anomaly column. "
        "Run detection again."
    )
    st.stop()


# --------------------------------------------------
# NORMALISE RESULT LABELS
# --------------------------------------------------

result["Anomaly"] = (
    result["Anomaly"]
    .astype(str)
    .str.strip()
    .str.title()
)

anomaly_df = result[
    result["Anomaly"] == "Anomaly"
].copy()

normal_df = result[
    result["Anomaly"] == "Normal"
].copy()

other_df = result[
    ~result["Anomaly"].isin(["Anomaly", "Normal"])
].copy()

total = len(result)
anomalies = len(anomaly_df)
normal = len(normal_df)
other = len(other_df)

percentage = (
    round((anomalies / total) * 100, 2)
    if total > 0
    else 0
)


# --------------------------------------------------
# ANOMALY SUMMARY
# --------------------------------------------------

st.markdown("---")
st.subheader("📈 Detection Summary")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Analysed", f"{total:,}")

with k2:
    st.metric("Normal Records", f"{normal:,}")

with k3:
    st.metric(
        "Anomalies Detected",
        f"{anomalies:,}",
        delta=f"{percentage}% of records",
        delta_color="inverse"
    )

with k4:
    st.metric("Other Labels", f"{other:,}")

st.progress(
    min(max(percentage / 100, 0.0), 1.0),
    text=f"Anomaly share: {percentage}%"
)

st.caption(
    "The anomaly percentage is the share of records labelled "
    "'Anomaly' by the detector. It is not a fraud probability."
)


# --------------------------------------------------
# RESULT FILTERS
# --------------------------------------------------

st.markdown("---")
st.subheader("🔎 Explore Detection Results")

filter_col, search_col = st.columns([1, 2])

with filter_col:
    label_options = sorted(
        result["Anomaly"].dropna().unique().tolist()
    )

    selected_labels = st.multiselect(
        "Record classification",
        options=label_options,
        default=label_options
    )

with search_col:
    record_search = st.text_input(
        "Search result records",
        placeholder="Search across the available result values..."
    )

filtered_result = result[
    result["Anomaly"].isin(selected_labels)
].copy()

if record_search.strip():
    query = record_search.strip().lower()

    row_matches = filtered_result.astype(str).apply(
        lambda column: column.str.lower().str.contains(
            query,
            na=False,
            regex=False
        )
    ).any(axis=1)

    filtered_result = filtered_result[row_matches]

st.caption(
    f"Displaying {len(filtered_result):,} of {len(result):,} records."
)


# --------------------------------------------------
# RESULT TABLE
# --------------------------------------------------

st.subheader("📋 Detection Results")

st.dataframe(
    filtered_result,
    use_container_width=True,
    hide_index=True,
    height=350
)


# --------------------------------------------------
# ANOMALY-ONLY TABLE
# --------------------------------------------------

st.markdown("---")
st.subheader("🚨 Anomaly Investigation")

if anomaly_df.empty:
    st.success(
        "No records were labelled as anomalies in this run."
    )

else:
    st.write(
        f"Found **{len(anomaly_df):,}** records for further review."
    )

    with st.expander(
        "View detected anomaly records",
        expanded=True
    ):
        st.dataframe(
            anomaly_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )

    if numeric_columns:
        available_features = [
            column
            for column in numeric_columns
            if column in anomaly_df.columns
        ]

        if available_features:
            selected_feature = st.selectbox(
                "Inspect an anomaly feature",
                options=available_features
            )

            feature_values = pd.to_numeric(
                anomaly_df[selected_feature],
                errors="coerce"
            ).dropna()

            if not feature_values.empty:
                st.metric(
                    f"Average {selected_feature} in anomalies",
                    f"{feature_values.mean():,.3f}"
                )

                st.caption(
                    "This statistic describes flagged records only; "
                    "compare it with normal records before drawing conclusions."
                )


# --------------------------------------------------
# VISUAL ANALYTICS
# --------------------------------------------------

st.markdown("---")
st.subheader("📊 Anomaly Analytics")

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown("#### Normal vs Anomaly")

    distribution = (
        result["Anomaly"]
        .value_counts()
        .rename_axis("Classification")
        .reset_index(name="Records")
    )

    pie_fig = px.pie(
        distribution,
        names="Classification",
        values="Records",
        hole=0.48
    )

    pie_fig.update_layout(
        margin=dict(l=10, r=10, t=25, b=10)
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

with chart_right:
    st.markdown("#### Classification Counts")

    bar_fig = px.bar(
        distribution,
        x="Classification",
        y="Records",
        text="Records"
    )

    bar_fig.update_layout(
        xaxis_title="Classification",
        yaxis_title="Number of Records",
        showlegend=False,
        margin=dict(l=10, r=10, t=25, b=10)
    )

    bar_fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        bar_fig,
        use_container_width=True
    )


# --------------------------------------------------
# NUMERIC FEATURE COMPARISON
# --------------------------------------------------

st.markdown("---")
st.subheader("📉 Numeric Feature Comparison")

shared_numeric = [
    column
    for column in numeric_columns
    if column in result.columns
]

if shared_numeric and result["Anomaly"].nunique() > 1:

    selected_numeric = st.selectbox(
        "Choose a numeric feature",
        options=shared_numeric,
        key="anomaly_feature_comparison"
    )

    comparison_df = result.copy()

    comparison_df[selected_numeric] = pd.to_numeric(
        comparison_df[selected_numeric],
        errors="coerce"
    )

    comparison_df = comparison_df.dropna(
        subset=[selected_numeric]
    )

    if not comparison_df.empty:

        box_fig = px.box(
            comparison_df,
            x="Anomaly",
            y=selected_numeric,
            color="Anomaly",
            points="outliers",
            title=f"{selected_numeric}: Normal vs Anomaly"
        )

        box_fig.update_layout(
            xaxis_title="Detector classification",
            yaxis_title=selected_numeric
        )

        st.plotly_chart(
            box_fig,
            use_container_width=True
        )

        st.caption(
            "This chart compares feature values by detector label. "
            "It does not establish the cause of an anomaly."
        )

else:
    st.info(
        "Feature comparison requires numeric columns in the detection "
        "results and at least two classification groups."
    )


# --------------------------------------------------
# DOWNLOAD REPORTS
# --------------------------------------------------

st.markdown("---")
st.subheader("📥 Export Detection Reports")

export_all_col, export_anomaly_col = st.columns(2)

with export_all_col:
    st.download_button(
        "📄 Download Full Detection Results",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="nexdecision_full_detection_report.csv",
        mime="text/csv",
        use_container_width=True
    )

with export_anomaly_col:
    st.download_button(
        "🚨 Download Anomaly-Only Report",
        data=anomaly_df.to_csv(index=False).encode("utf-8"),
        file_name="nexdecision_anomaly_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# --------------------------------------------------
# BUSINESS INTERPRETATION
# --------------------------------------------------

st.markdown("---")
st.subheader("🤖 Interpretation & Next Steps")

if anomalies == 0:
    st.info(
        "The detector did not label any records as anomalies. "
        "This does not guarantee that every record is correct or normal."
    )

elif percentage < 5:
    st.info(
        f"{percentage}% of records were flagged. Start by reviewing "
        "the flagged rows, checking data quality, and comparing their "
        "feature values with normal records."
    )

elif percentage < 15:
    st.warning(
        f"{percentage}% of records were flagged. Investigate recurring "
        "patterns, unusual values, and possible changes in data collection "
        "or business operations."
    )

else:
    st.warning(
        f"{percentage}% of records were flagged. Review the detector's "
        "output and dataset characteristics before treating this as an "
        "operational issue. A high anomaly rate may also reflect the "
        "data distribution or detector settings."
    )

ai_insight(
    "Anomaly detection highlights records that differ from learned or "
    "configured patterns. Investigate flagged records using business "
    "context before making operational decisions. Validate the detector "
    "against labelled examples when possible."
)


# --------------------------------------------------
# PAGE NAVIGATION
# --------------------------------------------------

st.markdown("---")
st.subheader("🧭 Continue Exploring NexDecision AI")

prev_col, home_col, next_col = st.columns(3)

with prev_col:
    if st.button(
        "⬅️ Prediction History",
        use_container_width=True
    ):
        st.switch_page("pages/14_Prediction_History.py")

with home_col:
    if st.button(
        "🏠 Home",
        use_container_width=True
    ):
        st.switch_page("pages/0_Home.py")

with next_col:
    if st.button(
        "➡️ Executive Report",
        use_container_width=True
    ):
        st.switch_page("pages/18_Executive_Report.py")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

page_footer()
