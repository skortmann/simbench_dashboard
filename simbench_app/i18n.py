"""Minimal UI translation layer (English source text -> German).

Convention: every user-visible string is written in English in the code and
wrapped in :func:`tr`. German translations live in ``simbench_app/locales/de_*.py``
modules that each define a dict ``DE = {english: german}``. A missing entry
falls back to the English text, so the app never breaks - the coverage check in
``tests/translation_check.py`` lists what is still untranslated.

Rules:

* ``tr`` takes a *string literal* so that the checker can find it. Dynamic
  parts use ``str.format`` placeholders: ``tr("Loaded {n} buses", n=len(net.bus))``.
  Never build the argument with an f-string or concatenation.
* Placeholders must be identical in the English and German text.
* Technical identifiers (pandapower column names such as ``vm_pu``, SimBench
  codes, units like MW/kV, algorithm names) are not translated.
* Never call ``tr`` inside ``st.cache_data`` / ``st.cache_resource`` functions
  (the cached text would stay in the language of the first call).
"""

from __future__ import annotations

import importlib
import pkgutil

import streamlit as st

LANGS = {"en": "English", "de": "Deutsch"}
DEFAULT_LANG = "en"
KEY_LANG = "_lang"           # session-state key holding the active language
_WIDGET_KEY = "lang_widget"  # key of the sidebar selectbox

_DE: dict[str, str] = {}


def _load_catalogs() -> None:
    """Import every ``locales/de_*.py`` module and merge its ``DE`` dict."""
    from . import locales

    for mod in pkgutil.iter_modules(locales.__path__):
        if mod.name.startswith("de_"):
            module = importlib.import_module(f"{locales.__name__}.{mod.name}")
            _DE.update(getattr(module, "DE", {}))


_load_catalogs()


def get_lang() -> str:
    """Active UI language code (``"en"`` or ``"de"``)."""
    return st.session_state.get(KEY_LANG, DEFAULT_LANG)


def tr(text: str, **fmt) -> str:
    """Translate an English source string into the active language.

    ``fmt`` placeholders are applied with ``str.format`` after translation.
    """
    out = _DE.get(text, text) if get_lang() == "de" else text
    return out.format(**fmt) if fmt else out


def translations() -> dict[str, str]:
    """All registered German translations (for the coverage check)."""
    return _DE


def language_selector() -> str:
    """Render the sidebar language switch and return the active language."""
    ss = st.session_state
    ss.setdefault(KEY_LANG, DEFAULT_LANG)

    def _on_change() -> None:
        ss[KEY_LANG] = ss[_WIDGET_KEY]

    codes = list(LANGS)
    st.sidebar.selectbox(
        "Language / Sprache", codes, index=codes.index(ss[KEY_LANG]),
        format_func=LANGS.get, key=_WIDGET_KEY, on_change=_on_change)
    return ss[KEY_LANG]
