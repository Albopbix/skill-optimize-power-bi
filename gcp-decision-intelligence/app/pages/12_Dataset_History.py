
import streamlit as st
import pandas as pd

from src.database.database import Database
from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Dataset History",
    page_icon="📂",
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
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# PAGE HEADER
# ==========================================================

page_header(
    "📂 Dataset History",
    "Track uploaded datasets, inspect historical records, "
    "analyze upload patterns, and export history."
)


# ==========================================================
# LOAD DATABASE
# ==========================================================

try:
    database = Database()
    history = database.get_uploads()

except Exception as error:
    st.error("Unable to load dataset history from the database.")
    st.code(str(error))
    history = None


# ==========================================================
# EMPTY STATE
# ==========================================================

if history is None:
    st.warning("Dataset history could not be retrieved.")

elif len(history) == 0:
    st.info(
        "📂 No datasets have been uploaded yet. "
        "Upload a dataset to begin building your history."
    )

    st.markdown("### 🚀 Get Started")
    st.write(
        "After uploading a CSV or Excel dataset, its upload "
        "information can appear here for tracking and review."
    )

else:

    # ======================================================
    # CREATE DATAFRAME
    # ======================================================

    history_df = pd.DataFrame(
        history,
        columns=[
            "ID",
            "Filename",
            "Rows",
            "Columns",
            "Dataset Type",
            "Upload Time",
        ],
    )

    history_df["Rows"] = pd.to_numeric(
        history_df["Rows"], errors="coerce"
    ).fillna(0)

    history_df["Columns"] = pd.to_numeric(
        history_df["Columns"], errors="coerce"
    ).fillna(0)

    history_df["Filename"] = (
        history_df["Filename"].fillna("Unknown").astype(str)
    )

    history_df["Dataset Type"] = (
        history_df["Dataset Type"].fillna("Unknown").astype(str)
    )

    history_df["Upload Time"] = (
        history_df["Upload Time"].fillna("").astype(str)
    )

    # Keep the original display value and create a parsed date
    # for filtering and chronological sorting.
    history_df["_parsed_date"] = pd.to_datetime(
        history_df["Upload Time"],
        errors="coerce",
        utc=True,
    )

    history_df["_parsed_date"] = (
        history_df["_parsed_date"].dt.tz_convert(None)
    )

    history_df["_filename_lower"] = (
        history_df["Filename"].str.lower()
    )

    # ======================================================
    # SIDEBAR FILTERS
    # ======================================================

    st.sidebar.header("🔎 History Filters")

    search = st.sidebar.text_input(
        "Search filename",
        placeholder="Enter a filename...",
    )

    available_types = sorted(
        history_df["Dataset Type"].unique().tolist()
    )

    selected_types = st.sidebar.multiselect(
        "Dataset type",
        options=available_types,
        default=available_types,
    )

    min_rows = int(history_df["Rows"].min())
    max_rows = int(history_df["Rows"].max())

    row_range = st.sidebar.slider(
        "Number of rows",
        min_value=min_rows,
        max_value=max_rows,
        value=(min_rows, max_rows),
    )

    valid_dates = history_df["_parsed_date"].dropna()

    date_range = None

    if not valid_dates.empty:

        first_date = valid_dates.min().date()
        last_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Upload date range",
            value=(first_date, last_date),
        )

    if st.sidebar.button(
        "🔄 Reset Filters",
        use_container_width=True,
    ):
        st.rerun()

    # ======================================================
    # APPLY FILTERS
    # ======================================================

    filtered_df = history_df.copy()

    if search.strip():
        filtered_df = filtered_df[
            filtered_df["_filename_lower"].str.contains(
                search.strip().lower(),
                regex=False,
                na=False,
            )
        ]

    filtered_df = filtered_df[
        filtered_df["Dataset Type"].isin(selected_types)
    ]

    filtered_df = filtered_df[
        filtered_df["Rows"].between(
            row_range[0], row_range[1]
        )
    ]

    if date_range and len(date_range) == 2:

        start_date, end_date = date_range

        start_timestamp = pd.Timestamp(start_date)
        end_timestamp = (
            pd.Timestamp(end_date) + pd.Timedelta(days=1)
        )

        # Retain records with unparseable dates rather than
        # silently removing them from the history.
        in_date_range = (
            filtered_df["_parsed_date"].isna()
            | (
                (filtered_df["_parsed_date"] >= start_timestamp)
                & (filtered_df["_parsed_date"] < end_timestamp)
            )
        )

        filtered_df = filtered_df[in_date_range]

    # ======================================================
    # PAGE TITLE AND SUMMARY
    # ======================================================

    st.subheader("📊 Upload Summary")

    total_datasets = len(history_df)
    filtered_datasets = len(filtered_df)

    total_rows = int(filtered_df["Rows"].sum())
    total_columns = int(filtered_df["Columns"].sum())

    dataset_types_count = filtered_df["Dataset Type"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "📁 Total Uploads",
            f"{filtered_datasets:,}",
            delta=f"{filtered_datasets - total_datasets:+,} vs all"
            if filtered_datasets != total_datasets else None,
        )

    with c2:
        st.metric("📄 Combined Rows", f"{total_rows:,}")

    with c3:
        st.metric("📊 Combined Columns", f"{total_columns:,}")

    with c4:
        st.metric("🗂️ Dataset Types", dataset_types_count)

    st.caption(
        f"Showing {filtered_datasets:,} of "
        f"{total_datasets:,} historical uploads."
    )

    st.divider()

    # ======================================================
    # HISTORY TABLE
    # ======================================================

    st.subheader("📋 Upload Records")

    sort_by = st.selectbox(
        "Sort records by",
        [
            "Newest upload",
            "Oldest upload",
            "Filename A–Z",
            "Most rows",
            "Most columns",
        ],
    )

    if sort_by == "Newest upload":
        filtered_df = filtered_df.sort_values(
            "_parsed_date",
            ascending=False,
            na_position="last",
        )

    elif sort_by == "Oldest upload":
        filtered_df = filtered_df.sort_values(
            "_parsed_date",
            ascending=True,
            na_position="last",
        )

    elif sort_by == "Filename A–Z":
        filtered_df = filtered_df.sort_values(
            "Filename",
            ascending=True,
        )

    elif sort_by == "Most rows":
        filtered_df = filtered_df.sort_values(
            "Rows",
            ascending=False,
        )

    elif sort_by == "Most columns":
        filtered_df = filtered_df.sort_values(
            "Columns",
            ascending=False,
        )

    display_df = filtered_df[
        [
            "ID",
            "Filename",
            "Rows",
            "Columns",
            "Dataset Type",
            "Upload Time",
        ]
    ].copy()

    if display_df.empty:
        st.warning(
            "No upload records match the current filters. "
            "Try changing your search or filter settings."
        )

    else:
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ======================================================
    # DATASET DETAIL VIEW
    # ======================================================

    st.divider()
    st.subheader("🔍 Inspect an Upload")

    if not filtered_df.empty:

        selected_index = st.selectbox(
            "Choose an upload",
            options=filtered_df.index.tolist(),
            format_func=lambda idx: (
                f"{filtered_df.loc[idx, 'Filename']} "
                f"(ID: {filtered_df.loc[idx, 'ID']})"
            ),
        )

        selected_record = filtered_df.loc[selected_index]

        d1, d2, d3 = st.columns(3)

        with d1:
            st.metric(
                "Rows",
                f"{int(selected_record['Rows']):,}",
            )

        with d2:
            st.metric(
                "Columns",
                f"{int(selected_record['Columns']):,}",
            )

        with d3:
            st.metric(
                "Dataset Type",
                str(selected_record["Dataset Type"]),
            )

        st.write("**Filename:**", selected_record["Filename"])
        st.write("**Upload ID:**", selected_record["ID"])
        st.write("**Upload Time:**", selected_record["Upload Time"])

        st.caption(
            "This view displays stored upload metadata. "
            "It does not automatically reload the original dataset."
        )

    # ======================================================
    # DATASET TYPE DISTRIBUTION
    # ======================================================

    st.divider()
    st.subheader("📈 Dataset Type Distribution")

    if not filtered_df.empty:

        dataset_count = (
            filtered_df["Dataset Type"]
            .value_counts()
            .rename_axis("Dataset Type")
            .reset_index(name="Count")
        )

        chart_col, summary_col = st.columns([2, 1])

        with chart_col:
            st.bar_chart(
                dataset_count.set_index("Dataset Type"),
                x_label="Dataset Type",
                y_label="Number of Uploads",
            )

        with summary_col:
            st.markdown("**Upload breakdown**")

            st.dataframe(
                dataset_count,
                use_container_width=True,
                hide_index=True,
            )

    else:
        st.info("No data is available for the distribution chart.")

    # ======================================================
    # ROW COUNT DISTRIBUTION
    # ======================================================

    st.divider()
    st.subheader("📊 Dataset Size Overview")

    if not filtered_df.empty:

        size_col1, size_col2 = st.columns(2)

        with size_col1:
            st.metric(
                "Average Rows per Upload",
                f"{filtered_df['Rows'].mean():,.1f}",
            )

        with size_col2:
            st.metric(
                "Largest Dataset",
                f"{int(filtered_df['Rows'].max()):,} rows",
            )

        size_distribution = filtered_df[
            ["Filename", "Rows"]
        ].copy()

        size_distribution = size_distribution.sort_values(
            "Rows",
            ascending=False,
        ).head(15)

        st.bar_chart(
            size_distribution.set_index("Filename"),
            x_label="Filename",
            y_label="Rows",
        )

    # ======================================================
    # DOWNLOAD HISTORY
    # ======================================================

    st.divider()
    st.subheader("📥 Export History")

    download_col1, download_col2 = st.columns(2)

    with download_col1:

        export_filtered = filtered_df[
            [
                "ID",
                "Filename",
                "Rows",
                "Columns",
                "Dataset Type",
                "Upload Time",
            ]
        ]

        st.download_button(
            "📥 Download Filtered Records",
            data=export_filtered.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="filtered_dataset_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_col2:

        export_all = history_df[
            [
                "ID",
                "Filename",
                "Rows",
                "Columns",
                "Dataset Type",
                "Upload Time",
            ]
        ]

        st.download_button(
            "📦 Download All Records",
            data=export_all.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="all_dataset_history.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ==========================================================
# AI INSIGHT
# ==========================================================

st.divider()

ai_insight(
    "Dataset History provides a searchable record of uploaded "
    "datasets. Filtering, size summaries, and downloadable records "
    "help users track their data assets and maintain project "
    "traceability."
)


# ==========================================================
# PREVIOUS / HOME / NEXT PAGE NAVIGATION
# ==========================================================

st.divider()

st.subheader("🧭 Page Navigation")

st.caption(
    "Move between the previous page, Home, and the next page "
    "in NexDecision AI."
)

nav_prev, nav_home, nav_next = st.columns(3)

with nav_prev:

    if st.button(
        "⬅️ Previous: AI Chat",
        use_container_width=True,
    ):
        st.switch_page("pages/11_AI_Chat.py")

with nav_home:

    if st.button(
        "🏠 Home",
        use_container_width=True,
    ):
        st.switch_page("pages/0_Home.py")

with nav_next:

    if st.button(
        "Next: Model History ➡️",
        use_container_width=True,
    ):
        st.switch_page("pages/13_Model_History.py")


# ==========================================================
# FOOTER
# ==========================================================

page_footer()
