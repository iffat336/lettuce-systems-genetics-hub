"""Upload/download page for full systems-genetics workflow exchange."""
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.workflow_io import (
    build_procedure_bundle,
    clear_active_project_data,
    get_active_or_synthetic,
    parse_uploaded_bundle,
    set_active_project_data,
)

st.title("Workflow Upload/Download")
st.caption("Load your own matrices and export the complete analysis procedure package")

with st.sidebar:
    seed = st.number_input("Fallback synthetic seed", min_value=1, max_value=9999, value=42, step=1)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")

st.subheader("1) Upload full input bundle")
st.markdown(
    "Upload a `.zip` containing `genotype.csv`, `expression.csv`, `metadata.csv`, and `microbiome.csv` "
    "(optional: `causal_map.csv`)."
)
uploaded = st.file_uploader("Upload workflow bundle (.zip)", type=["zip"])
if uploaded is not None:
    try:
        parsed = parse_uploaded_bundle(uploaded.getvalue())
        set_active_project_data(parsed, f"Uploaded: {uploaded.name}")
        st.success("Upload validated and activated across the app.")
        st.rerun()
    except Exception as exc:
        st.error(f"Upload failed: {exc}")

col1, col2 = st.columns(2)
with col1:
    if st.button("Use synthetic demo data"):
        clear_active_project_data()
        st.success("Switched to synthetic mode.")
        st.rerun()
with col2:
    st.write("")

st.subheader("2) Download whole procedure package")
st.markdown(
    "This export includes all input tables and all computed outputs (eQTL, GxE stability, "
    "network edges, host-microbiome links, AI metrics/importances)."
)
bundle_bytes = build_procedure_bundle(data=data, seed=seed)
st.download_button(
    label="Download whole procedure (.zip)",
    data=bundle_bytes,
    file_name="lettuce_systems_genetics_workflow.zip",
    mime="application/zip",
    use_container_width=True,
)

st.subheader("Current data snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Samples", data.genotype.shape[0])
c2.metric("SNPs", data.genotype.shape[1])
c3.metric("Genes", data.expression.shape[1])
c4.metric("Microbial species", data.microbiome.shape[1])
