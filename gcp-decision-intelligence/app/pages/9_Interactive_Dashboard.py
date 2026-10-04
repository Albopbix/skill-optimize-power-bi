
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.ui.layout import page_header, ai_insight, page_footer


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Interactive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM STYLING
# ==========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.20);
        padding: 16px;
        border-radius: 12px;
    }

    div[data-testid="stPlotlyChart"] {
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
    "📊 Interactive Dashboard",
    "Explore business data through interactive visualizations, "
    "discover patterns, and investigate data quality."
)


# ==========================================================
# DATASET VALIDATION
# ==========================================================

if "dataset" not in st.session_state:
    st.warning("Upload a dataset first.")
    st.stop()

original_df = st.session_state["dataset"]

if not isinstance(original_df, pd.DataFrame):
    st.error("The uploaded dataset is not a valid DataFrame.")
    st.stop()

if original_df.empty:
    st.warning("The uploaded dataset is empty.")
    st.stop()

# Preserve the original uploaded data.
df = original_df.copy()

# Sample large datasets for responsive chart rendering.
MAX_ROWS = 5000

if len(df) > MAX_ROWS:
    st.info(
        f"The dataset contains {len(df):,} rows. "
        f"Charts will use a reproducible sample of {MAX_ROWS:,} rows "
        "for performance. Data exploration and CSV export retain "
        "the full filtered dataset."
    )

    # Use the same sample for charts and analysis.
    # Filtering and export will operate on the full dataset below.
    chart_source = df.sample(
        n=MAX_ROWS,
        random_state=42
    )
else:
    chart_source = df.copy()


# ==========================================================
# COLUMN CLASSIFICATION
# ==========================================================

numeric_cols = df.select_dtypes(
    include="number"
).columns.tolist()

categorical_cols = df.select_dtypes(
    include=["object", "category", "bool", "string"]
).columns.tolist()

datetime_cols = df.select_dtypes(
    include=["datetime", "datetimetz"]
).columns.tolist()

# Include likely date columns stored as text.
for col in df.select_dtypes(
    include=["object", "string"]
).columns:
    if col not in datetime_cols:
        name = str(col).lower()

        if any(word in name for word in [
            "date", "datetime", "timestamp"
        ]):
            parsed = pd.to_datetime(
                df[col], errors="coerce"
            )

            if parsed.notna().mean() >= 0.8:
                datetime_cols.append(col)


# ==========================================================
# SIDEBAR FILTERS
# ==========================================================

st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.caption("Filters apply to the full dataset.")

filtered_df = df.copy()

with st.sidebar.expander(
    "🔎 Category Filters",
    expanded=True
):
    filter_cols = [
        col for col in categorical_cols
        if df[col].nunique(dropna=True) <= 100
    ]

    for col in filter_cols:
        values = df[col].dropna().unique().tolist()

        if not values:
            continue

        selected = st.multiselect(
            f"{col}",
            options=values,
            key=f"interactive_filter_{col}",
        )

        if selected:
            filtered_df = filtered_df[
                filtered_df[col].isin(selected)
            ]


with st.sidebar.expander("📏 Numeric Filters"):
    for col in numeric_cols:
        series = pd.to_numeric(
            filtered_df[col],
            errors="coerce"
        ).dropna()

        if series.empty:
            continue

        minimum = float(series.min())
        maximum = float(series.max())

        if minimum >= maximum:
            continue

        low, high = st.slider(
            f"{col}",
            min_value=minimum,
            max_value=maximum,
            value=(minimum, maximum),
            key=f"interactive_range_{col}",
        )

        filtered_df = filtered_df[
            filtered_df[col].between(low, high)
            | filtered_df[col].isna()
        ]


if filtered_df.empty:
    st.warning(
        "No records match your filters. "
        "Adjust the sidebar selections."
    )
    st.stop()


# ==========================================================
# DATASET OVERVIEW
# ==========================================================

st.subheader("📌 Dataset Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Filtered Records",
    f"{len(filtered_df):,}"
)

k2.metric(
    "Total Columns",
    f"{len(filtered_df.columns):,}"
)

k3.metric(
    "Missing Cells",
    f"{int(filtered_df.isna().sum().sum()):,}"
)

k4.metric(
    "Duplicate Rows",
    f"{int(filtered_df.duplicated().sum()):,}"
)

st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} original records."
)

st.divider()


# ==========================================================
# DASHBOARD TABS
# ==========================================================

overview_tab, builder_tab, explorer_tab, quality_tab = st.tabs(
    [
        "📈 Overview",
        "🛠️ Chart Builder",
        "🗂️ Data Explorer",
        "🧪 Data Quality",
    ]
)


# ==========================================================
# TAB 1: AUTOMATIC VISUALIZATIONS
# ==========================================================

with overview_tab:

    st.subheader("Distribution Analysis")

    left, right = st.columns(2)

    # ------------------------------------------------------
    # HISTOGRAM
    # ------------------------------------------------------

    with left:
        if numeric_cols:
            hist_col = st.selectbox(
                "Numeric column",
                numeric_cols,
                key="overview_hist_column",
            )

            fig = px.histogram(
                filtered_df,
                x=hist_col,
                nbins=30,
                marginal="box",
                title=f"Distribution of {hist_col}",
                template="plotly_white",
            )

            fig.update_layout(
                height=400,
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "No numeric columns available for a histogram."
            )

    # ------------------------------------------------------
    # PIE CHART
    # ------------------------------------------------------

    with right:
        if categorical_cols:
            pie_col = st.selectbox(
                "Category column",
                categorical_cols,
                key="overview_pie_column",
            )

            counts = (
                filtered_df[pie_col]
                .fillna("(Missing)")
                .astype(str)
                .value_counts()
                .head(10)
                .rename_axis("Category")
                .reset_index(name="Count")
            )

            fig = px.pie(
                counts,
                names="Category",
                values="Count",
                hole=0.45,
                title=f"Top Categories: {pie_col}",
                template="plotly_white",
            )

            fig.update_layout(height=400)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "No categorical columns available for a pie chart."
            )

    # ------------------------------------------------------
    # SCATTER PLOT
    # ------------------------------------------------------

    st.divider()
    st.subheader("Relationship Analysis")

    if len(numeric_cols) >= 2:
        c1, c2, c3 = st.columns(3)

        with c1:
            scatter_x = st.selectbox(
                "X-axis",
                numeric_cols,
                index=0,
                key="overview_scatter_x",
            )

        with c2:
            y_index = (
                1 if numeric_cols[0] == scatter_x else 0
            )

            scatter_y = st.selectbox(
                "Y-axis",
                numeric_cols,
                index=y_index,
                key="overview_scatter_y",
            )

        with c3:
            scatter_color = st.selectbox(
                "Color by",
                ["None"] + categorical_cols,
                key="overview_scatter_color",
            )

        plot_df = filtered_df

        if len(plot_df) > MAX_ROWS:
            plot_df = plot_df.sample(
                MAX_ROWS,
                random_state=42
            )

        fig = px.scatter(
            plot_df,
            x=scatter_x,
            y=scatter_y,
            color=(
                scatter_color
                if scatter_color != "None"
                else None
            ),
            hover_data=[scatter_x, scatter_y],
            title=f"{scatter_x} vs {scatter_y}",
            template="plotly_white",
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info(
            "At least two numeric columns are required "
            "for a scatter plot."
        )

    # ------------------------------------------------------
    # CORRELATION HEATMAP
    # ------------------------------------------------------

    st.divider()
    st.subheader("Correlation Heatmap")

    if len(numeric_cols) >= 2:
        heatmap_cols = st.multiselect(
            "Choose numeric features",
            numeric_cols,
            default=numeric_cols[:min(10, len(numeric_cols))],
            key="overview_heatmap_cols",
        )

        if len(heatmap_cols) >= 2:
            corr = filtered_df[heatmap_cols].corr()

            fig = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                aspect="auto",
                title="Feature Correlation Matrix",
            )

            fig.update_layout(
                height=max(400, len(heatmap_cols) * 40)
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            upper_triangle = corr.where(
                np.triu(
                    np.ones(corr.shape),
                    k=1
                ).astype(bool)
            ).stack()

            if not upper_triangle.empty:
                pair = upper_triangle.abs().idxmax()
                coefficient = upper_triangle.loc[pair]

                st.info(
                    f"Strongest absolute correlation: "
                    f"{pair[0]} and {pair[1]} "
                    f"(r = {coefficient:.3f}). "
                    "Correlation does not imply causation."
                )
        else:
            st.info(
                "Select at least two columns for correlation analysis."
            )
    else:
        st.info(
            "Correlation analysis requires at least two numeric columns."
        )


# ==========================================================
# TAB 2: INTERACTIVE CHART BUILDER
# ==========================================================

with builder_tab:

    st.subheader("🛠️ Custom Chart Builder")

    chart_type = st.selectbox(
        "Choose visualization",
        [
            "Scatter Plot",
            "Line Chart",
            "Bar Chart",
            "Histogram",
            "Box Plot",
            "Violin Plot",
            "Pie Chart",
            "Correlation Heatmap",
        ],
        key="builder_chart_type",
    )

    # ------------------------------------------------------
    # HISTOGRAM
    # ------------------------------------------------------

    if chart_type == "Histogram":

        if numeric_cols:
            x_col = st.selectbox(
                "Numeric column",
                numeric_cols,
                key="builder_hist_x",
            )

            bins = st.slider(
                "Number of bins",
                min_value=5,
                max_value=100,
                value=30,
                key="builder_hist_bins",
            )

            fig = px.histogram(
                filtered_df,
                x=x_col,
                nbins=bins,
                marginal="box",
                template="plotly_white",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info("A histogram requires a numeric column.")

    # ------------------------------------------------------
    # PIE CHART
    # ------------------------------------------------------

    elif chart_type == "Pie Chart":

        if categorical_cols:
            x_col = st.selectbox(
                "Category column",
                categorical_cols,
                key="builder_pie_x",
            )

            top_n = st.slider(
                "Maximum categories",
                min_value=3,
                max_value=20,
                value=10,
                key="builder_pie_top_n",
            )

            counts = (
                filtered_df[x_col]
                .fillna("(Missing)")
                .astype(str)
                .value_counts()
                .head(top_n)
                .rename_axis("Category")
                .reset_index(name="Count")
            )

            fig = px.pie(
                counts,
                names="Category",
                values="Count",
                hole=0.4,
                template="plotly_white",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info("A pie chart requires a categorical column.")

    # ------------------------------------------------------
    # CORRELATION HEATMAP
    # ------------------------------------------------------

    elif chart_type == "Correlation Heatmap":

        if len(numeric_cols) >= 2:
            selected_cols = st.multiselect(
                "Numeric features",
                numeric_cols,
                default=numeric_cols[:min(10, len(numeric_cols))],
                key="builder_heatmap_cols",
            )

            if len(selected_cols) >= 2:
                fig = px.imshow(
                    filtered_df[selected_cols].corr(),
                    text_auto=".2f",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    aspect="auto",
                    template="plotly_white",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )
            else:
                st.info("Select at least two numeric columns.")
        else:
            st.info("At least two numeric columns are required.")

    # ------------------------------------------------------
    # SCATTER, LINE, BAR, BOX, VIOLIN
    # ------------------------------------------------------

    else:

        x_options = list(
            dict.fromkeys(
                categorical_cols
                + numeric_cols
                + datetime_cols
            )
        )

        if not x_options or not numeric_cols:
            st.info(
                "This chart requires suitable X-axis and numeric columns."
            )
        else:
            c1, c2 = st.columns(2)

            with c1:
                x_col = st.selectbox(
                    "X-axis",
                    x_options,
                    key="builder_x",
                )

            with c2:
                y_col = st.selectbox(
                    "Y-axis",
                    numeric_cols,
                    key="builder_y",
                )

            color_col = st.selectbox(
                "Group by / Color",
                ["None"] + categorical_cols,
                key="builder_color",
            )

            plot_df = filtered_df

            if len(plot_df) > MAX_ROWS:
                plot_df = plot_df.sample(
                    MAX_ROWS,
                    random_state=42
                )

            color_arg = (
                color_col
                if color_col != "None"
                else None
            )

            if chart_type == "Scatter Plot":

                fig = px.scatter(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    template="plotly_white",
                )

            elif chart_type == "Line Chart":

                fig = px.line(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    template="plotly_white",
                )

            elif chart_type == "Bar Chart":

                aggregation = st.selectbox(
                    "Aggregation",
                    ["Sum", "Mean", "Median", "Count"],
                    key="builder_bar_aggregation",
                )

                if aggregation == "Count":
                    plot_df = (
                        plot_df.groupby(
                            x_col,
                            dropna=False,
                        )[y_col]
                        .count()
                        .reset_index(name="Count")
                    )

                    fig = px.bar(
                        plot_df,
                        x=x_col,
                        y="Count",
                        template="plotly_white",
                    )

                else:
                    agg_func = {
                        "Sum": "sum",
                        "Mean": "mean",
                        "Median": "median",
                    }[aggregation]

                    plot_df = (
                        plot_df.groupby(
                            x_col,
                            dropna=False,
                        )[y_col]
                        .agg(agg_func)
                        .reset_index()
                    )

                    fig = px.bar(
                        plot_df,
                        x=x_col,
                        y=y_col,
                        template="plotly_white",
                    )

            elif chart_type == "Box Plot":

                fig = px.box(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    template="plotly_white",
                )

            else:

                fig = px.violin(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_arg,
                    box=True,
                    template="plotly_white",
                )

            fig.update_layout(height=520)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


# ==========================================================
# TAB 3: DATA EXPLORER
# ==========================================================

with explorer_tab:

    st.subheader("🗂️ Data Explorer")

    st.caption(
        "Inspect filtered records and download the selected data."
    )

    selected_columns = st.multiselect(
        "Columns to display",
        options=filtered_df.columns.tolist(),
        default=filtered_df.columns.tolist()[
            :min(10, len(filtered_df.columns))
        ],
        key="explorer_columns",
    )

    if selected_columns:
        st.dataframe(
            filtered_df[selected_columns],
            use_container_width=True,
            height=420,
        )
    else:
        st.info("Select at least one column.")

    st.markdown("#### Statistical Summary")

    summary = filtered_df.describe(
        include="all"
    ).transpose()

    st.dataframe(
        summary,
        use_container_width=True,
    )

    st.download_button(
        label="⬇️ Download Filtered Dataset (CSV)",
        data=filtered_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="filtered_dataset.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ==========================================================
# TAB 4: DATA QUALITY
# ==========================================================

with quality_tab:

    st.subheader("🧪 Data Quality Report")

    missing_report = pd.DataFrame({
        "Column": filtered_df.columns,
        "Missing Values": (
            filtered_df.isna().sum().values
        ),
        "Missing %": (
            filtered_df.isna().mean().values * 100
        ).round(2),
        "Unique Values": (
            filtered_df.nunique(dropna=True).values
        ),
        "Data Type": (
            filtered_df.dtypes.astype(str).values
        ),
    }).sort_values(
        "Missing %",
        ascending=False,
    )

    st.markdown("#### Missing Values by Column")

    st.dataframe(
        missing_report,
        use_container_width=True,
    )

    missing_only = missing_report[
        missing_report["Missing Values"] > 0
    ]

    if not missing_only.empty:

        fig = px.bar(
            missing_only,
            x="Column",
            y="Missing %",
            title="Missing Data Percentage",
            template="plotly_white",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.success("No missing values found in the filtered data.")

    # ------------------------------------------------------
    # DUPLICATE ROWS
    # ------------------------------------------------------

    st.markdown("#### Duplicate Records")

    duplicate_count = int(
        filtered_df.duplicated().sum()
    )

    st.metric(
        "Duplicate Rows",
        f"{duplicate_count:,}",
    )

    # ------------------------------------------------------
    # OUTLIER DETECTION
    # ------------------------------------------------------

    st.markdown("#### Potential Numeric Outliers")

    outlier_rows = []

    for col in numeric_cols:

        series = filtered_df[col].dropna()

        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = int(
            (
                (series < lower)
                | (series > upper)
            ).sum()
        )

        outlier_rows.append({
            "Column": col,
            "Potential Outliers": count,
            "Lower Bound": round(float(lower), 3),
            "Upper Bound": round(float(upper), 3),
        })

    if outlier_rows:

        st.dataframe(
            pd.DataFrame(outlier_rows),
            use_container_width=True,
        )

        st.caption(
            "Outliers use the 1.5 × IQR rule. "
            "Flagged values are not necessarily errors."
        )

    else:
        st.info("No numeric columns available for outlier analysis.")

    # ------------------------------------------------------
    # AUTOMATED DATA SUMMARY
    # ------------------------------------------------------

    st.markdown("#### Automated Summary")

    total_cells = (
        len(filtered_df) * len(filtered_df.columns)
    )

    missing_cells = int(
        filtered_df.isna().sum().sum()
    )

    missing_pct = (
        missing_cells / total_cells * 100
        if total_cells else 0
    )

    st.write(f"**Records analyzed:** {len(filtered_df):,}")
    st.write(f"**Numeric columns:** {len(numeric_cols)}")
    st.write(f"**Categorical columns:** {len(categorical_cols)}")
    st.write(f"**Missing cells:** {missing_cells:,}")
    st.write(f"**Missing-cell rate:** {missing_pct:.2f}%")
    st.write(f"**Duplicate rows:** {duplicate_count:,}")

    if len(numeric_cols) >= 2:

        corr = filtered_df[numeric_cols].corr()

        pairs = corr.where(
            np.triu(
                np.ones(corr.shape),
                k=1,
            ).astype(bool)
        ).stack()

        if not pairs.empty:

            pair = pairs.abs().idxmax()
            value = pairs.loc[pair]

            st.write(
                f"**Strongest absolute correlation:** "
                f"{pair[0]} vs {pair[1]} "
                f"(r = {value:.3f})"
            )

    ai_insight(
        "Explore distributions, correlations, missing values, "
        "duplicates, and potential outliers to understand your data. "
        "Treat statistical patterns as evidence for investigation, "
        "not proof of causation."
    )

# ==========================================================
# CUSTOM NAVIGATION BAR
# ==========================================================

if "dashboard_page" not in st.session_state:
    st.session_state["dashboard_page"] = "Overview"

st.markdown(
    """
    <style>
    div.stButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

nav_items = [
    ("Overview", "📈 Overview"),
    ("Chart Builder", "🛠️ Chart Builder"),
    ("Data Explorer", "🗂️ Data Explorer"),
    ("Data Quality", "🧪 Data Quality"),
]

nav_cols = st.columns(4)

for col, (page_key, label) in zip(nav_cols, nav_items):
    with col:
        if st.button(
            label,
            key=f"nav_{page_key}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["dashboard_page"] == page_key
                else "secondary"
            ),
        ):
            st.session_state["dashboard_page"] = page_key
            st.rerun()

st.divider()

current_page = st.session_state["dashboard_page"]
# =========================================================
# PREVIOUS / NEXT PAGE NAVIGATION
# Keep this at the very bottom of app/pages/7_Prediction.py.
# =========================================================
st.divider()
nav_previous, nav_spacer, nav_next = st.columns([1, 2, 1])

with nav_previous:
    if st.button(
        "⬅️ Previous: Prediction",
        key="page7_previous_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/7_Prediction.py")

with nav_next:
    if st.button(
        "Next: 11_AI_Chat.py➡️",
        key="page7_next_navigation",
        use_container_width=True,
    ):
        st.switch_page("pages/11_AI_Chat.py")


# ==========================================================
# FOOTER
# ==========================================================

page_footer()
