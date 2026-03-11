"""Network biology page based on co-expression patterns."""
from pathlib import Path
import sys

import numpy as np
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import (
    build_coexpression_edges,
    summarize_network,
)
from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label


st.title("Network Biology")
st.caption("Co-expression modules and hub-gene prioritization")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    threshold = st.slider("Absolute correlation threshold", 0.30, 0.90, 0.65, 0.05)
    top_hubs = st.slider("Hub genes shown", 5, 20, 10, 1)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")
st.caption(f"Mode: {get_data_mode_label(source)}")
edges = build_coexpression_edges(data.expression, threshold=threshold)
degree_table = summarize_network(edges, data.expression.columns.tolist())
genes = data.expression.columns.tolist()

c1, c2, c3 = st.columns(3)
c1.metric("Genes", len(genes))
c2.metric("Edges", len(edges))
c3.metric("Average degree", f"{degree_table['degree'].mean():.2f}")

if edges.empty:
    st.warning("No edges above threshold. Lower the threshold in the sidebar.")
    st.stop()

st.subheader("Top Hub Genes")
st.dataframe(degree_table.head(top_hubs), use_container_width=True)
st.caption(
    "Hub interpretation: genes with higher degree connect to more partners and may act as key "
    "regulatory coordinators in the network."
)

# Circular network layout for lightweight visualization without extra dependencies.
gene_to_idx = {g: i for i, g in enumerate(genes)}
theta = np.linspace(0, 2 * np.pi, len(genes), endpoint=False)
positions = {g: (np.cos(theta[i]), np.sin(theta[i])) for g, i in gene_to_idx.items()}

edge_x = []
edge_y = []
for _, row in edges.iterrows():
    x0, y0 = positions[row["source"]]
    x1, y1 = positions[row["target"]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

node_x = [positions[g][0] for g in genes]
node_y = [positions[g][1] for g in genes]
node_degree = degree_table.set_index("gene").loc[genes, "degree"].values

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1, color="rgba(120,120,120,0.5)"),
        hoverinfo="skip",
        showlegend=False,
    )
)
fig.add_trace(
    go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=genes,
        textposition="top center",
        marker=dict(size=8 + node_degree * 2, color=node_degree, colorscale="Viridis"),
        hovertemplate="Gene: %{text}<br>Degree: %{marker.color}<extra></extra>",
        showlegend=False,
    )
)
fig.update_layout(
    title="Gene co-expression network (circular layout)",
    height=680,
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Network interpretation: larger/darker nodes have higher connectivity. "
    "Dense local links suggest co-expression modules worth biological follow-up."
)

st.subheader("Edge List")
st.dataframe(edges.sort_values("weight", key=np.abs, ascending=False), use_container_width=True)
st.caption(
    "Edge table: absolute weight close to 1 means stronger co-expression. "
    "Use top edges to nominate module-level hypotheses."
)
