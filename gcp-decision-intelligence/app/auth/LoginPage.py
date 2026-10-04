
import os
import sys
from datetime import datetime

import streamlit as st

# =========================================================
# PROJECT PATHS
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =========================================================
# EXISTING DATABASE AND AUTHENTICATION
# =========================================================

from src.database.database import Database
from src.auth.auth import Auth

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nex Decision AI | Sign In",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    /* PAGE */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(22, 91, 190, 0.20),
                transparent 36%
            ),
            radial-gradient(
                circle at 95% 90%,
                rgba(107, 45, 190, 0.15),
                transparent 35%
            ),
            #030916;
        color: #F4F7FF;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1500px;
        padding: 1.5rem 2.5rem 2rem;
    }

    h1, h2, h3, h4 {
        color: #F4F7FF !important;
    }

    p, label {
        color: #C5D3EA;
    }

    /* BRAND */

    .brand-icon {
        width: 58px;
        height: 58px;
        min-width: 58px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        background: linear-gradient(135deg, #087CFF, #8247FF);
        color: white;
        border-radius: 17px;
        font-size: 30px;
        font-weight: 800;
        line-height: 1;
        padding: 0;
        box-shadow: 0 0 28px rgba(35, 110, 255, 0.23);
    }

    .brand-title {
        font-size: 29px;
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1.25;
        color: #F4F7FF;
        margin: 0;
    }

    .brand-title span {
        color: #36C9FF;
    }

    .brand-subtitle {
        font-size: 10px;
        letter-spacing: 1.25px;
        color: #91B5E9;
        margin-top: 7px;
        line-height: 1.8;
    }

    /* LEFT HERO */

    .eyebrow {
        display: inline-block;
        color: #55D5FF;
        background: rgba(15, 116, 220, 0.12);
        border: 1px solid rgba(51, 169, 255, 0.38);
        border-radius: 30px;
        padding: 9px 14px;
        margin-top: 25px;
        margin-bottom: 17px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
    }

    .hero-title {
        color: #F4F7FF;
        font-size: clamp(33px, 3.1vw, 49px);
        font-weight: 800;
        line-height: 1.17;
        letter-spacing: -1.8px;
        margin-bottom: 18px;
    }

    .gradient-text {
        background: linear-gradient(
            90deg,
            #31D4FF 0%,
            #527BFF 55%,
            #B05CFF 100%
        );
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-description {
        color: #AEC3E4;
        font-size: 13px;
        line-height: 1.9;
        margin-bottom: 18px;
    }

    /* FEATURE CARDS */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(7, 20, 40, 0.72);
        border: 1px solid rgba(92, 132, 185, 0.28);
        border-radius: 14px;
    }

    .feature-heading {
        color: #E9F2FF;
        font-weight: 700;
        font-size: 14px;
    }

    /* LOGIN PANEL */

    .login-title {
        text-align: center;
        color: #F4F7FF;
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .login-subtitle {
        text-align: center;
        color: #91B5E9;
        font-size: 11px;
        line-height: 1.8;
        margin-bottom: 18px;
    }

    /* INPUTS */

    .stTextInput label {
        color: #D8E5FA !important;
        font-size: 12px !important;
        font-weight: 500;
    }

    div[data-baseweb="input"] {
        background: #101B30 !important;
        border: 1px solid #2C4567 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #438FFF !important;
        box-shadow: 0 0 0 2px rgba(67, 143, 255, 0.13);
    }

    div[data-baseweb="input"] input {
        background: transparent !important;
        color: #F5F8FF !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: #8498B7 !important;
    }

    /* RADIO TABS */

    div[role="radiogroup"] {
        display: flex;
        gap: 8px;
        background: #071326;
        border: 1px solid #203B60;
        border-radius: 11px;
        padding: 8px;
    }

    div[role="radiogroup"] label {
        color: #D5E3F8 !important;
        font-size: 12px !important;
    }

    /* BUTTONS */

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 44px;
        border: 1px solid #438BFF;
        border-radius: 10px;
        background: linear-gradient(
            110deg,
            #087CFF,
            #514BFF,
            #8846F5
        );
        color: white;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: #74D7FF;
        color: white;
        box-shadow: 0 0 20px rgba(55, 124, 255, 0.22);
    }

    /* CHECKBOX AND CAPTIONS */

    .stCheckbox label {
        color: #AFC2E1 !important;
        font-size: 11px !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #91A6C5;
    }

    /* FOOTER */

    .footer {
        color: #7187A7;
        font-size: 10px;
        line-height: 1.9;
        margin-top: 20px;
    }

    hr {
        border-color: rgba(80, 123, 183, 0.23) !important;
    }

    /* MOBILE */

    @media (max-width: 800px) {
        .block-container {
            padding: 1rem;
        }

        .brand-title {
            font-size: 23px;
        }

        .hero-title {
            font-size: 35px;
            letter-spacing: -1px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "logged_in": False,
    "username": "",
    "user_email": "",
    "login_time": "",
    "registered_at": "",
    "auth_page": "Sign In",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# INITIALIZE DATABASE
# =========================================================

database = Database()
auth = Auth()

# =========================================================
# BRAND HEADER
# =========================================================

def render_brand():
    icon_col, title_col = st.columns(
        [0.09, 0.91],
        gap="small",
    )

    with icon_col:
        st.markdown(
            '<div class="brand-icon">N</div>',
            unsafe_allow_html=True,
        )

    with title_col:
        st.markdown(
            '<div class="brand-title">'
            'Nex Decision <span>AI</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="brand-subtitle">'
            'SMARTER DATA &nbsp; | &nbsp; BETTER DECISIONS'
            '&nbsp; | &nbsp; BIGGER TOMORROW'
            '</div>',
            unsafe_allow_html=True,
        )

# =========================================================
# HERO SECTION
# =========================================================

def render_hero():
    st.markdown(
        '<div class="eyebrow">'
        '✦ &nbsp; INTELLIGENCE FOR BETTER DECISIONS'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-title">'
        'Turn Your Data Into<br>'
        '<span class="gradient-text">'
        'Powerful Decisions.'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-description">'
        'Discover patterns hidden in your business data. '
        'Generate predictions, explore trends, understand '
        'model outputs and transform analytical findings '
        'into actionable business insights.'
        '</div>',
        unsafe_allow_html=True,
    )

# =========================================================
# FEATURE CARDS
# =========================================================

def render_features():
    features = [
        (
            "📊",
            "Data Analysis",
            "Explore datasets and discover patterns.",
        ),
        (
            "🧠",
            "AI Insights",
            "Discover meaningful business insights.",
        ),
        (
            "🎯",
            "Predictions",
            "Predict outcomes using machine learning.",
        ),
        (
            "📈",
            "Forecasting",
            "Explore future business trends.",
        ),
        
        (
            "📄",
            "Reports",
            "Present findings in business reports.",
        ),
    ]

    # Two columns keep the feature section compact.
    for start in range(0, len(features), 2):
        columns = st.columns(2, gap="small")

        for column, feature in zip(
            columns,
            features[start:start + 2],
        ):
            icon, title, description = feature

            with column:
                with st.container(border=True):
                    st.markdown(f"### {icon}")
                    st.markdown(f"**{title}**")
                    st.caption(description)

# =========================================================
# SIGN-IN FORM
# =========================================================

def render_login_form():
    st.markdown(
        '<div class="login-title">Welcome Back 👋</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="login-subtitle">'
        'Sign in to access your dashboard, analytics, '
        'predictions and AI tools.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("signin_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
        )

        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
        )

        st.caption(
            "Use the username and password associated "
            "with your account."
        )

        submitted = st.form_submit_button(
            "🔑  Sign In to Nex Decision AI",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    username_clean = username.strip()

    if not username_clean:
        st.warning("Please enter your username.")
        return

    if not password:
        st.warning("Please enter your password.")
        return

    try:
        user = database.get_user(username_clean)

        if user is None:
            st.error("No account was found with that username.")
            return

        # Existing database user record:
        # 0 = id
        # 1 = username
        # 2 = password hash
        # 3 = email
        stored_password = user[2]

        if not auth.verify_password(
            password,
            stored_password,
        ):
            st.error("Incorrect password. Please try again.")
            return

        try:
            database.update_last_login(username_clean)
        except Exception:
            pass

        try:
            profile = database.get_user_profile(username_clean)
        except Exception:
            profile = user

        st.session_state.logged_in = True
        st.session_state.username = profile[1]

        st.session_state.user_email = (
            profile[2]
            if len(profile) > 2 and profile[2]
            else "Email not provided"
        )

        st.session_state.login_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )

        st.session_state.registered_at = (
            str(profile[3])
            if len(profile) > 3 and profile[3]
            else ""
        )

        st.rerun()

    except Exception:
        st.error(
            "Unable to complete sign in. Check your database "
            "connection and authentication configuration."
        )

# =========================================================
# CREATE ACCOUNT FORM
# =========================================================

def render_registration_form():
    st.markdown(
        '<div class="login-title">Create Account ✨</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="login-subtitle">'
        'Create your account to explore business intelligence.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("registration_form"):
        username = st.text_input(
            "Username",
            placeholder="Choose a username",
        )

        email = st.text_input(
            "Email address",
            placeholder="Enter your email address",
        )

        password = st.text_input(
            "Password",
            placeholder="Create a password",
            type="password",
        )

        confirm_password = st.text_input(
            "Confirm password",
            placeholder="Re-enter your password",
            type="password",
        )

        submitted = st.form_submit_button(
            "✨  Create My Account",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    username_clean = username.strip()
    email_clean = email.strip()
    password_clean = password

    if not username_clean:
        st.warning("Please enter a username.")
        return

    if not email_clean:
        st.warning("Please enter your email address.")
        return

    if (
        "@" not in email_clean
        or "." not in email_clean.rsplit("@", 1)[-1]
    ):
        st.warning("Please enter a valid email address.")
        return

    if not password_clean:
        st.warning("Please create a password.")
        return

    if password_clean != confirm_password:
        st.error("The passwords do not match.")
        return

    if len(password_clean) < 6:
        st.warning(
            "Your password must contain at least 6 characters."
        )
        return

    try:
        existing_user = database.get_user(username_clean)

        if existing_user is not None:
            st.error("That username is already registered.")
            return

        # Use the existing email lookup when available.
        email_lookup = getattr(
            database,
            "get_user_by_email",
            None,
        )

        if callable(email_lookup):
            try:
                existing_email = email_lookup(email_clean)
            except (AttributeError, NotImplementedError):
                existing_email = None

            if existing_email is not None:
                st.error(
                    "That email address is already registered."
                )
                return

        hashed_password = auth.hash_password(password_clean)

        database.create_user(
            username_clean,
            hashed_password,
            email_clean,
        )

        st.success("Your account has been created successfully!")

        st.info(
            "Select Sign In above to log in with your new account."
        )

    except Exception:
        st.error(
            "Unable to create your account. Check your database "
            "configuration and try again."
        )

# =========================================================
# LOGOUT
# =========================================================

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_email = ""
    st.session_state.login_time = ""
    st.session_state.registered_at = ""
    st.session_state.auth_page = "Sign In"
    st.rerun()

# =========================================================
# AUTHENTICATED VIEW
# =========================================================

if st.session_state.logged_in:
    render_brand()

    st.write("")
    st.success(
        f"Welcome back, {st.session_state.username}!"
    )

    st.markdown("### Your Profile")

    st.write(
        f"**Username:** {st.session_state.username}"
    )
    st.write(
        f"**Email:** {st.session_state.user_email}"
    )
    st.write(
        f"**Login time:** {st.session_state.login_time}"
    )

    if st.session_state.registered_at:
        st.write(
            f"**Registered:** {st.session_state.registered_at}"
        )

    st.info(
        "Continue to your existing application navigation "
        "to access dashboards, analytics and reports."
    )

    if st.button(
        "🚪 Sign Out",
        type="primary",
        use_container_width=True,
    ):
        logout()

    st.stop()

# =========================================================
# MAIN PAGE
# =========================================================

render_brand()
st.write("")

# Keep the login panel alongside the introduction.
left, right = st.columns(
    [1.08, 0.92],
    gap="large",
)

# ---------------- LEFT: LANDING PAGE ----------------

with left:
    render_hero()
    render_features()

    st.markdown(
        '<div class="footer">'
        '<strong>DATA TODAY. DECISIONS TOMORROW.</strong><br>'
        'Explore your data. Understand the patterns. '
        'Make informed decisions.'
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------- RIGHT: AUTHENTICATION ----------------

with right:
    with st.container(border=True):
        st.markdown(
            '<div class="login-title">'
            'Nex Decision <span style="color:#36C9FF;">AI</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="login-subtitle">'
            'AI-Powered Business Intelligence Platform'
            '</div>',
            unsafe_allow_html=True,
        )

        st.radio(
            "Account",
            ["Sign In", "Create Account"],
            horizontal=True,
            key="auth_page",
            label_visibility="collapsed",
        )

        st.divider()

        if st.session_state.auth_page == "Sign In":
            render_login_form()
        else:
            render_registration_form()

        st.divider()

        st.caption(
            "🔒 Keep your account credentials private."
        )

    st.markdown(
        '<div class="footer" style="text-align:center;">'
        'Nex Decision AI · Business Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )
