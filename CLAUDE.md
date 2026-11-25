# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multi-page Streamlit platform for scientific inspection and analysis of SimBench power networks (built on `simbench` and `pandapower`). Requires Python ≥ 3.12; dependencies are managed with `uv` locally and `requirements.txt` for Streamlit Community Cloud deployment (deliberately slim — no `pandapower[all]`).

## Commands

```bash
uv sync                              # Install dependencies
uv run streamlit run streamlit_app.py  # Run the app (http://localhost:8501)
uv run python tests/smoke_test.py    # Validation: modules, network load, PF, all pages via AppTest
python -m compileall .               # Syntax check
```

There is no pytest/linter setup; `tests/smoke_test.py` is a plain script with asserts.

## Architecture

`streamlit_app.py` is the entrypoint/router (language switch + `st.navigation`, so menu titles are translatable); `pages/00_Home.py` (network selection) and `pages/01_…10_….py` are thin UI layers. All analysis logic lives in the `simbench_app/` package — when adding features, put computation there and keep pages to layout/interaction.

Pages share state exclusively through `st.session_state` keys defined in `simbench_app/config.py`: `net` (mutable working copy), `sb_code`, `pf_result` (a `powerflow.PowerFlowResult`; numerical results live in `net.res_*` per pandapower convention), `thresholds`, `modification_log`. Every page guards with `utils.require_network()`. Loading a new network or modifying the current one must invalidate `pf_result`.

Non-obvious constraints:
- `data_loading.load_network` uses `st.cache_data` (returns a fresh copy per call, so session mutations never corrupt the cache; `max_entries=3` bounds memory).
- pandapower ≥ 3.0 stores geodata as GeoJSON strings in `net.bus.geo` (no `bus_geodata` table). `visualization.bus_coordinates` parses these and falls back to a deterministic networkx spring layout.
- SimBench profiles: `net.profiles` is keyed `load`/`renewables`/`powerplants`/`storage` with a `time` column and `<name>_pload/_qload` columns at 15-min resolution (96 steps/day). The time-series demo uses `sb.get_absolute_values` on a deep copy and is capped via `config.TIMESERIES_MAX_STEPS/_MAX_BUSES`.
- Exports are generated in memory (`utils.net_to_bytes` uses a tempdir for pickle/Excel) — never write to the server CWD.
- Power flow runs through `powerflow.run_power_flow(backend=...)`: lightsim2grid (C++ Newton-Raphson) is tried first and falls back to native pandapower on `NotImplementedError` (non-NR algorithm, voltage-dependent loads, several ext_grids, …); the backend actually used is stored in `PowerFlowResult.backend`. `pandapower[all]` must not be used — it pins lightsim2grid <0.14.
- Annual time series (`profiles.run_annual_timeseries`) uses `pp.timeseries.run_timeseries` + `sb.apply_const_controllers`, chunked, with lightsim2grid (~8 ms/step). pandapower keeps *stale* results on divergence, so convergence is recorded via a custom `output_writer_fct`, never inferred from the output. `lightsim2grid.TimeSerie/ContingencyAnalysis/ScenarioSweep` need a grid2op env and are not used.
- UI language (English/German): every user-visible string is `tr("English literal")` from `simbench_app.i18n`; German lives in `simbench_app/locales/de_*.py` (`DE = {english: german}`), missing entries fall back to English. Use `tr("... {n}", n=...)` for dynamic parts (never f-strings), never `tr` inside `st.cache_data` functions, keep logic keys English and translate on display. `tests/translation_check.py` (also run by the smoke test) fails on untranslated literals, non-literal `tr()` arguments and placeholder mismatches. To test a page in German under AppTest set `at.session_state["_lang"] = "de"`.
- Report generation (`report.py`) needs `tabulate` for `DataFrame.to_markdown`.
- Streamlit ≥ 1.58: use `width='stretch'`, not the removed `use_container_width=True`.

When running pages under `streamlit.testing.v1.AppTest`, insert the repo root into `sys.path` first (pages import `simbench_app`, and AppTest makes the page the main script).
