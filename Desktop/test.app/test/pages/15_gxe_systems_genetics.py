"""Genotype-by-environment systems genetics page."""
from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import (
    run_environment_eqtl_scan,
    summarize_eqtl_stability,
)
from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label


st.title("GxE Systems Genetics")
st.caption("Environment-dependent regulatory variation across lettuce habitats")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    top_n = st.slider("Top stable eQTLs", 10, 80, 25, 5)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")
st.caption(f"Mode: {get_data_mode_label(source)}")
env_eqtl = run_environment_eqtl_scan(data.genotype, data.expression, data.metadata)
stability = summarize_eqtl_stability(env_eqtl)

if env_eqtl.empty or stability.empty:
    st.warning("No environment-specific associations found for this seed.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Habitat groups", data.metadata["habitat"].nunique())
c2.metric("Population groups", data.metadata["population"].nunique())
c3.metric("Cross-habitat eQTL candidates", int((stability["habitats_detected"] >= 2).sum()))

st.subheader("Stable vs environment-specific regulatory loci")
plot_df = stability.head(top_n).copy()
fig = px.scatter(
    plot_df,
    x="mean_abs_effect",
    y="habitats_detected",
    color="effect_sign_consistent",
    hover_data=["gene", "snp", "best_p"],
    title="eQTL stability across habitats",
)
fig.update_layout(height=460)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Scatter interpretation: points higher on the y-axis appear in more habitats, indicating stronger cross-environment stability. "
    "Higher x-values indicate stronger average effect size."
)

st.subheader("Top stability table")
st.dataframe(stability.head(top_n), use_container_width=True)
st.caption(
    "Stability table: prioritize candidates with high habitats_detected and strong mean_abs_effect. "
    "These are robust targets for downstream validation."
)

st.subheader("Environment-level hits")
habitat_filter = st.selectbox("Filter habitat", sorted(env_eqtl["habitat"].unique()))
st.dataframe(
    env_eqtl[env_eqtl["habitat"] == habitat_filter].sort_values("p_value").head(60),
    use_container_width=True,
)
st.caption(
    "Habitat view: this table isolates environment-specific signals. "
    "Compare habitats to identify context-dependent regulators."
)

st.info(
    "Interview framing: this mirrors his interest in gene expression variation across "
    "different environments and identification of robust vs context-dependent regulators."
)
