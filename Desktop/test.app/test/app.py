"""Lettuce Systems Genetics Hub - curated multipage entrypoint."""
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Lettuce Systems Genetics Hub",
    page_icon="L",
    layout="wide",
)

if hasattr(st, "navigation"):
    overview = st.Page("pages/10_project_overview.py", title="Project Overview", icon=":material/home:")
    eqtl = st.Page("pages/11_eqtl_explorer.py", title="eQTL Explorer", icon=":material/query_stats:")
    network = st.Page("pages/12_network_biology.py", title="Network Biology", icon=":material/hub:")
    ai = st.Page("pages/13_ai_trait_predictor.py", title="AI Trait Predictor", icon=":material/psychology:")
    gxe = st.Page("pages/15_gxe_systems_genetics.py", title="GxE Systems Genetics", icon=":material/lan:")
    microbiome = st.Page("pages/16_meta_biome_integration.py", title="Meta-Biome Integration", icon=":material/biotech:")
    methods = st.Page("pages/14_methods_reproducibility.py", title="Methods", icon=":material/lab_profile:")
    fit = st.Page("pages/17_lab_fit_pain_points.py", title="Lab Fit and Pain Points", icon=":material/handshake:")
    supervisors = st.Page("pages/18_supervisor_alignment.py", title="Supervisor Alignment", icon=":material/groups:")
    workflow = st.Page("pages/19_workflow_upload_download.py", title="Workflow Upload/Download", icon=":material/upload_file:")
    robustness = st.Page("pages/20_model_robustness.py", title="Model Robustness", icon=":material/monitoring:")
    validation = st.Page("pages/21_candidate_validation_plan.py", title="Candidate Validation Plan", icon=":material/fact_check:")

    navigation = st.navigation(
        {
            "Research Scope": [overview],
            "Analysis Modules": [eqtl, network, ai, gxe, microbiome, robustness],
            "Validation Design": [validation],
            "Project Fit": [methods, fit, supervisors],
            "Data Exchange": [workflow],
        }
    )
    navigation.run()
else:
    st.title("Lettuce Systems Genetics Hub")
    st.caption("Streamlit version is too old for curated page navigation.")
    st.info("Upgrade Streamlit to >= 1.36 and run this app from app.py.")
