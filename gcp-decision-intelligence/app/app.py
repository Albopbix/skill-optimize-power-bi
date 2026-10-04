
import os
import sys
import streamlit as st

# =========================================================
# PROJECT PATH
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nex Decision AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "login_time" not in st.session_state:
    st.session_state.login_time = ""


# =========================================================
# LOGIN PAGE
# =========================================================

login_page = st.Page(
    "auth/LoginPage.py",
    title="Sign In",
    icon="🔐",
    url_path="signin"
)


# =========================================================
# APPLICATION PAGES
# =========================================================

home_page = st.Page(
    "pages/0_Home.py",
    title="Home",
    icon="🏠"
)

upload_page = st.Page(
    "pages/1_Upload_Dataset.py",
    title="Upload Dataset",
    icon="📂"
)

dataset_page = st.Page(
    "pages/2_Dataset_Intelligence.py",
    title="Dataset Intelligence",
    icon="🧠"
)

copilot_page = st.Page(
    "pages/3_AI_Business_Copilot.py",
    title="AI Business Copilot",
    icon="🤖"
)

executive_page = st.Page(
    "pages/4_Executive_Dashboard.py",
    title="Executive Dashboard",
    icon="📊"
)

automl_page = st.Page(
    "pages/5_AutoML.py",
    title="AutoML",
    icon="⚙️"
)

forecasting_page = st.Page(
    "pages/6_Business_Forecasting.py",
    title="Business Forecasting",
    icon="📈"
)

# The merged Prediction Studio uses this single page.
prediction_page = st.Page(
    "pages/7_Prediction.py",
    title="Prediction Studio",
    icon="🔮",
    url_path="prediction-studio"
)


interactive_page = st.Page(
    "pages/9_Interactive_Dashboard.py",
    title="Interactive Dashboard",
    icon="📊"
)



chat_page = st.Page(
    "pages/11_AI_Chat.py",
    title="AI Chat",
    icon="💬"
)

dataset_history_page = st.Page(
    "pages/12_Dataset_History.py",
    title="Dataset History",
    icon="📚"
)

model_history_page = st.Page(
    "pages/13_Model_History.py",
    title="Model History",
    icon="🧪"
)

prediction_history_page = st.Page(
    "pages/14_Prediction_History.py",
    title="Prediction History",
    icon="📜"
)

anomaly_page = st.Page(
    "pages/17_AI_Anomaly_Detection.py",
    title="AI Anomaly Detection",
    icon="🚨"
)

report_page = st.Page(
    "pages/18_Executive_Report.py",
    title="Executive Report",
    icon="📄"
)


# =========================================================
# LOGOUT
# =========================================================

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_email = ""
    st.session_state.login_time = ""

    # Remove uploaded dataset from current session.
    for key in ("dataset", "filename"):
        st.session_state.pop(key, None)


# =========================================================
# LOGIN STATE
# =========================================================

if not st.session_state.logged_in:
    pg = st.navigation(
        [login_page],
        position="hidden"
    )

    pg.run()
    st.stop()


# =========================================================
# AUTHENTICATED APPLICATION NAVIGATION
# =========================================================

pages = {
    "Nex Decision AI": [
        home_page,
        upload_page,
        dataset_page,
        copilot_page,
        executive_page,
        automl_page,
        forecasting_page,
        prediction_page,
        
        interactive_page,
        
        chat_page,
        dataset_history_page,
        model_history_page,
        prediction_history_page,
        anomaly_page,
        report_page
    ]
}


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:700;
            margin-bottom:5px;
        ">
            🤖 Nex Decision AI
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        f"👤 Signed in as: {st.session_state.username}"
    )

    if st.session_state.user_email:
        st.caption(
            f"📧 {st.session_state.user_email}"
        )

    st.divider()

    if st.button("🚪 Logout", width="stretch"):
        logout()
        st.rerun()


# =========================================================
# APPLICATION NAVIGATION
# =========================================================

pg = st.navigation(
    pages,
    position="sidebar"
)

pg.run()
