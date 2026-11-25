"""Translation coverage: every ``tr("...")`` literal must have a German entry.

Run ``uv run python tests/translation_check.py`` to print the missing
strings; ``missing_translations()`` is also used by ``smoke_test.py``.
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

SOURCE_DIRS = ["pages", "simbench_app"]
SOURCE_FILES = ["streamlit_app.py"]


def _literals_in(path: str) -> list[tuple[str, int]]:
    """String literals passed as first argument to ``tr(...)`` in a file."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "tr" and node.args):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                out.append((arg.value, node.lineno))
            else:
                out.append((f"<NON-LITERAL tr() argument at line {node.lineno}>",
                            node.lineno))
    return out


def _constant_texts() -> list[tuple[str, str]]:
    """Texts stored in module-level constants and translated on display."""
    from simbench_app import (config, data_loading, explanations,
                              powerflow, profiles, scenarios)
    items: list[tuple[str, str]] = []
    for name, d in (("explanations.TEXTS", explanations.TEXTS),
                    ("powerflow.ALGORITHMS", powerflow.ALGORITHMS),
                    ("powerflow.BACKENDS", powerflow.BACKENDS),
                    ("profiles.PROFILE_GROUPS", profiles.PROFILE_GROUPS),
                    ("scenarios.PLANNING_CASES", scenarios.PLANNING_CASES),
                    ("data_loading.SCENARIO_MEANING", data_loading.SCENARIO_MEANING)):
        items += [(name, v) for v in d.values()]
    items += [("data_loading.CODE_PART_LABELS", v)
              for v in data_loading.CODE_PART_LABELS]
    for label, (_, _, expl) in config.VOLTAGE_BAND_PRESETS.items():
        items += [("config.VOLTAGE_BAND_PRESETS", label),
                  ("config.VOLTAGE_BAND_PRESETS", expl)]
    return items


def missing_translations() -> list[str]:
    """Descriptions of every English text without a German translation."""
    from simbench_app import i18n

    de = i18n.translations()
    missing = []
    files = [os.path.join(ROOT, f) for f in SOURCE_FILES]
    for d in SOURCE_DIRS:
        for dirpath, _, names in os.walk(os.path.join(ROOT, d)):
            files += [os.path.join(dirpath, n) for n in names if n.endswith(".py")]
    for path in sorted(files):
        for text, line in _literals_in(path):
            if text.startswith("<NON-LITERAL") or text not in de:
                missing.append(f"{os.path.relpath(path, ROOT)}:{line}: {text[:90]!r}")
    for where, text in _constant_texts():
        if text not in de:
            missing.append(f"{where}: {text[:90]!r}")
    # placeholder consistency
    import string
    fmt = string.Formatter()

    def fields(s: str) -> set[str]:
        return {f for _, f, _, _ in fmt.parse(s) if f}
    for en, de_text in de.items():
        try:
            if fields(en) != fields(de_text):
                missing.append(f"placeholder mismatch: {en[:70]!r}")
        except ValueError:
            missing.append(f"invalid format string: {en[:70]!r}")
    return missing


if __name__ == "__main__":
    problems = missing_translations()
    print("\n".join(problems) if problems else "All strings translated.")
    print(f"\n{len(problems)} problem(s)")
