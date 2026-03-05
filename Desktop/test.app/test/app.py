"""Lettuce Systems Genetics Hub - Streamlit multipage entrypoint."""
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Lettuce Systems Genetics Hub",
    page_icon="L",
    layout="wide",
)

overview = st.Page("pages/10_project_overview.py", title="Project Overview", icon=":material/home:")
eqtl = st.Page("pages/11_eqtl_explorer.py", title="eQTL Explorer", icon=":material/query_stats:")
network = st.Page("pages/12_network_biology.py", title="Network Biology", icon=":material/hub:")
ai = st.Page("pages/13_ai_trait_predictor.py", title="AI Trait Predictor", icon=":material/psychology:")
methods = st.Page("pages/14_methods_reproducibility.py", title="Methods", icon=":material/lab_profile:")
gxe = st.Page("pages/15_gxe_systems_genetics.py", title="GxE Systems Genetics", icon=":material/lan:")
microbiome = st.Page("pages/16_meta_biome_integration.py", title="Meta-Biome Integration", icon=":material/biotech:")
fit = st.Page("pages/17_lab_fit_pain_points.py", title="Lab Fit and Pain Points", icon=":material/handshake:")

navigation = st.navigation(
    {
        "Research Scope": [overview],
        "Analysis Modules": [eqtl, network, ai, gxe, microbiome],
        "Project Fit": [methods, fit],
    }
)

navigation.run()
