import base64
import json
import tomllib
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
DEFAULT_THEME = "airbnb-theme"

# Sentinel value used for a user-forked (custom) theme. Doubles as the value of
# the `theme` query param and of st.session_state.selected_theme when active.
CUSTOM_THEME_SENTINEL = "custom"


def get_available_themes():
    """Read all theme files from the themes folder."""
    themes_dir = Path(THEMES_DIR)
    if themes_dir.exists():
        themes = sorted([f.stem for f in themes_dir.glob("*.toml")])
        return themes
    return []


def encode_theme_value(name: str, toml_text: str) -> str:
    """Encode a forked theme's name + TOML into a URL-safe query param value."""
    payload = json.dumps({"name": name, "toml": toml_text})
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii")


def decode_theme_value(value: str) -> dict | None:
    """Decode a `theme-value` query param.

    Returns {"name": str, "toml": str} or None if the envelope is malformed.
    Only the envelope (base64 + JSON shape) is validated here; TOML validity is
    checked separately at apply time so the two failure modes stay distinct.
    """
    try:
        raw = base64.urlsafe_b64decode(value.encode("ascii")).decode("utf-8")
        payload = json.loads(raw)
        if (
            isinstance(payload, dict)
            and isinstance(payload.get("name"), str)
            and isinstance(payload.get("toml"), str)
        ):
            return payload
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return None


def format_theme_name(theme_name: str) -> str:
    """Format a theme file stem into a human-readable display name."""
    return theme_name.replace("-theme", "").replace("-", " ").title()


# Get available themes first (needed for validation)
available_themes = get_available_themes()

# Check for theme in query parameters
query_params = st.query_params
theme_from_url = query_params.get("theme", None)
theme_value_from_url = query_params.get("theme-value", None)

# Resolve a forked (custom) theme from the URL, if present.
custom_payload = None
if theme_from_url == CUSTOM_THEME_SENTINEL and theme_value_from_url:
    custom_payload = decode_theme_value(theme_value_from_url)

# Initialize session state for theme selection
if "selected_theme" not in st.session_state:
    if custom_payload is not None:
        # Custom theme: name is derived by parsing the theme-value param.
        st.session_state.selected_theme = CUSTOM_THEME_SENTINEL
        st.session_state.custom_theme_name = custom_payload["name"]
        st.session_state.custom_theme_toml = custom_payload["toml"]
    # If theme is in URL and valid, use it; otherwise use default
    elif theme_from_url and theme_from_url in available_themes:
        st.session_state.selected_theme = theme_from_url
    elif theme_from_url:
        # Try with -theme suffix
        theme_with_suffix = f"{theme_from_url}-theme"
        if theme_with_suffix in available_themes:
            st.session_state.selected_theme = theme_with_suffix
        else:
            st.session_state.selected_theme = DEFAULT_THEME
    else:
        st.session_state.selected_theme = DEFAULT_THEME

# Load the theme for this session (must be early, before other st.* calls)
if st.session_state.selected_theme == CUSTOM_THEME_SENTINEL:
    custom_toml = st.session_state.get("custom_theme_toml", "")
    loaded = False
    if custom_toml:
        try:
            theme_loader.load_theme_from_toml(custom_toml)
            loaded = True
        except (tomllib.TOMLDecodeError, ValueError):
            loaded = False
    if not loaded:
        # Malformed custom theme: fall back to default and clear custom state.
        st.session_state.selected_theme = DEFAULT_THEME
        st.session_state.pop("custom_theme_name", None)
        st.session_state.pop("custom_theme_toml", None)
        st.session_state["_pending_theme_sync"] = True
        st.query_params["theme"] = DEFAULT_THEME
        if "theme-value" in st.query_params:
            del st.query_params["theme-value"]
        theme_loader.load_theme_by_name(DEFAULT_THEME, THEMES_DIR)
else:
    theme_loader.load_theme_by_name(st.session_state.selected_theme, THEMES_DIR)

# Theme selector in sidebar
if available_themes:
    # Inject the custom sentinel as a (pinned-to-top) option when active.
    is_custom_active = st.session_state.selected_theme == CUSTOM_THEME_SENTINEL
    options = list(available_themes)
    if is_custom_active:
        options = [CUSTOM_THEME_SENTINEL] + options

    def format_theme_option(x):
        if x == CUSTOM_THEME_SENTINEL:
            name = st.session_state.get("custom_theme_name", "Custom")
            return f"{name} (Custom)"
        return format_theme_name(x)

    # The widget key is the source of truth for user-driven changes. Seed it
    # from selected_theme only on first render or after a programmatic change
    # (e.g. forking) so we never clobber a fresh user selection. A persisted
    # widget value otherwise takes precedence over any index, which would
    # silently revert programmatic changes.
    if (
        "theme_selector" not in st.session_state
        or st.session_state.pop("_pending_theme_sync", False)
    ):
        st.session_state.theme_selector = st.session_state.selected_theme

    selected_theme = st.sidebar.selectbox(
        "Theme",
        options,
        format_func=format_theme_option,
        key="theme_selector",
    )

    # Update session state and URL if theme changed
    if selected_theme != st.session_state.selected_theme:
        st.session_state.selected_theme = selected_theme
        if selected_theme == CUSTOM_THEME_SENTINEL:
            # Re-selecting custom: keep query params reflecting the custom theme.
            name = st.session_state.get("custom_theme_name", "Custom")
            toml_text = st.session_state.get("custom_theme_toml", "")
            st.query_params["theme"] = CUSTOM_THEME_SENTINEL
            st.query_params["theme-value"] = encode_theme_value(name, toml_text)
        else:
            # Switching to a preset: clear custom state + theme-value param.
            st.query_params["theme"] = selected_theme
            if "theme-value" in st.query_params:
                del st.query_params["theme-value"]
            st.session_state.pop("custom_theme_name", None)
            st.session_state.pop("custom_theme_toml", None)
        st.rerun()


@st.dialog("Install Theme")
def show_install_dialog():
    """Show installation instructions for the selected theme."""
    theme_name = st.session_state.selected_theme

    if theme_name == CUSTOM_THEME_SENTINEL:
        display_name = st.session_state.get("custom_theme_name", "Custom")
        theme_content = st.session_state.get("custom_theme_toml", "")
    else:
        theme_path = Path(THEMES_DIR) / f"{theme_name}.toml"
        # Read the theme file content
        with open(theme_path, "r") as f:
            theme_content = f.read()
        display_name = format_theme_name(theme_name)

    st.markdown(f"### {display_name} Theme")

    st.markdown(
        "To install this theme, create or update your `.streamlit/config.toml` file "
        "with the following content:"
    )

    st.code(theme_content, language="toml")

    st.markdown("**Steps:**")
    st.markdown(
        """
1. Create a `.streamlit` folder in your project root (if it doesn't exist)
2. Create a `config.toml` file inside `.streamlit/`
3. Paste the theme configuration above
4. Restart your Streamlit app
"""
    )


def seed_fork_inputs():
    """Seed the fork dialog inputs from the currently selected theme.

    Called when the dialog opens (before its widgets render) so each open
    starts from the current theme rather than stale prior edits.
    """
    current = st.session_state.selected_theme
    if current == CUSTOM_THEME_SENTINEL:
        st.session_state.fork_name = st.session_state.get("custom_theme_name", "Custom")
        st.session_state.fork_toml = st.session_state.get("custom_theme_toml", "")
    else:
        st.session_state.fork_name = format_theme_name(current)
        with open(Path(THEMES_DIR) / f"{current}.toml", "r") as f:
            st.session_state.fork_toml = f.read()


@st.dialog("Fork Theme")
def show_fork_dialog():
    """Edit a copy of the current theme and apply it as a custom theme."""
    st.markdown("Customize the name and theme below, then save to apply it.")
    # Inputs are driven purely by their keys (seeded in seed_fork_inputs) so
    # edits persist across dialog reruns without a value=/key= conflict.
    name = st.text_input("Name", key="fork_name")
    toml_text = st.text_area("Theme", height=400, key="fork_toml")

    if st.button("Save", type="primary", icon=":material/save:"):
        # Validate the edited TOML before committing.
        try:
            theme_loader.parse_theme_toml(toml_text)
        except (tomllib.TOMLDecodeError, ValueError) as exc:
            st.error(f"Invalid theme: {exc}")
            return

        st.session_state.custom_theme_name = name
        st.session_state.custom_theme_toml = toml_text
        st.session_state.selected_theme = CUSTOM_THEME_SENTINEL
        st.session_state["_pending_theme_sync"] = True
        st.query_params["theme"] = CUSTOM_THEME_SENTINEL
        st.query_params["theme-value"] = encode_theme_value(name, toml_text)
        st.rerun()


if st.sidebar.button(
    "Install Theme", icon=":material/download:", width="stretch"
):
    show_install_dialog()

if st.sidebar.button(
    "Fork Theme",
    icon=":material/fork_right:",
    type="tertiary",
    width="stretch",
):
    seed_fork_inputs()
    show_fork_dialog()

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

if st.session_state.selected_theme == CUSTOM_THEME_SENTINEL:
    current_theme_label = f"{st.session_state.get('custom_theme_name', 'Custom')} (Custom)"
else:
    current_theme_label = format_theme_name(st.session_state.selected_theme)

st.sidebar.caption(f"Current theme: **{current_theme_label}**")
