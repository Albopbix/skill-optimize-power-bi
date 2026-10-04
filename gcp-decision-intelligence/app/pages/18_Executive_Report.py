
import os
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer
from src.executive_reports.report_builder import ExecutiveReportBuilder


# ------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------

st.set_page_config(
    page_title="Executive Report | NexDecision AI",
    page_icon="📄",
    layout="wide"
)

page_header(
    "📄 Executive Report Generator",
    "Create management-ready reports from dataset quality metrics "
    "and your existing AI analysis workflow."
)

st.caption(
    "Review data quality, understand potential risks, and export "
    "a PDF report for business stakeholders."
)

st.markdown("---")


# ------------------------------------------------
# CUSTOM STYLING
# ------------------------------------------------

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


# ------------------------------------------------
# CHECK DATASET
# ------------------------------------------------

if "dataset" not in st.session_state:
    st.warning(
        "No dataset is loaded. Upload a dataset before generating "
        "an executive report."
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


# ------------------------------------------------
# DATASET STATISTICS
# ------------------------------------------------

rows = len(df)
columns = len(df.columns)
missing = int(df.isnull().sum().sum())
duplicates = int(df.duplicated().sum())

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

categorical_columns = df.select_dtypes(
    include=["object", "category", "string"]
).columns.tolist()

missing_percentage = (
    round((missing / (rows * columns)) * 100, 2)
    if rows > 0 and columns > 0
    else 0
)

duplicate_percentage = (
    round((duplicates / rows) * 100, 2)
    if rows > 0
    else 0
)

dataset_summary = {
    "Rows": rows,
    "Columns": columns,
    "Missing": missing,
    "Duplicates": duplicates
}


# ------------------------------------------------
# DATA QUALITY SCORE
# ------------------------------------------------
# A simple heuristic, not a validated business score.
# ------------------------------------------------

health = 100

health -= min(missing_percentage * 0.7, 50)
health -= min(duplicate_percentage * 0.5, 30)

health = max(0, min(100, round(health)))

if health >= 90:
    grade = "Excellent"
elif health >= 75:
    grade = "Good"
elif health >= 60:
    grade = "Needs Attention"
else:
    grade = "Poor"


# ------------------------------------------------
# EXECUTIVE SUMMARY
# ------------------------------------------------

st.subheader("📊 Executive Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📄 Total Records", f"{rows:,}")

with c2:
    st.metric("📊 Total Features", f"{columns:,}")

with c3:
    st.metric(
        "⚠️ Missing Values",
        f"{missing:,}",
        delta=f"{missing_percentage}% of cells",
        delta_color="inverse"
    )

with c4:
    st.metric(
        "🔁 Duplicate Rows",
        f"{duplicates:,}",
        delta=f"{duplicate_percentage}% of rows",
        delta_color="inverse"
    )

st.markdown("---")

score_col, grade_col, numeric_col, category_col = st.columns(4)

with score_col:
    st.metric(
        "Dataset Quality Score",
        f"{health}/100"
    )

with grade_col:
    st.metric(
        "Quality Category",
        grade
    )

with numeric_col:
    st.metric(
        "Numeric Features",
        len(numeric_columns)
    )

with category_col:
    st.metric(
        "Categorical Features",
        len(categorical_columns)
    )

st.progress(
    health / 100,
    text=f"Heuristic dataset quality score: {health}/100"
)

st.caption(
    "The score is a simple internal heuristic based on missing-cell "
    "and duplicate-row percentages. It is not a validated measure of "
    "overall business health, model readiness, or business performance."
)

st.markdown("---")


# ------------------------------------------------
# DATA QUALITY VISUALIZATION
# ------------------------------------------------

st.subheader("🔬 Dataset Quality Analysis")

quality_left, quality_right = st.columns(2)

with quality_left:

    st.markdown("#### Missing vs Available Cells")

    total_cells = rows * columns
    available_cells = max(0, total_cells - missing)

    quality_chart_df = pd.DataFrame({
        "Cell Status": ["Available", "Missing"],
        "Cells": [available_cells, missing]
    })

    quality_fig = px.pie(
        quality_chart_df,
        names="Cell Status",
        values="Cells",
        hole=0.5
    )

    quality_fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(
        quality_fig,
        use_container_width=True
    )

with quality_right:

    st.markdown("#### Missing Values by Feature")

    missing_by_column = (
        df.isnull()
        .sum()
        .sort_values(ascending=False)
        .head(15)
    )

    missing_df = (
        missing_by_column
        .rename_axis("Feature")
        .reset_index(name="Missing Values")
    )

    missing_df = missing_df[
        missing_df["Missing Values"] > 0
    ]

    if not missing_df.empty:

        missing_fig = px.bar(
            missing_df.sort_values(
                "Missing Values",
                ascending=True
            ),
            x="Missing Values",
            y="Feature",
            orientation="h",
            text="Missing Values"
        )

        missing_fig.update_layout(
            xaxis_title="Number of Missing Values",
            yaxis_title="Feature",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            missing_fig,
            use_container_width=True
        )

    else:
        st.success(
            "No missing values were found in the current dataset."
        )

st.markdown("---")


# ------------------------------------------------
# AUTOMATED QUALITY FINDINGS
# ------------------------------------------------

st.subheader("🧠 Key Findings")

findings = []

if missing == 0:
    findings.append(
        "No missing cells were found in the current dataset."
    )
else:
    findings.append(
        f"{missing:,} missing cells were detected "
        f"({missing_percentage}% of all cells)."
    )

if duplicates == 0:
    findings.append(
        "No fully duplicated rows were found."
    )
else:
    findings.append(
        f"{duplicates:,} fully duplicated rows were found "
        f"({duplicate_percentage}% of all records)."
    )

findings.append(
    f"The dataset contains {len(numeric_columns)} numeric "
    f"and {len(categorical_columns)} categorical features."
)

for finding in findings:
    st.markdown(f"- {finding}")

st.markdown("---")


# ------------------------------------------------
# AUTO ML SUMMARY
# ------------------------------------------------

st.subheader("🤖 AutoML Summary")

automl_result = (
    "AutoML execution status and model performance were not retrieved "
    "by this report page. Open the AutoML page to inspect the actual "
    "models evaluated, metrics, and selected model."
)

st.info(automl_result)

if st.button(
    "🧪 Open AutoML",
    use_container_width=False
):
    st.switch_page("pages/5_AutoML.py")

st.caption(
    "This report does not claim that a best model was found unless "
    "the actual AutoML results are connected to the report builder."
)

st.markdown("---")


# ------------------------------------------------
# ANOMALY SUMMARY
# ------------------------------------------------

st.subheader("🚨 Anomaly Detection Summary")

anomaly_summary = (
    "Anomaly detection results have not been connected directly to "
    "this report page. Visit AI Anomaly Detection to run the detector "
    "and review flagged records."
)

anomaly_result = st.session_state.get(
    "anomaly_detection_result"
)

if isinstance(anomaly_result, pd.DataFrame) and (
    not anomaly_result.empty
    and "Anomaly" in anomaly_result.columns
):

    labels = (
        anomaly_result["Anomaly"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    anomaly_count = int(
        (labels == "Anomaly").sum()
    )

    anomaly_rate = round(
        anomaly_count / len(anomaly_result) * 100,
        2
    )

    anomaly_summary = (
        f"The most recently stored anomaly detection result contains "
        f"{len(anomaly_result):,} analysed records, with "
        f"{anomaly_count:,} labelled as anomalies "
        f"({anomaly_rate}%). These are detector labels, not confirmed "
        f"fraud or errors."
    )

    st.info(anomaly_summary)

else:
    st.info(anomaly_summary)

if st.button(
    "🚨 Open AI Anomaly Detection",
    use_container_width=False
):
    st.switch_page("pages/17_AI_Anomaly_Detection.py")

st.markdown("---")


# ------------------------------------------------
# RECOMMENDATIONS
# ------------------------------------------------

st.subheader("💡 Recommended Next Steps")

recommendations = []

if missing > 0:
    recommendations.append(
        "Inspect missing values by feature and choose suitable "
        "imputation or exclusion rules before modelling."
    )

if duplicates > 0:
    recommendations.append(
        "Review duplicate records and remove them only when they "
        "represent unintended duplication."
    )

if numeric_columns:
    recommendations.append(
        "Review numeric feature distributions and potential outliers."
    )

if categorical_columns:
    recommendations.append(
        "Check category consistency, spelling differences, and "
        "high-cardinality fields."
    )

recommendations.extend([
    "Validate data types, ranges, and business rules.",
    "Compare candidate models using appropriate validation metrics.",
    "Track model performance and data quality as new data arrives."
])

for number, recommendation in enumerate(
    recommendations,
    start=1
):
    st.markdown(f"**{number}.** {recommendation}")

st.markdown("---")


# ------------------------------------------------
# REPORT CONFIGURATION
# ------------------------------------------------

st.subheader("⚙️ Configure Your Report")

report_title = st.text_input(
    "Report title",
    value="NexDecision AI - Executive Data Report"
)

prepared_for = st.text_input(
    "Prepared for / department",
    placeholder="e.g. Management, Analytics Team"
)

include_recommendations = st.checkbox(
    "Include recommendations",
    value=True
)

include_anomaly_summary = st.checkbox(
    "Include anomaly summary",
    value=True
)

final_recommendations = (
    recommendations
    if include_recommendations
    else []
)

final_anomaly_summary = (
    anomaly_summary
    if include_anomaly_summary
    else "Anomaly summary excluded by the report configuration."
)

report_filename = st.text_input(
    "PDF filename",
    value="Executive_Report.pdf"
).strip()

if not report_filename:
    report_filename = "Executive_Report.pdf"

if not report_filename.lower().endswith(".pdf"):
    report_filename += ".pdf"

st.caption(
    "The existing PDF builder determines the report's layout and "
    "content. Additional fields above are shown in the interface, "
    "but are passed to the builder only if its existing interface "
    "supports them."
)

st.markdown("---")


# ------------------------------------------------
# GENERATE PDF REPORT
# ------------------------------------------------

st.subheader("📄 Generate Executive PDF")

st.write(
    "Generate a downloadable PDF using your existing "
    "ExecutiveReportBuilder."
)

if st.button(
    "📄 Generate Executive Report",
    type="primary",
    use_container_width=True
):

    try:

        builder = ExecutiveReportBuilder()

        with st.spinner("Generating executive report..."):

            filename = builder.generate(
                filename=report_filename,
                dataset_summary=dataset_summary,
                health_score=health,
                automl_result=automl_result,
                recommendations=final_recommendations,
                anomaly_summary=final_anomaly_summary
            )

        if not filename:
            st.error(
                "The report builder did not return a file path."
            )

        elif not os.path.isfile(filename):
            st.error(
                "The report builder returned a path, but the file "
                "could not be found."
            )

        else:

            with open(filename, "rb") as report_file:
                pdf_bytes = report_file.read()

            st.session_state["executive_report_pdf"] = pdf_bytes
            st.session_state["executive_report_filename"] = (
                os.path.basename(filename)
            )

            st.success(
                "Executive report generated successfully."
            )

    except Exception as error:

        st.error(
            f"Report generation failed: {error}"
        )

if "executive_report_pdf" in st.session_state:

    st.download_button(
        "⬇️ Download Executive Report PDF",
        data=st.session_state["executive_report_pdf"],
        file_name=st.session_state.get(
            "executive_report_filename",
            "Executive_Report.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )


# ------------------------------------------------
# AI INSIGHT
# ------------------------------------------------

st.markdown("---")

ai_insight(
    "An executive report helps stakeholders review dataset quality, "
    "potential risks, and recommended next steps. Model performance "
    "and anomaly findings should be reported only when supported by "
    "actual analysis results."
)


# ------------------------------------------------
# PAGE NAVIGATION
# ------------------------------------------------

st.markdown("---")

st.subheader("🧭 Continue Exploring NexDecision AI")

prev_col, home_col, next_col = st.columns(3)

with prev_col:
    if st.button(
        "⬅️ AI Anomaly Detection",
        use_container_width=True
    ):
        st.switch_page("pages/17_AI_Anomaly_Detection.py")

with home_col:
    if st.button(
        "🏠 Home",
        use_container_width=True
    ):
        st.switch_page("pages/0_Home.py")



# ------------------------------------------------
# FOOTER
# ------------------------------------------------

page_footer()
