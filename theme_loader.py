"""Session-level theme loader using monkey-patching.

This module provides per-session theme switching without modifying the
shared config.toml file. Each browser session can have its own theme.
"""

import tomllib
from contextvars import ContextVar

import streamlit as st
from streamlit import config
from streamlit.runtime.app_session import AppSession
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Store themes per session (using session ID as key)
_SESSION_THEMES: dict[str, dict] = {}
_PATCHED = False

# Context variable to track which session is currently creating a NewSession message
_CURRENT_SESSION_ID: ContextVar[str | None] = ContextVar("current_session_id", default=None)

# Nested sections that should be handled separately
_NESTED_SECTIONS = {"sidebar", "light", "dark"}


def _get_current_session_id() -> str | None:
    """Get the current session ID from script context or context variable."""
    # First try script run context (available during script execution)
    ctx = get_script_run_ctx()
    if ctx:
        return ctx.session_id
    # Fall back to context variable (set during NewSession creation)
    return _CURRENT_SESSION_ID.get()


def _get_theme_for_section(theme_data: dict, section: str) -> dict | None:
    """Get theme options for a specific section.

    Args:
        theme_data: The full theme dict (may include nested sections).
        section: The section to get ("theme" or "theme.sidebar" etc).

    Returns:
        Dict of options for that section, or None if not found.
    """
    if section == "theme":
        # Return top-level options without nested sections
        return {k: v for k, v in theme_data.items() if k not in _NESTED_SECTIONS}

    # Handle nested sections like "theme.sidebar"
    if section.startswith("theme."):
        subsection = section[6:]  # Remove "theme." prefix
        if subsection in theme_data and isinstance(theme_data[subsection], dict):
            return theme_data[subsection]

    return None


def _apply_patch():
    """Apply the monkey-patch to intercept theme config loading."""
    global _PATCHED
    if _PATCHED:
        return

    # Patch 1: Wrap _create_new_session_message to set session ID context
    _original_create_msg = AppSession._create_new_session_message

    def _patched_create_msg(self, *args, **kwargs):
        # Set the session ID in context before creating the message
        token = _CURRENT_SESSION_ID.set(self._session_data.session_id)
        try:
            return _original_create_msg(self, *args, **kwargs)
        finally:
            _CURRENT_SESSION_ID.reset(token)

    AppSession._create_new_session_message = _patched_create_msg

    # Patch 2: Intercept get_options_for_section for theme sections
    _original_get_options = config.get_options_for_section

    def _patched_get_options(section: str):
        # Only intercept theme-related sections
        if section == "theme" or section.startswith("theme."):
            session_id = _get_current_session_id()
            if session_id and session_id in _SESSION_THEMES:
                theme_data = _SESSION_THEMES[session_id]
                result = _get_theme_for_section(theme_data, section)
                if result is not None:
                    return result

        return _original_get_options(section)

    config.get_options_for_section = _patched_get_options
    _PATCHED = True


def load_theme(theme_path: str) -> bool:
    """Load per-session theme from a TOML file.

    Args:
        theme_path: Path to the theme TOML file.

    Returns:
        True if theme was loaded and rerun triggered, False if already loaded.
    """
    _apply_patch()

    ctx = get_script_run_ctx()
    if ctx is None:
        return False

    # Load theme data (tomllib requires binary mode)
    with open(theme_path, "rb") as f:
        theme_data = tomllib.load(f).get("theme", {})

    # Check if this is a new theme for this session
    current_theme = _SESSION_THEMES.get(ctx.session_id)
    if current_theme == theme_data:
        return False

    # Update session-specific theme
    _SESSION_THEMES[ctx.session_id] = theme_data
    st.rerun()
    return True


def load_theme_by_name(theme_name: str, themes_dir: str) -> bool:
    """Load per-session theme by name from a themes directory.

    Args:
        theme_name: Name of the theme (without .toml extension).
        themes_dir: Path to the directory containing theme files.

    Returns:
        True if theme was loaded and rerun triggered, False if already loaded.
    """
    theme_path = f"{themes_dir}/{theme_name}.toml"
    return load_theme(theme_path)


def get_current_session_theme_data() -> dict | None:
    """Get the current session's theme data."""
    ctx = get_script_run_ctx()
    if ctx is None:
        return None
    return _SESSION_THEMES.get(ctx.session_id)
