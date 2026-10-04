import streamlit as st


def page_header(title, description):

    st.title(title)

    st.caption(description)

    st.markdown("---")


def ai_insight(message):

    st.markdown("---")

    st.subheader("🤖 Insight da IA")

    st.info(message)


def page_footer():

    st.markdown("---")

    st.caption(
        "Plataforma de Inteligência de Decisão com IA | Versão 2.0 | © 2026 Jashwanth S"
    )