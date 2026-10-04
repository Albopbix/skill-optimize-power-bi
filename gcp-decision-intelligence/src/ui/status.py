import streamlit as st


def loading(message="Processing..."):
    return st.spinner(message)


def success(message):
    st.success(f"✅ {message}")


def warning(message):
    st.warning(f"⚠️ {message}")


def error(message):
    st.error(f"❌ {message}")


def info(message):
    st.info(f"ℹ️ {message}")