"""Entrypoint: language switch and page navigation.

Pages live in ``pages/`` and are registered explicitly with ``st.navigation``
so that the menu titles can be translated (file names cannot).
"""

import streamlit as st

from simbench_app import i18n
from simbench_app.i18n import tr

st.set_page_config(page_title="SimBench Analysis Platform", page_icon="⚡",
                   layout="wide")
i18n.language_selector()

PAGES = [
    ("pages/00_Home.py", tr("Home"), "🏠"),
    ("pages/01_Network_Overview.py", tr("Network Overview"), "📊"),
    ("pages/02_Element_Inspector.py", tr("Element Inspector"), "🔍"),
    ("pages/03_Topology_Visualization.py", tr("Topology Visualization"), "🗺️"),
    ("pages/04_Power_Flow_Analysis.py", tr("Power Flow Analysis"), "⚡"),
    ("pages/05_Result_Diagnostics.py", tr("Result Diagnostics"), "🩺"),
    ("pages/06_Profiles_Time_Series.py", tr("Profiles & Time Series"), "📈"),
    ("pages/07_Modify_Network.py", tr("Modify Network"), "⚙️"),
    ("pages/08_Scenario_Comparison.py", tr("Scenario Comparison"), "🔀"),
    ("pages/09_N1_Security.py", tr("N-1 Security"), "🛡️"),
    ("pages/10_Export_and_Report.py", tr("Export & Report"), "📤"),
]

st.navigation([
    st.Page(path, title=title, icon=icon, default=(i == 0))
    for i, (path, title, icon) in enumerate(PAGES)
]).run()
