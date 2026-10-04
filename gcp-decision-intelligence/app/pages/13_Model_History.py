
import streamlit as st
import pandas as pd

from src.database.database import Database
from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Model History",
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

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        padding: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    "🤖 Model History & Leaderboard",
    "Review trained machine-learning models, compare their "
    "recorded scores, and explore model history."
)


# ==========================================================
# LOAD DATABASE
# ==========================================================

try:
    database = Database()
    models = database.get_models()

except Exception as error:
    st.error("Unable to load model history from the database.")
    st.code(str(error))
    models = None


# ==========================================================
# EMPTY STATE
# ==========================================================

if models is None:
    st.warning("Model history could not be retrieved.")

elif len(models) == 0:

    st.info("🤖 No AI models have been trained yet.")

    st.markdown("### 🚀 Get Started")
    st.write(
        "Train a machine-learning model using the AutoML Engine. "
        "Once training results are saved, they can appear here "
        "for review and comparison."
    )

    ai_insight(
        "Model History records model-training results to help "
        "users review their experiments."
    )

else:

    # ======================================================
    # PREPARE MODEL DATA
    # ======================================================

    model_df = pd.DataFrame(
        models,
        columns=[
            "ID",
            "Dataset",
            "Model",
            "Score",
            "Problem Type",
            "Created At",
        ],
    )

    model_df["Score"] = pd.to_numeric(
        model_df["Score"],
        errors="coerce",
    )

    model_df["Dataset"] = (
        model_df["Dataset"].fillna("Unknown").astype(str)
    )

    model_df["Model"] = (
        model_df["Model"].fillna("Unknown").astype(str)
    )

    model_df["Problem Type"] = (
        model_df["Problem Type"].fillna("Unknown").astype(str)
    )

    model_df["Created At"] = (
        model_df["Created At"].fillna("").astype(str)
    )

    model_df["ID"] = model_df["ID"].astype(str)

    model_df = model_df[
        model_df["Score"].notna()
        & model_df["Score"].map(
            lambda value: pd.notna(value)
            and abs(float(value)) != float("inf")
        )
    ].copy()

    if model_df.empty:

        st.warning(
            "No models with valid numeric scores were found. "
            "Check the saved model records and their score values."
        )

    else:

        # ==================================================
        # SIDEBAR FILTERS
        # ==================================================

        st.sidebar.header("🔎 Model Filters")

        search = st.sidebar.text_input(
            "Search model name",
            placeholder="e.g. Random Forest",
        )

        available_datasets = sorted(
            model_df["Dataset"].unique().tolist()
        )

        selected_datasets = st.sidebar.multiselect(
            "Datasets",
            options=available_datasets,
            default=available_datasets,
        )

        available_types = sorted(
            model_df["Problem Type"].unique().tolist()
        )

        selected_types = st.sidebar.multiselect(
            "Problem types",
            options=available_types,
            default=available_types,
        )

        available_models = sorted(
            model_df["Model"].unique().tolist()
        )

        selected_models = st.sidebar.multiselect(
            "Algorithms",
            options=available_models,
            default=available_models,
        )

        min_score = float(model_df["Score"].min())
        max_score = float(model_df["Score"].max())

        if min_score < max_score:
            score_range = st.sidebar.slider(
                "Recorded score range",
                min_value=min_score,
                max_value=max_score,
                value=(min_score, max_score),
            )
        else:
            score_range = (min_score, max_score)
            st.sidebar.caption(
                f"All valid model scores are {min_score:.4f}."
            )

        if st.sidebar.button(
            "🔄 Reset filters",
            use_container_width=True,
        ):
            st.rerun()

        # ==================================================
        # APPLY FILTERS
        # ==================================================

        filtered_df = model_df.copy()

        if search.strip():
            filtered_df = filtered_df[
                filtered_df["Model"].str.contains(
                    search.strip(),
                    case=False,
                    regex=False,
                    na=False,
                )
            ]

        filtered_df = filtered_df[
            filtered_df["Dataset"].isin(selected_datasets)
            & filtered_df["Problem Type"].isin(selected_types)
            & filtered_df["Model"].isin(selected_models)
        ]

        filtered_df = filtered_df[
            filtered_df["Score"].between(
                score_range[0],
                score_range[1],
            )
        ]

        # ==================================================
        # SUMMARY METRICS
        # ==================================================

        st.subheader("📊 Model Summary")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Models Recorded",
                f"{len(filtered_df):,}",
            )

        with c2:
            st.metric(
                "Distinct Algorithms",
                filtered_df["Model"].nunique(),
            )

        with c3:
            st.metric(
                "Problem Types",
                filtered_df["Problem Type"].nunique(),
            )

        with c4:
            st.metric(
                "Datasets Used",
                filtered_df["Dataset"].nunique(),
            )

        st.caption(
            f"Showing {len(filtered_df):,} of "
            f"{len(model_df):,} model records with valid scores."
        )

        st.divider()

        # ==================================================
        # LEADERBOARD
        # ==================================================

        st.subheader("🏆 Model Leaderboard")

        if filtered_df.empty:

            st.warning(
                "No models match your current filters. "
                "Adjust the filters in the sidebar."
            )

        else:

            sort_order = st.selectbox(
                "Sort leaderboard",
                [
                    "Highest score first",
                    "Lowest score first",
                    "Model name A–Z",
                    "Dataset name A–Z",
                ],
            )

            if sort_order == "Highest score first":
                leaderboard = filtered_df.sort_values(
                    "Score",
                    ascending=False,
                )

            elif sort_order == "Lowest score first":
                leaderboard = filtered_df.sort_values(
                    "Score",
                    ascending=True,
                )

            elif sort_order == "Model name A–Z":
                leaderboard = filtered_df.sort_values(
                    "Model",
                    ascending=True,
                )

            else:
                leaderboard = filtered_df.sort_values(
                    "Dataset",
                    ascending=True,
                )

            st.dataframe(
                leaderboard,
                use_container_width=True,
                hide_index=True,
            )

            # ==============================================
            # TOP RECORDED SCORE
            # ==============================================

            st.divider()
            st.subheader("🥇 Highest Recorded Score")

            best_model = filtered_df.loc[
                filtered_df["Score"].idxmax()
            ]

            b1, b2, b3, b4 = st.columns(4)

            with b1:
                st.metric(
                    "Model",
                    str(best_model["Model"]),
                )

            with b2:
                st.metric(
                    "Score",
                    f"{best_model['Score']:.4f}",
                )

            with b3:
                st.metric(
                    "Dataset",
                    str(best_model["Dataset"]),
                )

            with b4:
                st.metric(
                    "Problem Type",
                    str(best_model["Problem Type"]),
                )

            st.caption(
                "This identifies the highest recorded numeric score. "
                "Scores are comparable only when their metric, "
                "evaluation method, and problem context are compatible."
            )

            # ==============================================
            # PERFORMANCE CHART
            # ==============================================

            st.divider()
            st.subheader("📈 Recorded Model Scores")

            chart_data = filtered_df[
                ["Model", "Dataset", "Score"]
            ].copy()

            chart_data["Label"] = (
                chart_data["Model"]
                + " — "
                + chart_data["Dataset"]
            )

            chart_data = chart_data.sort_values(
                "Score",
                ascending=True,
            )

            st.bar_chart(
                chart_data.set_index("Label")["Score"],
                x_label="Model — Dataset",
                y_label="Recorded Score",
            )

            # ==============================================
            # AVERAGE SCORE BY ALGORITHM
            # ==============================================

            st.divider()
            st.subheader("📊 Average Score by Algorithm")

            algorithm_summary = (
                filtered_df.groupby("Model")["Score"]
                .agg(["mean", "count", "min", "max"])
                .reset_index()
            )

            algorithm_summary.columns = [
                "Model",
                "Average Score",
                "Number of Records",
                "Minimum Score",
                "Maximum Score",
            ]

            algorithm_summary = algorithm_summary.sort_values(
                "Average Score",
                ascending=False,
            )

            st.dataframe(
                algorithm_summary.round(4),
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                algorithm_summary.set_index("Model")[
                    "Average Score"
                ],
                x_label="Algorithm",
                y_label="Average Recorded Score",
            )

            # ==============================================
            # SCORE DISTRIBUTION
            # ==============================================

            st.divider()
            st.subheader("📉 Score Distribution")

            st.write(
                "Review the spread of recorded model scores. "
                "This is descriptive and does not establish "
                "that the models used the same evaluation metric."
            )

            st.line_chart(
                filtered_df.sort_values("Score")[
                    ["Score"]
                ].reset_index(drop=True),
                x_label="Model record (sorted)",
                y_label="Recorded Score",
            )

            # ==============================================
            # MODEL DETAILS
            # ==============================================

            st.divider()
            st.subheader("🔍 Inspect a Model Record")

            selected_id = st.selectbox(
                "Choose a model record",
                options=filtered_df["ID"].tolist(),
                format_func=lambda record_id: (
                    f"{filtered_df.loc[
                        filtered_df['ID'] == record_id, 'Model'
                    ].iloc[0]} "
                    f"(ID: {record_id})"
                ),
            )

            selected_record = filtered_df[
                filtered_df["ID"] == selected_id
            ].iloc[0]

            d1, d2 = st.columns(2)

            with d1:
                st.markdown("**Model information**")
                st.write("Record ID:", selected_record["ID"])
                st.write("Algorithm:", selected_record["Model"])
                st.write("Dataset:", selected_record["Dataset"])

            with d2:
                st.markdown("**Evaluation information**")
                st.write(
                    "Problem Type:",
                    selected_record["Problem Type"],
                )
                st.write(
                    "Recorded Score:",
                    f"{selected_record['Score']:.4f}",
                )
                st.write(
                    "Created At:",
                    selected_record["Created At"],
                )

            # ==============================================
            # EXPORT
            # ==============================================

            st.divider()
            st.subheader("📥 Export Model History")

            export_data = leaderboard.copy()

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                st.download_button(
                    "📥 Download Filtered Models",
                    data=export_data.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="filtered_model_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with export_col2:
                st.download_button(
                    "📦 Download All Valid Model Records",
                    data=model_df.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="all_model_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# ==========================================================
# AI INSIGHT
# ==========================================================

st.divider()

ai_insight(
    "Model History helps users explore previously trained "
    "machine-learning models, compare stored evaluation scores, "
    "and review experiment records. Confirm that models use "
    "compatible evaluation metrics before comparing their scores."
)


# ==========================================================
# PREVIOUS / HOME / NEXT NAVIGATION
# ==========================================================

st.divider()

st.subheader("🧭 Page Navigation")

nav_prev, nav_home, nav_next = st.columns(3)

with nav_prev:
    if st.button(
        "⬅️ Previous: Dataset History",
        use_container_width=True,
    ):
        st.switch_page("pages/12_Dataset_History.py")

with nav_home:
    if st.button(
        "🏠 Home",
        use_container_width=True,
    ):
        st.switch_page("pages/0_Home.py")

with nav_next:
    if st.button(
        "Next: Prediction History ➡️",
        use_container_width=True,
    ):
        st.switch_page("pages/14_Prediction_History.py")


# ==========================================================
# FOOTER
# ==========================================================

page_footer()
