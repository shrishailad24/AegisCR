import importlib
import streamlit as st

def get_translation(lang_code: str, key: str) -> str:
    """
    Fetch a translation key for the specified language.
    Falls back to English ('en') if the key or language is missing.
    """
    try:
        module = importlib.import_module(f"translations.{lang_code}")
        translations = getattr(module, "TRANSLATIONS", {})
    except ImportError:
        translations = {}

    if key in translations:
        return translations[key]
    
    try:
        en_module = importlib.import_module("translations.en")
        en_translations = getattr(en_module, "TRANSLATIONS", {})
        return en_translations.get(key, key)
    except ImportError:
        return key

def t(key: str) -> str:
    """Helper function to get translation based on session state."""
    lang = st.session_state.get("app_language", "en")
    return get_translation(lang, key)
