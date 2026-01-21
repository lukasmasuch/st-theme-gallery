from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import theme_loader
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

# Get the themes directory path
THEMES_DIR = str(Path(__file__).parent / "themes")
DEFAULT_THEME = "jupyter-theme"


def get_available_themes():
    """Read all theme files from the themes folder."""
    themes_dir = Path(THEMES_DIR)
    if themes_dir.exists():
        themes = sorted([f.stem for f in themes_dir.glob("*.toml")])
        return themes
    return []


# Initialize session state for theme selection
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = DEFAULT_THEME

# Load the theme for this session (must be early, before other st.* calls)
theme_loader.load_theme_by_name(st.session_state.selected_theme, THEMES_DIR)

# Theme selector in sidebar
available_themes = get_available_themes()

if available_themes:
    # Find current theme index
    current_index = 0
    if st.session_state.selected_theme in available_themes:
        current_index = available_themes.index(st.session_state.selected_theme)

    selected_theme = st.sidebar.selectbox(
        "Theme",
        available_themes,
        index=current_index,
        format_func=lambda x: x.replace("-theme", "").replace("-", " ").title(),
        key="theme_selector",
    )

    # Update session state if theme changed
    if selected_theme != st.session_state.selected_theme:
        st.session_state.selected_theme = selected_theme
        st.rerun()

st.sidebar.divider()

if "init" not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(
        np.random.randn(20, 3), columns=["a", "b", "c"]
    )
    st.session_state.map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
        columns=["lat", "lon"],
    )
    st.session_state.init = True


pages = [
    st.Page("home.py", title="Home", icon=":material/home:"),
    st.Page("widgets.py", title="Widgets", icon=":material/widgets:"),
    st.Page("text.py", title="Text", icon=":material/article:"),
    st.Page("data.py", title="Data", icon=":material/table:"),
    st.Page("charts.py", title="Charts", icon=":material/insert_chart:"),
    st.Page("media.py", title="Media", icon=":material/image:"),
    st.Page("layouts.py", title="Layouts", icon=":material/dashboard:"),
    st.Page("chat.py", title="Chat", icon=":material/chat:"),
    st.Page("status.py", title="Status", icon=":material/error:"),
]

page = st.navigation(pages)
page.run()

with st.sidebar.container(height=310):
    if page.title == "Widgets":
        widgets_card()
    elif page.title == "Text":
        text_card()
    elif page.title == "Data":
        dataframe_card()
    elif page.title == "Charts":
        charts_card()
    elif page.title == "Media":
        media_card()
    elif page.title == "Layouts":
        layouts_card()
    elif page.title == "Chat":
        chat_card()
    elif page.title == "Status":
        status_card()
    else:
        st.page_link("home.py", label="Home", icon=":material/home:")
        st.write("Welcome to the home page!")
        st.write(
            "Select a page from above. This sidebar thumbnail shows a subset of "
            "elements from each page so you can see the sidebar theme."
        )

st.sidebar.caption(
    f"Current theme: **{st.session_state.selected_theme.replace('-theme', '').replace('-', ' ').title()}**"
)
