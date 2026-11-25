"""SimBench code handling and cached network loading."""

from __future__ import annotations

import streamlit as st
import simbench as sb

from .i18n import tr

#: Alias for translating texts held in module constants (not literal ``tr`` calls).
tr_const = tr

#: Positional meaning of the dash-separated SimBench code parts.
CODE_PART_LABELS = [
    "Version", "Grid level", "Urbanisation / type", "LV subnet",
    "Scenario", "Switch variant",
]

#: Meaning of the scenario digit in SimBench codes.
SCENARIO_MEANING = {
    "0": "base state — present-day situation (limits kept, also under n-1)",
    "1": "development scenario labelled 2024 — more distributed generation",
    "2": "development scenario labelled 2034 — much more generation, "
         "heat pumps and e-mobility",
}


@st.cache_data(show_spinner=False)
def list_codes() -> list[str]:
    """All available SimBench grid codes (cached for the session)."""
    return list(sb.collect_all_simbench_codes())


def split_codes(codes: list[str]) -> list[list[str]]:
    """Split codes into their dash-separated components."""
    return [c.split("-") for c in codes]


def options_for(parts: list[list[str]], idx: int, filters: dict[int, str]) -> list[str]:
    """Unique values available for code component ``idx`` given fixed components.

    ``filters`` maps component index -> already selected value, implementing
    the cascading selection (each choice narrows the next).
    """
    vals = [p[idx] for p in parts if len(p) > idx
            and all(len(p) > i and p[i] == v for i, v in filters.items())]
    return sorted(set(vals))


def code_labels() -> dict[str, str]:
    """Display labels (active language) for the keys of :func:`describe_code`."""
    return {
        "SimBench code": tr("SimBench code"),
        "Version": tr("Version"),
        "Grid level": tr("Grid level"),
        "Urbanisation / type": tr("Urbanisation / type"),
        "LV subnet": tr("LV subnet"),
        "Scenario": tr("Scenario"),
        "Switches": tr("Switches"),
    }


def describe_code(code: str) -> dict[str, str]:
    """Human-readable metadata for a SimBench code.

    The dict *keys* are stable English identifiers (see :func:`code_labels` for
    their translated display labels); the *values* are in the active language.
    """
    p = code.split("-")
    info = {
        "SimBench code": code,
        "Version": p[0] if len(p) > 0 else "?",
        "Grid level": p[1] if len(p) > 1 else "?",
        "Urbanisation / type": p[2] if len(p) > 2 else "?",
        "LV subnet": p[3] if len(p) > 3 and p[3] else tr("— (none)"),
        "Scenario": "?",
        "Switches": (tr("modelled explicitly") if code.endswith("-sw")
                     else tr("not modelled")),
    }
    if len(p) > 4 and p[4] in SCENARIO_MEANING:
        info["Scenario"] = tr("{code}: {meaning}", code=p[4],
                              meaning=tr_const(SCENARIO_MEANING[p[4]]))
    return info


@st.cache_data(show_spinner="Loading SimBench network — this may take a moment …",
               max_entries=3)
def load_network(code: str):
    """Load a SimBench network by code.

    ``st.cache_data`` keeps the parsed network in cache and hands out a fresh
    copy on every call, so user modifications never corrupt the cached
    original. ``max_entries`` bounds memory on Streamlit Community Cloud.
    """
    return sb.get_simbench_net(code)
