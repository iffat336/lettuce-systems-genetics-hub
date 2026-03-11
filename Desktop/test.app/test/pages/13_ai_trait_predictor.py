"""AI module for stress tolerance prediction."""
from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import benchmark_trait_models, train_trait_model
from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label


st.title("AI Trait Predictor")
st.caption("Interpretable baseline model for supervisor-aligned trait prediction")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    top_features = st.slider("Top important genes", 5, 20, 10, 1)

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
    st.error("No supported trait target found in metadata.")
    st.stop()

target = st.selectbox("Target trait", target_options, index=0)
_, importances, metrics = train_trait_model(data.expression, data.metadata[target], seed=seed)
benchmark = benchmark_trait_models(data.expression, data.metadata[target], seed=seed, n_splits=5)

c1, c2 = st.columns(2)
c1.metric("Test R2", f"{metrics['r2']:.3f}")
c2.metric("Test MAE", f"{metrics['mae']:.3f}")

st.subheader("Model Comparison (5-fold CV)")
st.dataframe(benchmark, use_container_width=True, hide_index=True)
st.caption(
    "Comparison interpretation: prefer higher CV R2 and lower CV MAE. "
    "Small variance across folds suggests more stable performance."
)

st.subheader("Feature Importance")
top_imp = importances.head(top_features)
fig = px.bar(
    top_imp,
    x="importance",
    y="gene",
    orientation="h",
    title="Most informative transcripts for prediction",
)
fig.update_layout(height=420, yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Importance interpretation: top genes contribute most to prediction. "
    "Use these as priority candidates for eQTL and validation modules."
)

st.dataframe(importances, use_container_width=True)

st.markdown(
    """
Interpretation notes for interview:

- AI is used for prioritization and prediction, not as a black-box endpoint.
- Prioritized genes can be fed back into eQTL and network modules for biological validation.
- This is a baseline model; stronger designs can include cross-environment validation and
  multi-task learning across stress, photosynthesis, and micronutrient-homeostasis targets.
"""
)
