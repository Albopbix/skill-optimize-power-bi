import streamlit as st


def page_header(title, description):

    st.title(title)

    st.caption(description)

    st.markdown("---")


def ai_insight(message):

    st.markdown("---")

    st.subheader("🤖 AI Insight")

    st.info(message)


def page_footer():

    st.markdown("---")

    st.caption(
        "AI-Driven Decision Intelligence Platform | Version 2.0 | © 2026 Jashwanth S"
    )