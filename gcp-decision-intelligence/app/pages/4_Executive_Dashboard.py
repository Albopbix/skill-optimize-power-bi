import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer
from src.ui.cards import kpi_card

from src.dashboard_ai.visualization_recommender import VisualizationRecommender
from src.database.database import Database


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# PERFORMANCE SETTINGS
# ==========================================================

MAX_CHART_ROWS = 5000
MAX_CORRELATION_COLUMNS = 20


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>
    .dashboard-hero {
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.12),
            rgba(14, 116, 144, 0.10)
        );
        border: 1px solid rgba(100, 116, 139, 0.18);
        margin-bottom: 1.2rem;
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
    }

    .status-card {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(100, 116, 139, 0.18);
        background: rgba(248, 250, 252, 0.65);
        margin-bottom: 0.7rem;
    }

    .status-title {
        font-weight: 700;
        font-size: 0.9rem;
    }

    .status-value {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    .action-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(100, 116, 139, 0.18);
        background: Black;
        min-height: 130px;
    }

    .action-title {
        font-size: 1rem;
        font-weight: 750;
        margin-bottom: 0.4rem;
    }

    .action-text {
        color: #cbd5e1;
        font-size: 0.9rem;
    }

    .performance-note {
        padding: 0.8rem 1rem;
        border-radius: 12px;
        background: rgba(14, 116, 144, 0.08);
        border: 1px solid rgba(14, 116, 144, 0.15);
        color: #475569;
        font-size: 0.88rem;
    }

    .section-label {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    "📊 Executive Dashboard",
    "Executive Business KPIs, AI Insights & Decision Intelligence"
)

st.markdown(
    """
    <div class="dashboard-hero">
        <div class="dashboard-title">🚀 Executive Decision Center</div>
        <div class="dashboard-subtitle">
            A performance-optimized business intelligence layer for
            monitoring data health, AI activity, business patterns,
            and executive actions.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# DATASET CHECK
# ==========================================================

if "dataset" not in st.session_state:
    st.warning("📂 Please upload a dataset first.")
    st.info("Go to **Upload Dataset** and upload your business dataset.")
    st.stop()


df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Uploaded Dataset"
)


if df is None or df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()


# ==========================================================
# DATA PREPARATION
# ==========================================================

rows = len(df)
columns = len(df.columns)

numeric_cols = df.select_dtypes(
    include="number"
).columns.tolist()

cat_cols = df.select_dtypes(
    exclude="number"
).columns.tolist()


# ==========================================================
# CACHED DATA QUALITY CALCULATIONS
# ==========================================================

@st.cache_data(show_spinner=False)
def calculate_quality_metrics(dataframe):

    missing = int(
        dataframe.isnull().sum().sum()
    )

    duplicates = int(
        dataframe.duplicated().sum()
    )

    return missing, duplicates


missing, duplicates = calculate_quality_metrics(df)


# ==========================================================
# BUSINESS HEALTH SCORE
# ==========================================================

def calculate_health_score(
    missing_count,
    duplicate_count,
    total_rows,
    total_columns
):

    if total_rows == 0:
        return 0

    missing_rate = (
        missing_count /
        max(total_rows * max(total_columns, 1), 1)
    )

    duplicate_rate = (
        duplicate_count /
        max(total_rows, 1)
    )

    score = 100

    score -= min(
        int(missing_rate * 100),
        30
    )

    score -= min(
        int(duplicate_rate * 100),
        20
    )

    if total_columns < 3:
        score -= 10

    if total_rows < 100:
        score -= 10

    return max(
        min(score, 100),
        0
    )


score = calculate_health_score(
    missing,
    duplicates,
    rows,
    columns
)


if score >= 90:
    grade = "🟢 Excellent"
elif score >= 75:
    grade = "🟡 Good"
elif score >= 60:
    grade = "🟠 Average"
else:
    grade = "🔴 Needs Attention"


# ==========================================================
# DATABASE
# ==========================================================

@st.cache_resource
def get_database():
    return Database()


database = get_database()


@st.cache_data(show_spinner=False)
def load_database_activity():

    models_data = database.get_models()
    predictions_data = database.get_predictions()

    return models_data, predictions_data


try:

    models, predictions = load_database_activity()

except Exception:

    models = []
    predictions = []


# ==========================================================
# AI VISUALIZATION RECOMMENDER
# ==========================================================

@st.cache_data(show_spinner=False)
def get_visualization_recommendations(dataframe):

    recommender = VisualizationRecommender(
        dataframe
    )

    return recommender.recommend()


try:

    recommendations = get_visualization_recommendations(df)

except Exception:

    recommendations = []


# ==========================================================
# EXECUTIVE STATUS
# ==========================================================

st.markdown(
    '<div class="section-label">📌 Executive Status</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card(
        "Business Health",
        f"{score}/100"
    )

with c2:
    kpi_card(
        "Records",
        f"{rows:,}"
    )

with c3:
    kpi_card(
        "Features",
        columns
    )

with c4:
    kpi_card(
        "AI Models",
        len(models)
    )

with c5:
    kpi_card(
        "Predictions",
        len(predictions)
    )


st.divider()


# ==========================================================
# HEALTH CENTER
# ==========================================================

st.markdown(
    '<div class="section-label">🏥 Business & Data Health</div>',
    unsafe_allow_html=True
)

health_left, health_right = st.columns(
    [2, 1]
)

with health_left:

    st.progress(
        score / 100
    )

    st.metric(
        "Overall Business Data Health",
        f"{score}/100"
    )

    st.caption(
        f"Dataset: {filename}"
    )


with health_right:

    st.metric(
        "Health Grade",
        grade
    )

    st.metric(
        "Missing Values",
        f"{missing:,}"
    )

    st.metric(
        "Duplicate Rows",
        f"{duplicates:,}"
    )


# ==========================================================
# AI DECISION STATUS
# ==========================================================

if score >= 90:

    decision_status = (
        "Dataset is in strong condition for "
        "analytics, modelling and forecasting."
    )

    decision_type = "🟢 Ready for AI"

elif score >= 75:

    decision_status = (
        "Dataset is usable, but some preprocessing "
        "should be completed before critical decisions."
    )

    decision_type = "🟡 Review Before AI"

else:

    decision_status = (
        "Data quality issues should be addressed "
        "before relying on predictive results."
    )

    decision_type = "🔴 Data Cleanup Required"


st.info(
    f"**{decision_type}** — {decision_status}"
)


# ==========================================================
# EXECUTIVE SNAPSHOT
# ==========================================================

st.markdown(
    '<div class="section-label">🎯 Executive Snapshot</div>',
    unsafe_allow_html=True
)

s1, s2, s3 = st.columns(3)

with s1:

    st.markdown(
        """
        <div class="action-card">
            <div class="action-title">📊 Data Foundation</div>
            <div class="action-text">
                Your dataset currently contains the core
                information available for business analytics,
                modelling and decision support.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with s2:

    model_status = (
        f"{len(models)} trained model(s)"
        if len(models) > 0
        else "No trained models yet"
    )

    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-title">🤖 AI Activity</div>
            <div class="action-text">
                {model_status}. Prediction activity:
                {len(predictions)} recorded prediction run(s).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with s3:

    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-title">🔎 Intelligence Coverage</div>
            <div class="action-text">
                {len(numeric_cols)} numeric features and
                {len(cat_cols)} categorical features detected.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ==========================================================
# AI ACTION CENTER
# ==========================================================

st.markdown(
    '<div class="section-label">🧠 AI Executive Action Center</div>',
    unsafe_allow_html=True
)

actions = []

if missing > 0:
    actions.append(
        (
            "⚠️ Resolve Missing Data",
            f"{missing:,} missing values detected.",
            "Data Quality"
        )
    )

if duplicates > 0:
    actions.append(
        (
            "🔁 Review Duplicate Records",
            f"{duplicates:,} duplicate rows detected.",
            "Data Quality"
        )
    )

if len(numeric_cols) >= 2:
    actions.append(
        (
            "📈 Explore Predictive Patterns",
            "Multiple numerical features are available for modelling.",
            "Machine Learning"
        )
    )

if len(cat_cols) > 0:
    actions.append(
        (
            "🎯 Analyze Business Segments",
            "Categorical dimensions can support segmentation analysis.",
            "Business Intelligence"
        )
    )

if len(models) == 0:
    actions.append(
        (
            "🤖 Train Your First Model",
            "No trained model is currently recorded.",
            "AI"
        )
    )

if len(predictions) == 0:
    actions.append(
        (
            "🔮 Generate Predictions",
            "No prediction run is currently recorded.",
            "Prediction"
        )
    )


if not actions:

    st.success(
        "✅ No immediate executive action has been detected."
    )

else:

    action_cols = st.columns(
        min(len(actions), 3)
    )

    for index, action in enumerate(actions[:3]):

        with action_cols[index]:

            title, description, category = action

            st.markdown(
                f"""
                <div class="action-card">
                    <div class="action-title">{title}</div>
                    <div class="action-text">
                        {description}
                    </div>
                    <br>
                    <small><b>Area:</b> {category}</small>
                </div>
                """,
                unsafe_allow_html=True
            )


st.divider()


# ==========================================================
# MODEL & PREDICTION ACTIVITY
# ==========================================================

st.markdown(
    '<div class="section-label">🤖 AI Activity</div>',
    unsafe_allow_html=True
)

activity_left, activity_right = st.columns(2)


with activity_left:

    st.subheader("Latest Model")

    if len(models) > 0:

        latest_model = models[0]

        try:

            model_name = latest_model[2]
            performance = latest_model[3]
            problem_type = latest_model[4]

        except Exception:

            model_name = "Recorded Model"
            performance = "-"
            problem_type = "-"

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "Model",
                model_name
            )

        with m2:
            try:
                st.metric(
                    "Performance",
                    f"{float(performance):.2f}"
                )
            except Exception:
                st.metric(
                    "Performance",
                    performance
                )

        with m3:
            st.metric(
                "Problem",
                problem_type
            )

    else:

        st.info(
            "No trained model has been recorded yet."
        )


with activity_right:

    st.subheader("Latest Prediction")

    if len(predictions) > 0:

        latest_prediction = predictions[0]

        try:

            prediction_model = latest_prediction[1]
            prediction_dataset = latest_prediction[2]
            prediction_rows = latest_prediction[3]

        except Exception:

            prediction_model = "Prediction"
            prediction_dataset = filename
            prediction_rows = "-"

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric(
                "Model",
                prediction_model
            )

        with p2:
            st.metric(
                "Rows",
                prediction_rows
            )

        with p3:
            st.metric(
                "Dataset",
                prediction_dataset
            )

    else:

        st.info(
            "No prediction activity has been recorded yet."
        )


st.divider()


# ==========================================================
# PERFORMANCE OPTIMIZATION
# ==========================================================

st.markdown(
    '<div class="section-label">⚡ Visualization Performance</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="performance-note">
        <b>Performance mode enabled.</b>
        KPI calculations use the complete dataset.
        Visualizations automatically use at most
        <b>{MAX_CHART_ROWS:,} rows</b> when the dataset is larger,
        reducing browser rendering and Plotly processing time.
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# CHART DATA PREPARATION
# ==========================================================

@st.cache_data(show_spinner=False)
def prepare_chart_data(dataframe, max_rows):

    if len(dataframe) <= max_rows:

        return dataframe.copy()

    return dataframe.sample(
        n=max_rows,
        random_state=42
    ).copy()


chart_df = prepare_chart_data(
    df,
    MAX_CHART_ROWS
)


# ==========================================================
# VISUALIZATION CENTER
# ==========================================================

st.markdown(
    '<div class="section-label">📊 Visualization Intelligence Center</div>',
    unsafe_allow_html=True
)

st.caption(
    "Charts are generated only when you select them. "
    "This prevents unnecessary Plotly rendering during every page load."
)


visualization_options = [
    "📈 Distribution Analysis",
    "🔥 Correlation Analysis",
    "🥧 Category Distribution",
    "📊 Category vs Numeric",
    "📦 Outlier Analysis",
    "📈 Trend Analysis",
    "🌍 Geographic Analysis"
]


selected_visualization = st.selectbox(
    "Select analysis",
    visualization_options,
    key="executive_visualization"
)


# ==========================================================
# DISTRIBUTION
# ==========================================================

if selected_visualization == "📈 Distribution Analysis":

    if len(numeric_cols) == 0:

        st.info(
            "No numeric columns are available for distribution analysis."
        )

    else:

        column = st.selectbox(
            "Numeric Column",
            numeric_cols,
            key="executive_histogram_column"
        )

        plot_df = chart_df[[column]].dropna()

        fig = px.histogram(
            plot_df,
            x=column,
            nbins=30,
            title=f"Distribution of {column}"
        )

        fig.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_histogram"
        )


# ==========================================================
# CORRELATION
# ==========================================================

elif selected_visualization == "🔥 Correlation Analysis":

    if len(numeric_cols) < 2:

        st.info(
            "At least two numeric columns are required."
        )

    else:

        correlation_columns = numeric_cols[
            :MAX_CORRELATION_COLUMNS
        ]

        corr = chart_df[
            correlation_columns
        ].corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Feature Correlation Matrix"
        )

        fig.update_layout(
            height=650,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_heatmap"
        )

        if len(numeric_cols) > MAX_CORRELATION_COLUMNS:

            st.caption(
                f"Showing the first {MAX_CORRELATION_COLUMNS} "
                f"numeric features for performance."
            )


# ==========================================================
# PIE
# ==========================================================

elif selected_visualization == "🥧 Category Distribution":

    if len(cat_cols) == 0:

        st.info(
            "No categorical columns are available."
        )

    else:

        category = st.selectbox(
            "Category",
            cat_cols,
            key="executive_pie_category"
        )

        counts = (
            chart_df[category]
            .value_counts()
            .head(10)
            .reset_index()
        )

        counts.columns = [
            category,
            "Count"
        ]

        fig = px.pie(
            counts,
            names=category,
            values="Count",
            hole=0.45,
            title=f"{category} Distribution"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_pie"
        )


# ==========================================================
# CATEGORY VS NUMERIC
# ==========================================================

elif selected_visualization == "📊 Category vs Numeric":

    if len(cat_cols) == 0 or len(numeric_cols) == 0:

        st.info(
            "At least one categorical and one numeric column are required."
        )

    else:

        c1, c2 = st.columns(2)

        with c1:

            category = st.selectbox(
                "Category",
                cat_cols,
                key="executive_bar_category"
            )

        with c2:

            numeric = st.selectbox(
                "Numeric",
                numeric_cols,
                key="executive_bar_numeric"
            )

        grouped = (
            chart_df
            .groupby(category, dropna=False)[numeric]
            .mean()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        fig = px.bar(
            grouped,
            x=category,
            y=numeric,
            title=f"Average {numeric} by {category}"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_bar"
        )


# ==========================================================
# OUTLIER
# ==========================================================

elif selected_visualization == "📦 Outlier Analysis":

    if len(cat_cols) == 0 or len(numeric_cols) == 0:

        st.info(
            "At least one categorical and one numeric column are required."
        )

    else:

        c1, c2 = st.columns(2)

        with c1:

            category = st.selectbox(
                "Category",
                cat_cols,
                key="executive_box_category"
            )

        with c2:

            numeric = st.selectbox(
                "Numeric",
                numeric_cols,
                key="executive_box_numeric"
            )

        plot_df = chart_df[
            [category, numeric]
        ].dropna()

        # Prevent extremely high-cardinality boxplots
        top_categories = (
            plot_df[category]
            .value_counts()
            .head(15)
            .index
        )

        plot_df = plot_df[
            plot_df[category].isin(
                top_categories
            )
        ]

        fig = px.box(
            plot_df,
            x=category,
            y=numeric,
            title=f"Outlier Analysis — {numeric}"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_boxplot"
        )


# ==========================================================
# TREND
# ==========================================================

elif selected_visualization == "📈 Trend Analysis":

    if len(numeric_cols) < 2:

        st.info(
            "At least two numeric columns are required."
        )

    else:

        c1, c2 = st.columns(2)

        with c1:

            x_column = st.selectbox(
                "X Axis",
                numeric_cols,
                key="executive_line_x"
            )

        with c2:

            y_column = st.selectbox(
                "Y Axis",
                numeric_cols,
                key="executive_line_y"
            )

        if x_column == y_column:

            st.warning(
                "Select two different numeric columns."
            )

        else:

            plot_df = chart_df[
                [x_column, y_column]
            ].dropna()

            plot_df = plot_df.sort_values(
                x_column
            )

            fig = px.line(
                plot_df,
                x=x_column,
                y=y_column,
                title=f"{y_column} vs {x_column}"
            )

            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=60, b=20)
            )

            st.plotly_chart(
                fig,
                width="stretch",
                key="executive_line"
            )


# ==========================================================
# GEOGRAPHIC
# ==========================================================

elif selected_visualization == "🌍 Geographic Analysis":

    location_columns = []

    for col in df.columns:

        name = str(col).lower()

        if any(
            keyword in name
            for keyword in [
                "city",
                "state",
                "country",
                "region",
                "location"
            ]
        ):

            location_columns.append(col)


    if len(location_columns) == 0:

        st.info(
            "No obvious geographic column was detected."
        )

    else:

        location = st.selectbox(
            "Location",
            location_columns,
            key="executive_geo_location"
        )

        geo = (
            chart_df[location]
            .value_counts()
            .head(15)
            .reset_index()
        )

        geo.columns = [
            location,
            "Count"
        ]

        fig = px.bar(
            geo,
            x=location,
            y="Count",
            title="Top Business Locations"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig,
            width="stretch",
            key="executive_geo"
        )


# ==========================================================
# AI VISUALIZATION RECOMMENDATIONS
# ==========================================================

st.divider()

st.markdown(
    '<div class="section-label">🤖 AI Visualization Recommendations</div>',
    unsafe_allow_html=True
)

if recommendations:

    if isinstance(
        recommendations,
        (list, tuple)
    ):

        for recommendation in recommendations[:5]:

            if isinstance(
                recommendation,
                dict
            ):

                title = recommendation.get(
                    "title",
                    "Recommended Analysis"
                )

                description = recommendation.get(
                    "description",
                    ""
                )

                st.info(
                    f"**{title}** — {description}"
                )

            else:

                st.info(
                    str(recommendation)
                )

    else:

        st.info(
            str(recommendations)
        )

else:

    st.caption(
        "No additional visualization recommendations were generated."
    )


# ==========================================================
# DATASET PREVIEW
# ==========================================================

st.divider()

with st.expander(
    "📋 View Dataset Preview"
):

    st.dataframe(
        df.head(20),
        width="stretch",
        height=350
    )


# ==========================================================
# EXECUTIVE RECOMMENDATION
# ==========================================================

st.markdown(
    '<div class="section-label">💼 Executive Action Center</div>',
    unsafe_allow_html=True
)

if score >= 90:

    st.success(
        "✅ Data quality is strong. The next focus can be "
        "predictive modelling, forecasting and KPI monitoring."
    )

elif score >= 75:

    st.info(
        "🟡 Data is usable, but quality improvements should "
        "be completed before high-impact AI decisions."
    )

else:

    st.error(
        "🔴 Data quality should be improved before relying "
        "on predictive or automated decisions."
    )


# ==========================================================
# AI INSIGHT
# ==========================================================

ai_insight(
    "Executives should monitor data health, business KPIs, "
    "AI model activity, prediction activity, business patterns "
    "and emerging risks before making high-impact decisions."
)


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()

nav_left, nav_right = st.columns(2)

with nav_left:

    if st.button(
        "← Previous: AI Business Copilot",
        width="stretch"
    ):

        st.switch_page(
            "pages/3_AI_Business_Copilot.py"
        )


with nav_right:

    if st.button(
        "Next: Interactive Dashboard →",
        width="stretch"
    ):

        st.switch_page(
            "pages/5_AutoML.py"
        )


# ==========================================================
# FOOTER
# ==========================================================

page_footer()