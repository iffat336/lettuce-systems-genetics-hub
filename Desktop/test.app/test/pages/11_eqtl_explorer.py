"""eQTL explorer page."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import run_eqtl_scan
from src.lettuce_project.workflow_io import get_active_or_synthetic


st.title("eQTL Explorer")
st.caption("Association mapping across SNP markers and transcript abundance")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    min_abs_effect = st.slider("Min absolute effect", 0.01, 0.25, 0.05, 0.01)
    top_n = st.slider("Top hits shown", 10, 250, 40, 10)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")
results = run_eqtl_scan(data.genotype, data.expression, min_abs_effect=min_abs_effect)

if results.empty:
    st.warning("No associations found at the chosen effect-size threshold.")
    st.stop()

results["neg_log10_p"] = -np.log10(results["p_value"].clip(lower=1e-300))
sig_hits = (results["fdr"] < 0.05).sum()

c1, c2, c3 = st.columns(3)
c1.metric("Tested pairs", f"{len(results):,}")
c2.metric("FDR < 0.05 hits", int(sig_hits))
c3.metric("Best p-value", f"{results['p_value'].min():.2e}")

plot_df = results.head(top_n).copy()
plot_df["gene_snp"] = plot_df["gene"] + " | " + plot_df["snp"]

fig = px.scatter(
    plot_df,
    x="snp",
    y="neg_log10_p",
    color="effect_size",
    hover_data=["gene", "r2", "fdr"],
    title="Top eQTL signals",
    color_continuous_scale="RdBu",
)
fig.update_layout(height=480, xaxis_title="Marker", yaxis_title="-log10(p)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Top eQTL Table")
st.dataframe(
    results.head(top_n)[["gene", "snp", "effect_size", "r2", "p_value", "fdr"]],
    use_container_width=True,
)

selected_gene = st.selectbox("Inspect one gene", data.expression.columns.tolist(), index=0)
gene_hits = results[results["gene"] == selected_gene].sort_values("p_value").head(15)

st.subheader(f"Best markers for {selected_gene}")
if gene_hits.empty:
    st.write("No marker passed the current filter.")
else:
    bar = px.bar(
        gene_hits,
        x="snp",
        y="effect_size",
        color="fdr",
        title=f"Marker effects for {selected_gene}",
        color_continuous_scale="Viridis_r",
    )
    bar.update_layout(height=420)
    st.plotly_chart(bar, use_container_width=True)
    st.dataframe(gene_hits, use_container_width=True)
