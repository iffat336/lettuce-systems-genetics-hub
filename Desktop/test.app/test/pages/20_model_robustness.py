"""Model robustness diagnostics for PhD collaboration discussions."""
from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.core import evaluate_model_robustness
from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label

st.title("Model Robustness")
st.caption("Cross-validation, bootstrap confidence intervals, and permutation sanity checks")

with st.sidebar:
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    n_splits = st.slider("CV folds", 3, 8, 5, 1)
    permutations = st.slider("Permutation runs", 20, 120, 40, 10)

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

with st.spinner("Running robustness diagnostics..."):
    benchmark, perm_df, summary = evaluate_model_robustness(
        data.expression,
        data.metadata[target],
        seed=seed,
        n_splits=n_splits,
        permutations=permutations,
    )

c1, c2, c3 = st.columns(3)
c1.metric("Best model", str(summary["best_model"]))
c2.metric("CV R2 (mean)", f"{summary['cv_r2_mean']:.3f}")
c3.metric("Permutation p-value", f"{summary['permutation_p_value']:.4f}")

st.metric("CV MAE (mean)", f"{summary['cv_mae_mean']:.3f}")
st.write(
    f"Bootstrap 95% CI for CV R2: [{summary['cv_r2_ci_low']:.3f}, {summary['cv_r2_ci_high']:.3f}]"
)

st.subheader("Model benchmark table")
st.dataframe(benchmark, use_container_width=True, hide_index=True)

st.subheader("Permutation null distribution")
fig = px.histogram(
    perm_df,
    x="perm_cv_r2_mean",
    nbins=20,
    title="Null distribution of CV R2 under shuffled target",
)
fig.add_vline(x=float(summary["cv_r2_mean"]), line_dash="dash", line_color="red")
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)

st.info(
    "PhD collaboration framing: this page demonstrates statistical rigor by checking if performance "
    "is stable and meaningfully above chance."
)
