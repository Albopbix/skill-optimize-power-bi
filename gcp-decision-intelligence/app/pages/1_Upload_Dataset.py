import streamlit as st
import pandas as pd
import textwrap

from src.ui.layout import page_header, ai_insight, page_footer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Upload Dataset | Nex Decision AI",
    page_icon="📂",
    layout="wide"
)


# ============================================================
# CUSTOM PAGE STYLE
# ============================================================

st.markdown(
    textwrap.dedent("""
    <style>

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .upload-hero {
        padding: 28px 32px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            rgba(49, 51, 63, 0.95),
            rgba(31, 41, 55, 0.92)
        );
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 25px;
    }

    .upload-title {
        font-size: 30px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .upload-subtitle {
        font-size: 15px;
        opacity: 0.72;
        line-height: 1.6;
        max-width: 900px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 14px;
    }

    .info-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.20);
        min-height: 105px;
    }

    .info-icon {
        font-size: 26px;
    }

    .info-title {
        font-size: 15px;
        font-weight: 700;
        margin-top: 6px;
    }

    .info-text {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 4px;
        line-height: 1.5;
    }

    .upload-zone {
        padding: 24px;
        border-radius: 18px;
        border: 1px solid rgba(100,150,255,0.25);
        background: rgba(70,100,180,0.06);
        margin-top: 10px;
        margin-bottom: 20px;
        line-height: 2;
    }

    .format-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .format-item {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.20);
        font-size: 13px;
    }

    .status-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.18);
        margin-top: 15px;
    }

    .status-title {
        font-size: 15px;
        font-weight: 700;
    }

    .status-text {
        font-size: 13px;
        opacity: 0.72;
        margin-top: 5px;
    }

    </style>
    """),
    unsafe_allow_html=True
)


# ============================================================
# DATASET LOADER
# ============================================================

@st.cache_data
def load_dataset(file_bytes, filename):
    """
    Load supported business/data-science dataset formats.
    """

    try:

        from io import BytesIO, StringIO

        extension = filename.lower().split(".")[-1]

        # ----------------------------------------------------
        # CSV
        # ----------------------------------------------------

        if extension == "csv":

            return pd.read_csv(
                BytesIO(file_bytes)
            )

        # ----------------------------------------------------
        # EXCEL
        # ----------------------------------------------------

        elif extension in ["xlsx", "xls"]:

            return pd.read_excel(
                BytesIO(file_bytes)
            )

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        elif extension == "json":

            return pd.read_json(
                BytesIO(file_bytes)
            )

        # ----------------------------------------------------
        # TSV
        # ----------------------------------------------------

        elif extension == "tsv":

            return pd.read_csv(
                BytesIO(file_bytes),
                sep="\t"
            )

        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        elif extension == "txt":

            return pd.read_csv(
                StringIO(
                    file_bytes.decode("utf-8")
                )
            )

        # ----------------------------------------------------
        # PARQUET
        # ----------------------------------------------------

        elif extension == "parquet":

            return pd.read_parquet(
                BytesIO(file_bytes)
            )

        return None

    except Exception:
        return None


# ============================================================
# PAGE HEADER
# ============================================================




# ============================================================
# HERO
# ============================================================

st.markdown(
    textwrap.dedent("""
    <div class="upload-hero">
        <div class="upload-title">
            📂 Bring Your Business Data Into Nex Decision AI
        </div>
        <div class="upload-subtitle">
            Upload structured business data and prepare it for
            data intelligence, machine learning, forecasting,
            anomaly detection and decision analysis.
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


# ============================================================
# WHAT HAPPENS AFTER UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">🚀 What Nex Decision AI Will Analyze</div>',
    unsafe_allow_html=True
)

analysis_features = [
    (
        "📊",
        "Dataset Statistics",
        "Rows, columns and essential dataset measurements."
    ),
    (
        "🔎",
        "Data Structure",
        "Identify numeric, categorical and date-based fields."
    ),
    (
        "🧹",
        "Data Quality",
        "Detect missing values and duplicate records."
    ),
    (
        "🤖",
        "AI Opportunities",
        "Prepare the dataset for machine-learning analysis."
    ),
]

feature_columns = st.columns(4)

for column, feature in zip(
    feature_columns,
    analysis_features
):

    icon, title, description = feature

    with column:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="info-card">
                    <div class="info-icon">{icon}</div>
                    <div class="info-title">{title}</div>
                    <div class="info-text">{description}</div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


st.markdown("---")


# ============================================================
# SUPPORTED FORMATS
# ============================================================

st.markdown(
    '<div class="section-title">📁 Supported Data Formats</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="format-list">
        <span class="format-item">📄 CSV</span>
        <span class="format-item">📊 Excel XLSX</span>
        <span class="format-item">📊 Excel XLS</span>
        <span class="format-item">🧾 JSON</span>
        <span class="format-item">📑 TSV</span>
        <span class="format-item">🗃️ Parquet</span>
        <span class="format-item">📋 TXT</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILE UPLOADER
# ============================================================

st.markdown(
    '<div class="section-title">📤 Choose Your Dataset</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=[
        "csv",
        "xlsx",
        "xls",
        "json",
        "tsv",
        "parquet",
        "txt"
    ],
    help=(
        "Supported formats: CSV, Excel, JSON, TSV, "
        "Parquet and TXT."
    )
)


# ============================================================
# PROCESS UPLOADED DATASET
# ============================================================

if uploaded_file is not None:

    try:

        with st.spinner(
            "Reading and validating your dataset..."
        ):

            file_bytes = uploaded_file.getvalue()

            df = load_dataset(
                file_bytes,
                uploaded_file.name
            )


        # ====================================================
        # VALIDATION
        # ====================================================

        if df is None:

            st.error(
                "❌ We couldn't read this file. "
                "Please check that the file is valid and "
                "uses a supported tabular format."
            )

            st.stop()


        if df.empty:

            st.warning(
                "⚠️ The uploaded dataset is empty. "
                "Please upload a dataset containing records."
            )

            st.stop()


        # ====================================================
        # STORE DATASET
        # ====================================================

        st.session_state["dataset"] = df

        st.session_state["filename"] = uploaded_file.name


        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            f"✅ Dataset '{uploaded_file.name}' uploaded successfully."
        )


        # ====================================================
        # FILE INFORMATION
        # ====================================================

        file_size_mb = len(file_bytes) / (1024 * 1024)

        extension = (
            uploaded_file.name
            .lower()
            .split(".")[-1]
            .upper()
        )

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="status-card">
                    <div class="status-title">
                        📁 {uploaded_file.name}
                    </div>
                    <div class="status-text">
                        Format: {extension}
                        &nbsp; • &nbsp;
                        Size: {file_size_mb:.2f} MB
                        &nbsp; • &nbsp;
                        Status: Ready for analysis
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )


        # ====================================================
        # DATASET OVERVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">📊 Dataset Overview</div>',
            unsafe_allow_html=True
        )

        missing_values = int(
            df.isnull().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "📄 Rows",
                f"{len(df):,}"
            )

        with c2:

            st.metric(
                "📊 Columns",
                f"{len(df.columns):,}"
            )

        with c3:

            st.metric(
                "⚠️ Missing Values",
                f"{missing_values:,}"
            )

        with c4:

            st.metric(
                "🔁 Duplicate Rows",
                f"{duplicate_rows:,}"
            )


        st.divider()


        # ====================================================
        # DATASET PREVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">📋 Dataset Preview</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Showing the first 10 records to verify that the dataset was loaded correctly."
        )

        st.dataframe(
            df.head(10),
            width="stretch",
            hide_index=True
        )


        st.divider()


        # ====================================================
        # DATASET STRUCTURE
        # ====================================================

        st.markdown(
            '<div class="section-title">🔎 Dataset Structure</div>',
            unsafe_allow_html=True
        )

        numeric_columns = len(
            df.select_dtypes(
                include="number"
            ).columns
        )

        categorical_columns = len(
            df.select_dtypes(
                include=["object", "category"]
            ).columns
        )

        datetime_columns = len(
            df.select_dtypes(
                include=["datetime"]
            ).columns
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "🔢 Numeric Columns",
                numeric_columns
            )

        with c2:

            st.metric(
                "🔤 Categorical Columns",
                categorical_columns
            )

        with c3:

            st.metric(
                "📅 Date Columns",
                datetime_columns
            )


        # ====================================================
        # DATASET INFORMATION
        # ====================================================

        with st.expander(
            "📋 View Detailed Dataset Information"
        ):

            st.write("### Column Names")

            st.write(
                list(df.columns)
            )

            st.write("### Data Types")

            datatype_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": [
                    str(dtype)
                    for dtype in df.dtypes
                ]
            })

            st.dataframe(
                datatype_df,
                width="stretch",
                hide_index=True
            )


        # ====================================================
        # DATA QUALITY
        # ====================================================

        st.markdown(
            '<div class="section-title">🧹 Data Quality Snapshot</div>',
            unsafe_allow_html=True
        )

        quality_columns = st.columns(3)

        with quality_columns[0]:

            if missing_values == 0:

                st.success(
                    "✅ No missing values detected"
                )

            else:

                st.warning(
                    f"⚠️ {missing_values:,} missing values detected"
                )


        with quality_columns[1]:

            if duplicate_rows == 0:

                st.success(
                    "✅ No duplicate rows detected"
                )

            else:

                st.warning(
                    f"⚠️ {duplicate_rows:,} duplicate rows detected"
                )


        with quality_columns[2]:

            st.success(
                "✅ Dataset structure detected"
            )


        # ====================================================
        # READY STATUS
        # ====================================================

        st.markdown(
            textwrap.dedent("""
            <div class="status-card">
                <div class="status-title">
                    🚀 Dataset Ready
                </div>
                <div class="status-text">
                    Your dataset is now available to Nex Decision AI.
                    Continue to Dataset Intelligence to discover
                    patterns, data-quality issues and analytical opportunities.
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )


    except Exception as error:

        st.error(
            "❌ We couldn't process this dataset."
        )

        st.info(
            """
            Please check that:

            • The file is a valid supported format  
            • The file is not corrupted  
            • The dataset contains tabular data  

            Then try uploading it again.
            """
        )


# ============================================================
# AI INSIGHT
# ============================================================

ai_insight(
    "Clean and well-structured business data helps Nex Decision AI generate more reliable insights and predictions."
)


# ============================================================
# NAVIGATION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧭 Continue Your Analysis</div>',
    unsafe_allow_html=True
)

n1, n2 = st.columns(2)

with n1:

    if st.button(
        "← Previous · Home",
        width="stretch"
    ):

        st.switch_page(
            "pages/0_Home.py"
        )


with n2:

    if st.button(
        "Next · Dataset Intelligence →",
        width="stretch"
    ):

        st.switch_page(
            "pages/2_Dataset_Intelligence.py"
        )


# ============================================================
# FOOTER
# ============================================================

page_footer()