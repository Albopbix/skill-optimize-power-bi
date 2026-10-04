import os
import hashlib
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer
from src.model_prediction.predictor import Predictor
from src.model_prediction.prediction_export import PredictionExporter
from src.database.database import Database
from src.storage import model_store


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Prediction Studio | Nex Decision AI",
    page_icon="🔮",
    layout="wide",
)

RESULTS_KEY = "page7_prediction_results"
META_KEY = "page7_prediction_metadata"


# =========================================================
# HELPERS
# =========================================================
def file_fingerprint(uploaded_file):
    """Create a content-based signature so changed files invalidate old results."""
    content = uploaded_file.getvalue()
    return hashlib.sha256(content).hexdigest()


def safe_csv_bytes(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def prediction_is_numeric(series):
    converted = pd.to_numeric(series, errors="coerce")
    return pd.api.types.is_numeric_dtype(series) or converted.notna().all()


def format_number(value):
    try:
        return f"{float(value):,.4g}"
    except (TypeError, ValueError):
        return str(value)


def section_heading(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


# =========================================================
# HEADER
# =========================================================
page_header(
    "🔮 Prediction Studio",
    "Run saved machine-learning models, inspect input quality, understand "
    "prediction behaviour, and export reproducible results.",
)

# =========================================================
# MODEL DISCOVERY
# =========================================================
try:
    models = model_store.list_models()
except Exception as exc:
    st.error(
        "Could not list saved models. Check the model storage "
        "configuration (GCS_BUCKET / permissions)."
    )
    with st.expander("Technical details"):
        st.code(str(exc))
    page_footer()
    st.stop()

if not models:
    st.warning("No saved .pkl models were found.")
    st.info("Open AutoML, train a model, and save/export it first.")
    page_footer()
    st.stop()

# =========================================================
# CONFIGURATION
# =========================================================
section_heading("1. Configure a prediction run")

config_left, config_right = st.columns([1, 1])

with config_left:
    selected_model = st.selectbox(
        "Saved model",
        options=models,
        key="page7_selected_model",
    )

with config_right:
    uploaded_file = st.file_uploader(
        "Input dataset (CSV)",
        type=["csv"],
        help="The CSV should contain the feature columns used during training.",
        key="page7_uploaded_csv",
    )

if uploaded_file is None:
    st.info("Choose a saved model and upload a CSV to begin.")
    ai_insight(
        "For reliable predictions, use the same feature definitions and units "
        "that were used when the model was trained."
    )
    page_footer()
    st.stop()

# =========================================================
# LOAD CSV
# =========================================================
try:
    raw_bytes = uploaded_file.getvalue()
    df = pd.read_csv(BytesIO(raw_bytes))
except Exception as exc:
    st.error(f"Could not read this CSV file: {exc}")
    page_footer()
    st.stop()

if df.empty:
    st.warning("The uploaded CSV has no data rows.")
    page_footer()
    st.stop()

if len(df.columns) == 0:
    st.warning("The uploaded CSV has no columns.")
    page_footer()
    st.stop()

if df.columns.duplicated().any():
    duplicates = df.columns[df.columns.duplicated()].astype(str).tolist()
    st.error("Duplicate column names were found: " + ", ".join(duplicates))
    st.info("Rename duplicate columns in the CSV and upload it again.")
    page_footer()
    st.stop()

# Include content hash: same filename and size can still contain different data.
input_signature = (
    selected_model,
    uploaded_file.name,
    len(raw_bytes),
    file_fingerprint(uploaded_file),
)

previous_metadata = st.session_state.get(META_KEY)
if previous_metadata and previous_metadata.get("input_signature") != input_signature:
    st.session_state.pop(RESULTS_KEY, None)
    st.session_state.pop(META_KEY, None)

# =========================================================
# INPUT HEALTH
# =========================================================
section_heading("2. Input data health")

row_count, column_count = df.shape
missing_cells = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())
columns_with_missing = int(df.isna().any(axis=0).sum())
constant_columns = [
    str(col) for col in df.columns if df[col].nunique(dropna=False) <= 1
]
memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

h1, h2, h3, h4, h5 = st.columns(5)
h1.metric("Rows", f"{row_count:,}")
h2.metric("Columns", f"{column_count:,}")
h3.metric("Missing cells", f"{missing_cells:,}")
h4.metric("Duplicate rows", f"{duplicate_rows:,}")
h5.metric("Approx. memory", f"{memory_mb:.2f} MB")

with st.expander("Open detailed data-quality report"):
    missing_tab, types_tab, risk_tab = st.tabs(
        ["Missing values", "Column profile", "Potential risks"]
    )

    with missing_tab:
        missing_report = pd.DataFrame({
            "Column": df.columns.astype(str),
            "Missing count": df.isna().sum().values,
            "Missing %": (df.isna().mean().values * 100).round(2),
        })
        missing_report = missing_report[missing_report["Missing count"] > 0]
        if missing_report.empty:
            st.success("No missing values detected.")
        else:
            st.dataframe(missing_report, width="stretch", hide_index=True)

    with types_tab:
        profile = pd.DataFrame({
            "Column": df.columns.astype(str),
            "Data type": df.dtypes.astype(str).values,
            "Distinct values": [df[col].nunique(dropna=True) for col in df.columns],
            "Missing count": df.isna().sum().values,
        })
        st.dataframe(profile, width="stretch", hide_index=True)

    with risk_tab:
        if duplicate_rows:
            st.warning(f"{duplicate_rows:,} duplicate rows are present.")
        else:
            st.success("No duplicate rows detected.")
        if constant_columns:
            st.warning("Constant columns: " + ", ".join(constant_columns))
        else:
            st.success("No constant columns detected.")
        if missing_cells:
            st.warning(
                "Missing values are not automatically filled or removed. "
                "The model's preprocessing pipeline must be able to handle them."
            )

# =========================================================
# DATA PREVIEW
# =========================================================
with st.expander("Preview uploaded dataset", expanded=True):
    preview_count = st.slider(
        "Rows to preview",
        min_value=1,
        max_value=min(100, row_count),
        value=min(10, row_count),
        key="page7_preview_rows",
    )
    st.dataframe(df.head(preview_count), width="stretch", hide_index=True)

# =========================================================
# LOAD MODEL AND VALIDATE FEATURES
# =========================================================
section_heading("3. Model compatibility")

try:
    model_path = model_store.get_model_path(selected_model)
    predictor = Predictor(model_path)
except Exception as exc:
    st.error(
        "The selected model could not be loaded. The file may be corrupted "
        "or incompatible with the current project."
    )
    with st.expander("Technical details"):
        st.code(str(exc))
    page_footer()
    st.stop()

missing_features, extra_features = predictor.validate_features(df)
feature_left, feature_right = st.columns(2)

with feature_left:
    if missing_features:
        st.error(f"Missing required features ({len(missing_features)})")
        st.write(missing_features)
    else:
        st.success("All required model features are present.")

with feature_right:
    if extra_features:
        st.info(f"{len(extra_features)} extra column(s) will be ignored.")
        st.write(extra_features)
    else:
        st.success("No extra columns to ignore.")

with st.expander("Required model features"):
    st.write(list(predictor.feature_names))
    st.caption(
        "Feature names must match the trained model. The input is reordered "
        "to match the model's training feature order."
    )

# =========================================================
# RUN PREDICTIONS
# =========================================================
section_heading("4. Generate predictions")

if missing_cells:
    st.warning(
        "This dataset contains missing values. Prediction may fail if the "
        "saved model pipeline does not handle them."
    )

if st.button(
    "🚀 Generate predictions",
    type="primary",
    width="stretch",
    disabled=bool(missing_features),
    key="page7_predict_button",
):
    try:
        prediction_input = df[predictor.feature_names].copy()

        with st.spinner("Running model predictions..."):
            predictions = predictor.predict(prediction_input)

        if len(predictions) != len(df):
            raise ValueError(
                "The number of predictions does not match the number of input rows."
            )

        result = prediction_input.copy()
        result["Prediction"] = predictions

        # If available, attach class probabilities/confidence for classifiers.
        # This is optional; some estimators do not support predict_proba.
        probability_note = None
        try:
            model_object = getattr(predictor, "model", None)
            if model_object is not None and hasattr(model_object, "predict_proba"):
                probabilities = model_object.predict_proba(prediction_input)
                classes = getattr(model_object, "classes_", None)
                if probabilities is not None and len(probabilities) == len(result):
                    max_probability = probabilities.max(axis=1)
                    result["Prediction Confidence (%)"] = (
                        max_probability * 100
                    ).round(2)
                    if classes is not None and probabilities.shape[1] <= 20:
                        for index, class_name in enumerate(classes):
                            result[f"Probability - {class_name} (%)"] = (
                                probabilities[:, index] * 100
                            ).round(2)
                    probability_note = (
                        "Probability columns were added using the model's "
                        "predict_proba method. They are model scores, not guarantees."
                    )
        except Exception as probability_exc:
            probability_note = (
                "Prediction succeeded, but optional probability scores were "
                f"unavailable: {probability_exc}"
            )

        metadata = {
            "input_signature": input_signature,
            "model": selected_model,
            "dataset": uploaded_file.name,
            "rows": len(result),
            "columns": len(prediction_input.columns),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "problem_type": getattr(predictor, "problem_type", "Unknown"),
            "probability_note": probability_note,
        }
        st.session_state[RESULTS_KEY] = result
        st.session_state[META_KEY] = metadata
        st.success("Prediction run completed.")
        st.rerun()

    except Exception as exc:
        st.error("Prediction could not be completed.")
        with st.expander("Technical error details"):
            st.code(str(exc))

# =========================================================
# RESULTS
# =========================================================
stored_result = st.session_state.get(RESULTS_KEY)
metadata = st.session_state.get(META_KEY)

if stored_result is not None and metadata is not None:
    if metadata.get("input_signature") != input_signature:
        st.info("The previous result belongs to a different input. Generate a new run.")
    else:
        result = stored_result.copy()
        prediction_series = result["Prediction"]
        numeric_predictions = pd.to_numeric(prediction_series, errors="coerce")
        is_numeric = prediction_is_numeric(prediction_series)

        st.divider()
        section_heading("5. Prediction overview")

        if is_numeric:
            valid_values = numeric_predictions.dropna()
            a, b, c, d = st.columns(4)
            a.metric("Predicted records", f"{len(result):,}")
            b.metric("Mean prediction", format_number(valid_values.mean()) if not valid_values.empty else "N/A")
            c.metric("Minimum", format_number(valid_values.min()) if not valid_values.empty else "N/A")
            d.metric("Maximum", format_number(valid_values.max()) if not valid_values.empty else "N/A")

            if not valid_values.empty:
                spread = valid_values.max() - valid_values.min()
                st.caption(
                    f"Range: {format_number(spread)} · "
                    f"Standard deviation: {format_number(valid_values.std())}"
                )
        else:
            class_counts = prediction_series.astype(str).value_counts()
            a, b, c = st.columns(3)
            a.metric("Predicted records", f"{len(result):,}")
            b.metric("Distinct predicted classes", f"{len(class_counts):,}")
            c.metric(
                "Most frequent class",
                str(class_counts.index[0])[:40] if not class_counts.empty else "N/A",
            )
            st.dataframe(
                class_counts.rename_axis("Predicted class")
                .reset_index(name="Records"),
                width="stretch",
                hide_index=True,
            )

        if metadata.get("probability_note"):
            st.caption(metadata["probability_note"])

        # Optional actual-vs-predicted evaluation, if user supplies actual target values.
        with st.expander("Optional: compare predictions with actual values"):
            actual_col = st.selectbox(
                "Choose a column containing the true target values",
                options=["(Not provided)"] + list(df.columns),
                key="page7_actual_target_col",
            )
            if actual_col != "(Not provided)":
                actual = df[actual_col].reset_index(drop=True)
                predicted = result["Prediction"].reset_index(drop=True)
                compare = pd.DataFrame({"Actual": actual, "Predicted": predicted})
                if prediction_is_numeric(actual) and prediction_is_numeric(predicted):
                    compare["Actual"] = pd.to_numeric(compare["Actual"], errors="coerce")
                    compare["Predicted"] = pd.to_numeric(compare["Predicted"], errors="coerce")
                    compare = compare.dropna()
                    if not compare.empty:
                        mae = (compare["Actual"] - compare["Predicted"]).abs().mean()
                        rmse = (((compare["Actual"] - compare["Predicted"]) ** 2).mean()) ** 0.5
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Rows compared", f"{len(compare):,}")
                        m2.metric("MAE", format_number(mae))
                        m3.metric("RMSE", format_number(rmse))
                        st.caption("These metrics are meaningful only if the selected column is the true target for these same rows.")
                else:
                    compare["Correct?"] = compare["Actual"].astype(str) == compare["Predicted"].astype(str)
                    m1, m2 = st.columns(2)
                    m1.metric("Rows compared", f"{len(compare):,}")
                    m2.metric("Accuracy on supplied rows", f"{compare['Correct?'].mean() * 100:.2f}%")
                st.dataframe(compare, width="stretch", hide_index=True)

        # Search/filter/sort tools
        st.divider()
        section_heading("6. Explore results")

        search_col, filter_col, sort_col = st.columns([1.2, 1, 1])
        with search_col:
            search_text = st.text_input(
                "Search result values",
                placeholder="Search across columns...",
                key="page7_result_search",
            )
        with filter_col:
            prediction_options = sorted(prediction_series.astype(str).unique().tolist())
            selected_predictions = st.multiselect(
                "Filter prediction values",
                options=prediction_options,
                default=prediction_options,
                key="page7_prediction_filter",
            )
        with sort_col:
            sort_column = st.selectbox(
                "Sort results by",
                options=list(result.columns),
                key="page7_sort_column",
            )

        sort_ascending = st.checkbox(
            "Sort ascending",
            value=True,
            key="page7_sort_ascending",
        )

        filtered_result = result[
            result["Prediction"].astype(str).isin(selected_predictions)
        ].copy()

        if search_text.strip():
            search_mask = filtered_result.astype(str).apply(
                lambda col: col.str.contains(
                    search_text.strip(), case=False, regex=False, na=False
                )
            ).any(axis=1)
            filtered_result = filtered_result[search_mask]

        try:
            filtered_result = filtered_result.sort_values(
                by=sort_column, ascending=sort_ascending, kind="stable"
            )
        except (TypeError, ValueError):
            st.info("Some values in this column cannot be sorted together.")

        st.caption(f"Showing {len(filtered_result):,} of {len(result):,} records.")
        st.dataframe(filtered_result, width="stretch", hide_index=True)

        # Charts
        st.divider()
        section_heading("7. Prediction visualizations")
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(
            ["Distribution", "Counts", "Feature relationship"]
        )

        if filtered_result.empty:
            st.info("No results match the current search and filters.")
        else:
            with chart_tab1:
                try:
                    if is_numeric:
                        plot_values = pd.to_numeric(
                            filtered_result["Prediction"], errors="coerce"
                        ).dropna()
                        if not plot_values.empty:
                            fig = px.histogram(
                                x=plot_values,
                                nbins=30,
                                title="Distribution of predicted values",
                                labels={"x": "Prediction", "y": "Records"},
                            )
                            st.plotly_chart(fig, width="stretch")
                        else:
                            st.info("No numeric predictions are available to plot.")
                    else:
                        counts = filtered_result["Prediction"].astype(str).value_counts().rename_axis("Class").reset_index(name="Records")
                        fig = px.pie(
                            counts, names="Class", values="Records",
                            title="Predicted class share", hole=0.35
                        )
                        st.plotly_chart(fig, width="stretch")
                except Exception as exc:
                    st.info(f"Could not create the distribution chart: {exc}")

            with chart_tab2:
                try:
                    if is_numeric:
                        counts = pd.to_numeric(
                            filtered_result["Prediction"], errors="coerce"
                        ).dropna().value_counts().sort_index().rename_axis("Prediction").reset_index(name="Records")
                    else:
                        counts = filtered_result["Prediction"].astype(str).value_counts().rename_axis("Prediction").reset_index(name="Records")
                    fig = px.bar(
                        counts, x="Prediction", y="Records",
                        title="Prediction counts"
                    )
                    st.plotly_chart(fig, width="stretch")
                except Exception as exc:
                    st.info(f"Could not create the counts chart: {exc}")

            with chart_tab3:
                candidate_features = [
                    col for col in predictor.feature_names
                    if col in filtered_result.columns
                    and pd.api.types.is_numeric_dtype(filtered_result[col])
                ]
                if candidate_features and is_numeric:
                    x_feature = st.selectbox(
                        "Numeric feature for relationship chart",
                        options=candidate_features,
                        key="page7_relationship_feature",
                    )
                    relationship = filtered_result[[x_feature, "Prediction"]].copy()
                    relationship["Prediction"] = pd.to_numeric(
                        relationship["Prediction"], errors="coerce"
                    )
                    relationship = relationship.dropna()
                    if not relationship.empty:
                        fig = px.scatter(
                            relationship, x=x_feature, y="Prediction",
                            title=f"{x_feature} vs predicted value",
                            trendline=None,
                        )
                        st.plotly_chart(fig, width="stretch")
                    else:
                        st.info("No usable numeric values for this relationship.")
                else:
                    st.info(
                        "A feature relationship chart is available when the "
                        "result includes a numeric input feature and numeric predictions."
                    )

        # Export
        st.divider()
        section_heading("8. Export results")
        export_all, export_filtered = st.columns(2)
        with export_all:
            st.download_button(
                "Download all predictions",
                data=safe_csv_bytes(result),
                file_name="NexDecision_All_Predictions.csv",
                mime="text/csv",
                width="stretch",
                key="page7_download_all",
            )
        with export_filtered:
            st.download_button(
                "Download filtered results",
                data=safe_csv_bytes(filtered_result),
                file_name="NexDecision_Filtered_Predictions.csv",
                mime="text/csv",
                width="stretch",
                key="page7_download_filtered",
            )

        with st.expander("Advanced CSV exporter"):
            try:
                exporter = PredictionExporter()
                export_filename = exporter.export_csv(
                    result, filename="Predictions.csv"
                )
                with open(export_filename, "rb") as export_file:
                    st.download_button(
                        "Download via Prediction Exporter",
                        data=export_file.read(),
                        file_name="Predictions.csv",
                        mime="text/csv",
                        key="page7_exporter_download",
                    )
            except Exception as exc:
                st.caption(f"Optional exporter unavailable: {exc}")

        # History
        st.divider()
        section_heading("9. Prediction history")
        if st.button(
            "Save this run to prediction history",
            key="page7_save_history",
        ):
            try:
                database = Database()
                database.save_prediction(
                    metadata["model"], metadata["dataset"], metadata["rows"]
                )
                st.success("Prediction run saved to history.")
            except Exception as exc:
                st.warning(f"Could not save history; results remain available. Details: {exc}")

        try:
            history = Database().get_predictions()
            if history is not None:
                st.dataframe(
                    history if isinstance(history, pd.DataFrame) else pd.DataFrame(history),
                    width="stretch",
                    hide_index=True,
                )
        except Exception:
            st.caption("Saved prediction history is currently unavailable.")

        with st.expander("Prediction run information"):
            st.write(f"**Model:** {metadata['model']}")
            st.write(f"**Dataset:** {metadata['dataset']}")
            st.write(f"**Rows processed:** {metadata['rows']:,}")
            st.write(f"**Feature count:** {metadata['columns']:,}")
            st.write(f"**Run time:** {metadata['timestamp']}")
            st.write(f"**Problem type:** {metadata['problem_type']}")

        ai_insight(
            "Predictions are model estimates, not guarantees. Check data quality, "
            "feature compatibility, and—where possible—compare outputs with "
            "known outcomes before making real-world decisions."
        )

page_footer()

# =========================================================
# PREVIOUS / NEXT PAGE NAVIGATION
# Keep this at the very bottom of app/pages/7_Prediction.py.
# =========================================================
st.divider()
nav_previous, nav_spacer, nav_next = st.columns([1, 2, 1])

with nav_previous:
    if st.button(
        "⬅️ Previous: Business Forecasting",
        key="page7_previous_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/6_Business_Forecasting.py")

with nav_next:
    if st.button(
        "Next:➡️",
        key="page7_next_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/9_Interactive_Dashboard.py")
