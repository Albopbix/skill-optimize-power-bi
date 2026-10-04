import streamlit as st


def kpi_card(title, value, delta=None):

    if delta is None:

        st.metric(
            label=title,
            value=value
        )

    else:

        st.metric(
            label=title,
            value=value,
            delta=delta
        )


def section(title):

    st.markdown("## " + title)

    st.markdown("---")