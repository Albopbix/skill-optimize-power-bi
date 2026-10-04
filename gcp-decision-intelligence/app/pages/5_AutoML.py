import time

import streamlit as st
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from src.ui.layout import page_header, ai_insight, page_footer
from src.ui.status import loading, success

from src.automl.automl_engine import AutoMLEngine
from src.database.database import Database
from src.model_recommendation.model_recommender import ModelRecommender
from src.model_export.model_exporter import ModelExporter


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI AutoML Engine",
    page_icon="🤖",
    layout="wide"
)


# ==========================================================
# PERFORMANCE SETTINGS
# ==========================================================

MAX_TRAINING_ROWS = 15000


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    .automl-hero {
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.12),
            rgba(14, 116, 144, 0.10)
        );
        border: 1px solid rgba(100, 116, 139, 0.18);
        margin-bottom: 1.2rem;
    }

    .automl-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .automl-subtitle {
        color: #64748b;
        font-size: 1rem;
    }

    .config-card {
        padding: 1rem 1.2rem;
        border-radius: 15px;
        background: #eef6ff;
        border: 1px solid rgba(59, 130, 246, 0.18);
        min-height: 105px;
    }

    .config-title {
        font-weight: 750;
        font-size: 0.9rem;
    }

    .config-value {
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }

    .decision-card {
        padding: 1.3rem;
        border-radius: 16px;
        background: #172554;
        color: white;
        border: 1px solid #1e3a5f;
    }

    .decision-title {
        font-size: 1rem;
        font-weight: 800;
    }

    .decision-value {
        font-size: 1.45rem;
        font-weight: 850;
        margin-top: 0.35rem;
    }

    .performance-note {
        padding: 0.85rem 1rem;
        border-radius: 12px;
        background: rgba(14, 116, 144, 0.08);
        border: 1px solid rgba(14, 116, 144, 0.15);
        color: #475569;
        font-size: 0.9rem;
    }

    .section-label {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    "🤖 AI AutoML Engine",
    "Automatically train, compare and recommend the best Machine Learning model."
)

st.markdown(
    """
    <div class="automl-hero">
        <div class="automl-title">
            🧠 Automated Machine Learning Decision Center
        </div>
        <div class="automl-subtitle">
            Prepare your dataset, identify the prediction target,
            compare machine learning algorithms and export the
            strongest performing model.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# DATASET CHECK
# ==========================================================

if "dataset" not in st.session_state:

    st.warning(
        "⚠️ Please upload a dataset first."
    )

    st.stop()


df = st.session_state["dataset"]

filename = st.session_state.get(
    "filename",
    "Uploaded Dataset"
)


if df is None or df.empty:

    st.error(
        "The uploaded dataset is empty."
    )

    st.stop()


st.success(
    f"✅ Dataset loaded: **{filename}**"
)


# ==========================================================
# DATASET INFORMATION
# ==========================================================

rows = len(df)
columns = len(df.columns)

missing = int(
    df.isnull().sum().sum()
)

duplicates = int(
    df.duplicated().sum()
)

numeric_count = len(
    df.select_dtypes(include="number").columns
)

categorical_count = len(
    df.select_dtypes(exclude="number").columns
)


# ==========================================================
# DATASET STATUS
# ==========================================================

st.markdown(
    '<div class="section-label">📊 Dataset Readiness</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Rows",
        f"{rows:,}"
    )

with c2:
    st.metric(
        "Columns",
        columns
    )

with c3:
    st.metric(
        "Missing",
        f"{missing:,}"
    )

with c4:
    st.metric(
        "Numeric",
        numeric_count
    )

with c5:
    st.metric(
        "Categorical",
        categorical_count
    )


st.divider()


# ==========================================================
# TARGET DETECTION
# ==========================================================

ignore_columns = [
    "order_id",
    "customer_id",
    "product_id",
    "seller_id",
    "row id",
    "row_id",
    "id"
]


candidate_columns = [
    c
    for c in df.columns
    if str(c).lower().strip()
    not in ignore_columns
]


if len(candidate_columns) == 0:

    st.error(
        "No suitable target column was detected."
    )

    st.stop()


# ==========================================================
# TARGET SELECTION
# ==========================================================

st.markdown(
    '<div class="section-label">🎯 Prediction Configuration</div>',
    unsafe_allow_html=True
)

target = st.selectbox(
    "Prediction Target",
    candidate_columns,
    help="Select the column that the AutoML engine should predict."
)


# ==========================================================
# TARGET PROFILE
# ==========================================================

target_series = df[target]

target_unique = target_series.nunique(
    dropna=True
)

target_missing = int(
    target_series.isnull().sum()
)

target_type = str(
    target_series.dtype
)


if pd.api.types.is_numeric_dtype(
    target_series
):

    if target_unique <= 10:

        suggested_problem = "Classification"

    else:

        suggested_problem = "Regression"

else:

    suggested_problem = "Classification"


p1, p2, p3, p4 = st.columns(4)

with p1:

    st.metric(
        "Target",
        target
    )

with p2:

    st.metric(
        "Unique Values",
        f"{target_unique:,}"
    )

with p3:

    st.metric(
        "Missing Target",
        f"{target_missing:,}"
    )

with p4:

    st.metric(
        "Suggested Type",
        suggested_problem
    )


# ==========================================================
# LARGE DATASET NOTICE
# ==========================================================

if rows > MAX_TRAINING_ROWS:

    st.info(
        f"""
        ⚡ **Large dataset detected**

        The uploaded dataset contains **{rows:,} rows**.

        AutoML will use a maximum of
        **{MAX_TRAINING_ROWS:,} rows** for training
        to keep model comparison responsive.

        Your original dataset will not be modified.
        """
    )


# ==========================================================
# TRAINING PREPROCESSOR
# ==========================================================

@st.cache_data(
    show_spinner=False
)
def prepare_training_data(
    dataframe,
    target_column,
    max_rows
):

    data = dataframe.copy()

    # ------------------------------------------------------
    # Remove missing rows
    # ------------------------------------------------------

    data = (
        data
        .dropna()
        .reset_index(drop=True)
    )

    # ------------------------------------------------------
    # Large dataset sampling
    # ------------------------------------------------------

    sampled = False

    if len(data) > max_rows:

        data = data.sample(
            max_rows,
            random_state=42
        ).reset_index(
            drop=True
        )

        sampled = True

    # ------------------------------------------------------
    # Remove constant columns
    # ------------------------------------------------------

    constant_columns = [
        c
        for c in data.columns
        if data[c].nunique() <= 1
    ]

    data = data.drop(
        columns=constant_columns,
        errors="ignore"
    )

    if target_column not in data.columns:

        raise ValueError(
            "Target column was removed during preprocessing."
        )

    # ------------------------------------------------------
    # Encode features
    # ------------------------------------------------------

    feature_encoders = {}

    for col in data.columns:

        if col == target_column:
            continue

        # ----------------------------------------------
        # Date conversion
        # ----------------------------------------------

        if (
            pd.api.types.is_datetime64_any_dtype(
                data[col]
            )
        ):

            data[col] = (
                data[col]
                .astype("int64")
                // 10**9
            )

            continue

        # ----------------------------------------------
        # Try date detection
        # ----------------------------------------------

        if not pd.api.types.is_numeric_dtype(
            data[col]
        ):

            converted = pd.to_datetime(
                data[col],
                errors="coerce"
            )

            if (
                converted.notna().mean()
                >= 0.8
            ):

                data[col] = (
                    converted
                    .astype("int64")
                    // 10**9
                )

                continue

        # ----------------------------------------------
        # Categorical encoding
        # ----------------------------------------------

        if not pd.api.types.is_numeric_dtype(
            data[col]
        ):

            encoder = LabelEncoder()

            data[col] = encoder.fit_transform(
                data[col].astype(str)
            )

            feature_encoders[col] = encoder

    # ------------------------------------------------------
    # Target encoding
    # ------------------------------------------------------

    target_encoder = None

    if not pd.api.types.is_numeric_dtype(
        data[target_column]
    ):

        target_encoder = LabelEncoder()

        data[target_column] = (
            target_encoder
            .fit_transform(
                data[target_column]
                .astype(str)
            )
        )

    # ------------------------------------------------------
    # Split
    # ------------------------------------------------------

    X = data.drop(
        columns=[target_column]
    )

    y = data[target_column]

    if X.shape[1] == 0:

        raise ValueError(
            "No usable feature columns remain after preprocessing."
        )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42
        )
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        feature_encoders,
        target_encoder,
        sampled,
        constant_columns
    )


# ==========================================================
# TRAINING SESSION STATE
# ==========================================================

if "automl_result" not in st.session_state:

    st.session_state["automl_result"] = None


# ==========================================================
# TRAIN BUTTON
# ==========================================================

st.markdown(
    '<div class="section-label">🚀 Model Training</div>',
    unsafe_allow_html=True
)

train_button = st.button(
    "🚀 Train & Compare AI Models",
    type="primary",
    width="stretch"
)


# ==========================================================
# TRAINING
# ==========================================================

if train_button:

    start_time = time.perf_counter()

    try:

        with st.spinner(
            "⚙️ Preparing training data..."
        ):

            (
                X_train,
                X_test,
                y_train,
                y_test,
                feature_encoders,
                target_encoder,
                sampled,
                constant_columns
            ) = prepare_training_data(
                df,
                target,
                MAX_TRAINING_ROWS
            )


        status = st.empty()

        progress = st.progress(
            10
        )

        status.info(
            "🔄 Preparing AI training pipeline..."
        )


        # --------------------------------------------------
        # AUTOML
        # --------------------------------------------------

        automl = AutoMLEngine()

        progress.progress(
            25
        )

        status.info(
            "🤖 Comparing machine learning algorithms..."
        )


        with loading(
            "Training and evaluating models..."
        ):

            results = automl.compare_models(
                X_train,
                X_test,
                y_train,
                y_test
            )


        progress.progress(
            75
        )

        status.info(
            "📊 Evaluating model performance..."
        )


        if not results:

            raise ValueError(
                "AutoML did not return any model results."
            )


        best_model = max(
            results,
            key=results.get
        )

        progress.progress(
            90
        )

        status.info(
            "🏆 Selecting best-performing model..."
        )


        # --------------------------------------------------
        # EXPORT
        # --------------------------------------------------

        exporter = ModelExporter()

        filepath = exporter.export(
            model=automl.best_model,
            model_name=best_model.replace(
                " ",
                "_"
            ),
            feature_names=list(
                X_train.columns
            ),
            target_column=target,
            problem_type=automl.problem_type
        )


        # --------------------------------------------------
        # SAVE DATABASE HISTORY
        # --------------------------------------------------

        database = Database()

        database.save_model(
            filename,
            best_model,
            results[best_model],
            automl.problem_type
        )


        # --------------------------------------------------
        # TRAINING TIME
        # --------------------------------------------------

        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        # --------------------------------------------------
        # FEATURE IMPORTANCE
        # --------------------------------------------------

        importance = None

        try:

            importance = automl.feature_importance(
                X_train.columns
            )

        except Exception:

            importance = None


        # --------------------------------------------------
        # RECOMMENDATIONS
        # --------------------------------------------------

        recommender = ModelRecommender()

        recommendations = recommender.recommend(
            best_model,
            results[best_model],
            automl.problem_type
        )


        # --------------------------------------------------
        # STORE RESULT
        # --------------------------------------------------

        st.session_state[
            "automl_result"
        ] = {

            "results": results,

            "best_model": best_model,

            "problem_type":
                automl.problem_type,

            "feature_names":
                list(X_train.columns),

            "importance":
                importance,

            "recommendations":
                recommendations,

            "training_time":
                elapsed_time,

            "training_rows":
                len(X_train) + len(X_test),

            "sampled":
                sampled,

            "constant_columns":
                constant_columns,

            "target":
                target,

            "filepath":
                filepath,

            "score":
                results[best_model]
        }


        progress.progress(
            100
        )

        status.success(
            "✅ AutoML completed successfully!"
        )

        st.toast(
            "🎉 Model training completed!"
        )


    except Exception as e:

        st.error(
            f"❌ AutoML training failed: {e}"
        )


# ==========================================================
# SHOW TRAINING RESULT
# ==========================================================

result = st.session_state.get(
    "automl_result"
)


if result is None:

    st.info(
        "👆 Select a prediction target and click "
        "**Train & Compare AI Models** to start AutoML."
    )

    st.markdown(
        """
        <div class="performance-note">
            ⚡ <b>Performance optimization:</b>
            preprocessing is cached and models are trained
            only after you explicitly click the training button.
            Streamlit UI reruns will not automatically retrain
            your models.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    results = result["results"]

    best_model = result["best_model"]

    problem_type = result["problem_type"]

    importance = result["importance"]

    recommendations = result["recommendations"]

    training_time = result["training_time"]

    training_rows = result["training_rows"]

    sampled = result["sampled"]

    constant_columns = result[
        "constant_columns"
    ]

    target_used = result["target"]

    filepath = result["filepath"]

    best_score = result["score"]


    # ======================================================
    # SUCCESS
    # ======================================================

    st.success(
        f"🏆 Best model selected: **{best_model}**"
    )


    # ======================================================
    # DECISION SUMMARY
    # ======================================================

    st.markdown(
        '<div class="section-label">🏆 AI Model Decision</div>',
        unsafe_allow_html=True
    )

    d1, d2, d3, d4 = st.columns(4)

    with d1:

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    🥇 Best Model
                </div>
                <div class="decision-value">
                    {best_model}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d2:

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    🎯 Problem Type
                </div>
                <div class="decision-value">
                    {problem_type.title()}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d3:

        score_display = (
            f"{best_score:.2f}"
        )

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    📈 Model Score
                </div>
                <div class="decision-value">
                    {score_display}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d4:

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-title">
                    ⏱ Training Time
                </div>
                <div class="decision-value">
                    {training_time:.1f}s
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ======================================================
    # TRAINING DETAILS
    # ======================================================

    st.markdown(
        '<div class="section-label">⚙️ Training Configuration</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3, t4 = st.columns(4)

    with t1:

        st.metric(
            "Target",
            target_used
        )

    with t2:

        st.metric(
            "Training Rows",
            f"{training_rows:,}"
        )

    with t3:

        st.metric(
            "Models Compared",
            len(results)
        )

    with t4:

        st.metric(
            "Features Used",
            len(result["feature_names"])
        )


    if sampled:

        st.info(
            f"⚡ Training used a maximum of "
            f"{MAX_TRAINING_ROWS:,} sampled rows "
            f"because the original dataset was larger."
        )


    if constant_columns:

        with st.expander(
            "🔍 Preprocessing Details"
        ):

            st.write(
                "Constant columns removed:"
            )

            st.write(
                constant_columns
            )


    # ======================================================
    # MODEL COMPARISON
    # ======================================================

    st.markdown(
        '<div class="section-label">📊 Model Comparison</div>',
        unsafe_allow_html=True
    )

    results_df = pd.DataFrame(
        {
            "Model": list(
                results.keys()
            ),

            "Score": list(
                results.values()
            )
        }
    )


    results_df = results_df.sort_values(
        "Score",
        ascending=False
    ).reset_index(
        drop=True
    )


    results_df.insert(
        0,
        "Rank",
        range(
            1,
            len(results_df) + 1
        )
    )


    st.dataframe(
        results_df,
        width="stretch",
        hide_index=True
    )


    # ======================================================
    # MODEL COMPARISON CHART
    # ======================================================

    st.bar_chart(
        results_df.set_index(
            "Model"
        )["Score"]
    )


    # ======================================================
    # MODEL PERFORMANCE
    # ======================================================

    if problem_type == "classification":

        st.caption(
            "Classification score is displayed using the "
            "metric returned by the AutoML engine."
        )

    else:

        st.caption(
            "Regression score is displayed using the "
            "metric returned by the AutoML engine."
        )


    st.divider()


    # ======================================================
    # FEATURE IMPORTANCE
    # ======================================================

    st.markdown(
        '<div class="section-label">📌 Feature Importance</div>',
        unsafe_allow_html=True
    )


    if importance is not None:

        imp_df = pd.DataFrame(
            {
                "Feature":
                    list(
                        importance.keys()
                    ),

                "Importance":
                    list(
                        importance.values()
                    )
            }
        )


        imp_df = imp_df.sort_values(
            "Importance",
            ascending=False
        )


        top_features = imp_df.head(
            15
        )


        st.dataframe(
            top_features,
            width="stretch",
            hide_index=True
        )


        st.bar_chart(
            top_features.set_index(
                "Feature"
            )["Importance"]
        )


    else:

        st.info(
            "Feature importance is not available "
            "for the selected model."
        )


    # ======================================================
    # AI RECOMMENDATIONS
    # ======================================================

    st.markdown(
        '<div class="section-label">🤖 AI Model Recommendations</div>',
        unsafe_allow_html=True
    )


    if recommendations:

        for recommendation in recommendations:

            st.success(
                str(
                    recommendation
                )
            )

    else:

        st.info(
            "No additional recommendations were generated."
        )


    # ======================================================
    # EXPORT STATUS
    # ======================================================

    st.markdown(
        '<div class="section-label">💾 Model Export</div>',
        unsafe_allow_html=True
    )


    st.success(
        "✅ Best model exported successfully."
    )
    st.balloons()


    st.caption(
        f"Saved model path: {filepath}"
    )


    # ======================================================
    # AI INSIGHT
    # ======================================================

    ai_insight(
        "The AutoML engine compared multiple machine learning "
        "algorithms and selected the highest-performing model. "
        "Before deployment, review model performance, feature "
        "importance and business relevance."
    )


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()

nav_left, nav_right = st.columns(2)


with nav_left:

    if st.button(
        "← Previous: ",
        width="stretch"
    ):

        st.switch_page(
            "pages/3_AI_Business_Copilot.py"
        )


with nav_right:

    if st.button(
        "Next: →",
        width="stretch"
    ):

        st.switch_page(
            "pages/6_Business_Forecasting.py"
        )


# ==========================================================
# FOOTER
# ==========================================================

page_footer()