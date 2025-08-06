# SimBench Dashboard

A Streamlit-based dashboard for inspecting, visualizing and exporting SimBench networks.

## Prerequisites

- **Python** ≥ 3.12  
- **Git** (optional, to clone the repo)  
- **uv** CLI (used to scaffold the project)

## 1. Install the `uv` CLI

If you haven’t already got `uv`, install it with pip:

```bash
pip install uv
uv sync
```

## 2. Project structure

```
simbench-dashboard/
├── streamlit_app.py         # Home page: network selection
├── pages/
│   ├── 1_Inspect_Data.py    # Raw data tables & charts
│   ├── 2_Visualize_Network.py  # Plotly‐based network plots
│   └── 3_Modify_and_Save.py # Scale & export network
└── README.md                # You are here
```

## 3. Run the dashboard

Run in terminal: 

streamlit run streamlit_app.py

Then open the URL shown (usually http://localhost:8501) in your browser.