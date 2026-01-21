import streamlit as st

from cards import (
    charts_card,
    chat_card,
    dataframe_card,
    layouts_card,
    media_card,
    status_card,
    text_card,
    widgets_card,
)

st.title("Streamlit element explorer")

st.markdown(
    "This app displays most of Streamlit's built-in elements so you can "
    "conveniently explore how they look with different theming configurations "
    "applied."
)

cols = st.columns(2)
with cols[0].container(height=310):
    widgets_card()
with cols[1].container(height=310):
    layouts_card()
with cols[0].container(height=310):
    dataframe_card()
with cols[1].container(height=310):
    charts_card()
with cols[0].container(height=310):
    status_card()
with cols[1].container(height=310):
    text_card()
with cols[0].container(height=310):
    chat_card()
with cols[1].container(height=310):
    media_card()
