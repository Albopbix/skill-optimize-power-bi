import streamlit as st


def sidebar():

    st.sidebar.title("🤖 AI Decision Intelligence")

    st.sidebar.markdown("---")

    # ==========================================
    # DATASET STATUS
    # ==========================================

    st.sidebar.subheader("📂 Dataset Status")

    if "dataset" in st.session_state:

        df = st.session_state["dataset"]

        st.sidebar.success("Dataset Loaded")

        st.sidebar.metric("Rows", f"{len(df):,}")

        st.sidebar.metric("Columns", len(df.columns))

        missing = int(df.isnull().sum().sum())

        duplicates = int(df.duplicated().sum())

        st.sidebar.metric("Missing", missing)

        st.sidebar.metric("Duplicates", duplicates)

        score = 100

        score -= min(missing * 2, 30)

        score -= min(duplicates * 2, 20)

        score = max(score, 0)

        st.sidebar.metric("Health Score", f"{score}/100")

    else:

        st.sidebar.warning("No Dataset Loaded")

    st.sidebar.markdown("---")

    # ==========================================
    # SYSTEM STATUS
    # ==========================================

    st.sidebar.subheader("⚙️ System Status")

    st.sidebar.success("AI Engine Ready")

    st.sidebar.success("AutoML Available")

    st.sidebar.success("Forecast Ready")

    st.sidebar.success("Reports Enabled")

    st.sidebar.markdown("---")

    # ==========================================
    # QUICK HELP
    # ==========================================

    st.sidebar.subheader("💡 Quick Start")

    st.sidebar.write("1️⃣ Upload Dataset")

    st.sidebar.write("2️⃣ Analyze Dataset")

    st.sidebar.write("3️⃣ Train AutoML")

    st.sidebar.write("4️⃣ Predict")

    st.sidebar.write("5️⃣ Generate Report")

    st.sidebar.markdown("---")

    # ==========================================
    # FOOTER
    # ==========================================

    st.sidebar.caption("AI-Driven Decision Intelligence")

    st.sidebar.caption("Enterprise Analytics Suite")

    st.sidebar.caption("Version 2.0")