# SimBench Network Analysis Platform

A multi-page [Streamlit](https://streamlit.io) platform for **scientific
inspection and analysis of [SimBench](https://simbench.de) benchmark networks**
with [pandapower](https://www.pandapower.org): transparent, reproducible and
explainable — numbers are always accompanied by what they mean.

## Features

| Page | Purpose |
|---|---|
| **Home** | Select any of the 246 SimBench codes via cascading filters (or load a small example network) with code metadata |
| **01 Network Overview** | Element inventory, voltage levels, installed capacities, line/transformer statistics, data completeness, consistency checks |
| **02 Element Inspector** | Filterable pandapower element tables with units, column presets and CSV downloads |
| **03 Topology Visualization** | Interactive Plotly network map (geodata or automatic layout fallback), colouring by voltage level / voltage magnitude / line loading, bus-neighbourhood inspector |
| **04 Power Flow Analysis** | Configurable AC power flow incl. voltage band presets (EN 50160 / planning band) and voltage rise by generation (solver backend: lightsim2grid with automatic fallback to pandapower, algorithm, initialisation, Q-limits), voltage profile, branch loading, power balance, limit violations against configurable thresholds |
| **05 Result Diagnostics** | Severity-ranked structural and result checks with plain-language explanations |
| **06 Profiles & Time Series** | Full-year 15-minute SimBench profiles and statistics, an **annual time-series power flow** (duration curves, day × hour heat map, critical days and elements) and a capped demonstrative day simulation |
| **07 Modify Network** | What-if changes (load scaling, storage placement) on a session working copy, with a modification log |
| **08 Scenario Comparison** | Planning cases (hL/hW/lW) and development scenarios 0/1/2 of the same grid side by side |
| **09 N-1 Security** | Single outage of every line/transformer, supply-loss and violation classification, restoration by closing open points |
| **10 Export & Report** | CSV/JSON/pickle/Excel exports and a Markdown analysis report with full reproducibility information |

## Local setup

Requires Python ≥ 3.12.

With [uv](https://docs.astral.sh/uv/) (recommended, uses the lock file):

```bash
uv sync
uv run streamlit run streamlit_app.py
```

With plain pip:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open http://localhost:8501.

## Deployment on Streamlit Community Cloud

1. Push this repository to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app
   pointing at the repository with **`streamlit_app.py`** as the entrypoint.
3. Dependencies are picked up from `requirements.txt` automatically; no
   `packages.txt` (system packages) is needed.

Notes for shared hosting: network loading is cached (`st.cache_data`,
bounded to 3 networks); the time-series demonstration is capped in steps and
network size. Very large SimBench grids (complete HV datasets) may exceed
small-instance memory — the app reports this gracefully.

## Architecture

```
streamlit_app.py     # entrypoint: Home + network selection
pages/               # thin UI pages (01–08), layout and interaction only
simbench_app/        # reusable analysis layer
  config.py            session-state keys, defaults, thresholds
  data_loading.py      SimBench code handling, cached loading
  network_analysis.py  summary statistics & consistency checks
  powerflow.py         PF execution, result summaries, violations
  validation.py        severity-ranked diagnostics
  visualization.py     Plotly topology figures, coordinate handling
  profiles.py          time-series access & capped TS power flow
  tables.py            units, column presets, table filtering
  explanations.py      explainability texts
  report.py            Markdown report generation
  utils.py             session helpers, environment info, export bytes
tests/smoke_test.py  # validation script (module + page execution checks)
```

Pages communicate exclusively through `st.session_state` keys defined in
`simbench_app/config.py` (`net`, `sb_code`, `pf_result`, `thresholds`,
`modification_log`).

## Validation

```bash
uv run python tests/smoke_test.py   # loads a network, runs PF, executes all pages
python -m compileall .              # syntax check
```

## Scientific scope and limitations

Results stem from a **static, balanced AC power flow**: no dynamics, no
asymmetry, no protection modelling; loads and generators are PQ set-points.
SimBench grids are synthetic benchmarks — realistic, but not images of
specific real networks, and their geodata is schematic. See the in-app
explanations for interpretation guidance.

**References:** Meinecke et al., *SimBench — A Benchmark Dataset of Electric
Power Systems to Compare Innovative Solutions Based on Power Flow Analysis*,
Energies 13(12), 2020. Thurner et al., *pandapower — An Open-Source Python
Tool for Convenient Modeling, Analysis, and Optimization of Electric Power
Systems*, IEEE Trans. Power Systems 33(6), 2018.
