"""Candidate validation planning page for biology-to-lab handoff."""
from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import build_candidate_validation_plan
from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label

st.title("Candidate Validation Plan")
st.caption("From computational ranking to concrete wet-lab follow-up design")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    top_n_genes = st.slider("Top candidates", 5, 20, 10, 1)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")
st.caption(f"Mode: {get_data_mode_label(source)}")

target_options = [
    col
    for col in [
        "stress_tolerance_index",
        "photosynthesis_efficiency_index",
        "zinc_homeostasis_index",
    ]
    if col in data.metadata.columns
]
if not target_options:
    st.error("No supported target traits available in metadata.")
    st.stop()

target = st.selectbox("Target trait", target_options, index=0)
plan = build_candidate_validation_plan(
    data.genotype,
    data.expression,
    data.metadata,
    seed=seed,
    target_trait=target,
    top_n_genes=top_n_genes,
)

if plan.empty:
    st.warning("No candidates could be generated for this target.")
    st.stop()

st.subheader("Prioritized validation table")
st.dataframe(plan, use_container_width=True, hide_index=True)
st.caption(
    "Table interpretation: higher priority_score reflects combined AI importance plus genetics evidence. "
    "Use recommended_validation to plan immediate lab follow-up."
)

st.subheader("Priority ranking view")
fig = px.bar(
    plan.sort_values("priority_score"),
    x="priority_score",
    y="gene",
    color="habitats_detected",
    orientation="h",
    title="Candidate priority score",
)
fig.update_layout(height=440)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Bar interpretation: longer bars are stronger validation priorities. "
    "Color shows in how many habitats each candidate is detected."
)

checklist_md = (
    "# Candidate Validation Checklist\n\n"
    "1. Confirm genotype marker quality for listed SNPs.\n"
    "2. Run qPCR across greenhouse/field/stress for top-ranked genes.\n"
    "3. Prioritize genes with multi-habitat signal consistency.\n"
    "4. Design perturbation follow-up (knockout/overexpression) for top 3 candidates.\n"
    "5. Connect results back to AI ranking and update model features.\n"
)
st.download_button(
    "Download validation checklist (.md)",
    data=checklist_md,
    file_name="candidate_validation_checklist.md",
    mime="text/markdown",
)

st.info(
    "PhD collaboration framing: this page bridges systems-genetics outputs to practical validation planning."
)
