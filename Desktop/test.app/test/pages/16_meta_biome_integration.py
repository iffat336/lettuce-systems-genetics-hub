"""Meta-biome integration page for host-microbiome analysis."""
from pathlib import Path
import sys

import numpy as np
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import (
    build_species_cooccurrence_edges,
    host_microbiome_links,
)
from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label


st.title("Meta-Biome Integration")
st.caption("Species abundance patterns and host transcript links across habitats")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    coocc_threshold = st.slider("Species co-occurrence threshold", 0.20, 0.80, 0.35, 0.05)
    top_links = st.slider("Top host-microbe links", 20, 120, 50, 10)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")
st.caption(f"Mode: {get_data_mode_label(source)}")
edges = build_species_cooccurrence_edges(data.microbiome, threshold=coocc_threshold)
links = host_microbiome_links(data.expression, data.microbiome, top_n=top_links)

c1, c2, c3 = st.columns(3)
c1.metric("Microbial species", data.microbiome.shape[1])
c2.metric("Co-occurrence edges", len(edges))
c3.metric("Host-microbe links", len(links))

st.subheader("Habitat-level species composition")
composition = (
    data.microbiome.join(data.metadata[["habitat"]])
    .groupby("habitat")
    .mean()
    .T.reset_index()
    .rename(columns={"index": "species"})
)
comp_long = composition.melt(id_vars="species", var_name="habitat", value_name="mean_abundance")
fig = px.bar(
    comp_long,
    x="species",
    y="mean_abundance",
    color="habitat",
    title="Mean species abundance by habitat",
)
fig.update_layout(height=460, xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Composition interpretation: taller bars mean higher average abundance in that habitat. "
    "Large habitat shifts suggest environment-sensitive microbial groups."
)

st.subheader("Top host transcript vs species links")
if links.empty:
    st.write("No links detected.")
else:
    heat_df = links.copy()
    heat_df["pair"] = heat_df["gene"] + " <> " + heat_df["species"]
    scatter = px.scatter(
        heat_df,
        x="gene",
        y="species",
        color="corr",
        size=heat_df["abs_corr"] * 22.0,
        color_continuous_scale="RdBu",
        title="Host-microbiome association map",
    )
    scatter.update_layout(height=520)
    st.plotly_chart(scatter, use_container_width=True)
    st.dataframe(links.sort_values("abs_corr", ascending=False), use_container_width=True)
    st.caption(
        "Association map: larger circles indicate stronger host-microbe correlation. "
        "Red/blue colors show positive/negative association direction."
    )

if not edges.empty:
    st.subheader("Species co-occurrence edge list")
    st.dataframe(edges.sort_values("weight", key=np.abs, ascending=False), use_container_width=True)
    st.caption(
        "Co-occurrence table: strong positive/negative weights indicate consistent species coupling or exclusion. "
        "Use top edges to define candidate ecological modules."
    )

st.info(
    "Interview framing: this page addresses his near-future goal to integrate "
    "gene-expression genetics with meta-biome sequencing and species co-occurrence analysis."
)
