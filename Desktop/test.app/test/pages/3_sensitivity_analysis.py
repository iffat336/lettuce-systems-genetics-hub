"""Sensitivity Analysis - Parameter importance and interaction effects."""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SEED_TYPES, FEATURE_RANGES, NUMERICAL_FEATURES, COLOR_PRIMARY
from src.utils import check_model_available, init_session_state, make_transparent_plotly_layout

init_session_state()
model = check_model_available()

st.title("🔬 Sensitivity Analysis")
st.markdown("Understand how each input parameter influences predicted stability.")

# ── Controls ──────────────────────────────────────────────────────
seed_keys = list(SEED_TYPES.keys())
selected_seed = st.session_state.selected_seed_type
seed_index = seed_keys.index(selected_seed) if selected_seed in seed_keys else 0

seed_type = st.sidebar.selectbox(
    "Seed Type",
    seed_keys,
    format_func=lambda x: SEED_TYPES[x]["name"],
    index=seed_index,
    key="sa_seed",
)

st.sidebar.subheader("Baseline Values")
baseline = {}
baseline["relative_humidity_pct"] = st.sidebar.slider("RH (%)", 30.0, 95.0, 60.0, key="sa_rh")
baseline["temperature_c"] = st.sidebar.slider("Temp (°C)", 5.0, 45.0, 22.0, key="sa_temp")
baseline["mechanical_loading_kpa"] = st.sidebar.slider("Load (kPa)", 50.0, 500.0, 150.0, key="sa_load")
baseline["storage_duration_days"] = st.sidebar.slider("Duration (d)", 0.0, 3650.0, 180.0, key="sa_dur")
baseline["initial_moisture_pct"] = st.sidebar.slider("Moisture (%)", 5.0, 25.0, 12.0, key="sa_mc")

FEATURE_LABELS = {
    "relative_humidity_pct": "Relative Humidity (%)",
    "temperature_c": "Temperature (°C)",
    "mechanical_loading_kpa": "Mechanical Load (kPa)",
    "storage_duration_days": "Storage Duration (days)",
    "initial_moisture_pct": "Initial Moisture (%)",
}

# ── OAT Sensitivity Sweeps ───────────────────────────────────────
st.subheader("One-at-a-Time (OAT) Sensitivity")
st.write("Each plot sweeps one parameter while holding all others at baseline values.")

n_sweep = 80
sensitivity_indices = {}
cols = st.columns(3)
for i, feat in enumerate(NUMERICAL_FEATURES):
    fmin, fmax, _ = FEATURE_RANGES[feat]
    sweep_vals = np.linspace(fmin, fmax, n_sweep)

    sweep_df = pd.DataFrame({f: baseline[f] for f in NUMERICAL_FEATURES}, index=range(n_sweep))
    sweep_df[feat] = sweep_vals
    sweep_df["seed_type"] = seed_type

    preds = np.clip(model.predict(sweep_df), 0, 1) * 100
    sensitivity_indices[feat] = preds.max() - preds.min()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sweep_vals, y=preds,
        mode="lines", line=dict(color=COLOR_PRIMARY, width=3),
    ))
    fig.add_vline(x=baseline[feat], line_dash="dash", line_color="#f1c40f",
                  annotation_text="Baseline")
    fig.update_layout(**make_transparent_plotly_layout(
        height=280,
        title=FEATURE_LABELS[feat],
        xaxis_title=FEATURE_LABELS[feat],
        yaxis_title="Stability (%)",
        yaxis_range=[0, 100],
        margin=dict(l=40, r=20, t=40, b=40),
    ))
    with cols[i % 3]:
        st.plotly_chart(fig, use_container_width=True)

# Extra row for remaining plots
if len(NUMERICAL_FEATURES) > 3:
    remaining = st.columns(3)
    for j, feat in enumerate(NUMERICAL_FEATURES[3:]):
        pass  # Already plotted above via modular loop

# ── Parameter Importance Ranking ──────────────────────────────────
st.divider()
st.subheader("Parameter Importance Ranking")
st.write("Sensitivity index = max(stability) - min(stability) over the full parameter sweep.")

sorted_features = sorted(sensitivity_indices.items(), key=lambda x: x[1], reverse=True)
feat_names = [FEATURE_LABELS[f] for f, _ in sorted_features]
feat_vals = [v for _, v in sorted_features]

fig_bar = go.Figure(go.Bar(
    x=feat_vals, y=feat_names,
    orientation="h",
    marker_color=[COLOR_PRIMARY] * len(feat_names),
    text=[f"{v:.1f}%" for v in feat_vals],
    textposition="outside",
))
fig_bar.update_layout(
    **make_transparent_plotly_layout(height=350),
    title="Sensitivity Index (Stability Range %)",
    xaxis_title="Stability Range (%)",
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── Interactive Contour Plot ──────────────────────────────────────
st.divider()
st.subheader("Parameter Interaction Contour")
st.write("Select two parameters to visualize their joint effect on stability.")

c1, c2 = st.columns(2)
with c1:
    x_feat = st.selectbox("X-axis Parameter", NUMERICAL_FEATURES,
                          format_func=lambda x: FEATURE_LABELS[x], index=0)
with c2:
    y_options = [f for f in NUMERICAL_FEATURES if f != x_feat]
    y_feat = st.selectbox("Y-axis Parameter", y_options,
                          format_func=lambda x: FEATURE_LABELS[x], index=0)

with st.spinner("Computing contour..."):
    n_grid = 40
    x_range = np.linspace(*FEATURE_RANGES[x_feat][:2], n_grid)
    y_range = np.linspace(*FEATURE_RANGES[y_feat][:2], n_grid)
    X, Y = np.meshgrid(x_range, y_range)

    grid_df = pd.DataFrame({f: baseline[f] for f in NUMERICAL_FEATURES}, index=range(n_grid * n_grid))
    grid_df[x_feat] = X.ravel()
    grid_df[y_feat] = Y.ravel()
    grid_df["seed_type"] = seed_type

    Z = np.clip(model.predict(grid_df), 0, 1).reshape(X.shape) * 100

fig_cont = go.Figure(data=go.Contour(
    x=x_range, y=y_range, z=Z,
    colorscale="Viridis",
    colorbar=dict(title="Stability %"),
    contours=dict(showlabels=True),
))
fig_cont.add_trace(go.Scatter(
    x=[baseline[x_feat]], y=[baseline[y_feat]],
    mode="markers",
    marker=dict(size=14, color=COLOR_PRIMARY, symbol="x", line=dict(width=2, color="white")),
    name="Baseline",
))
fig_cont.update_layout(
    **make_transparent_plotly_layout(height=500),
    xaxis_title=FEATURE_LABELS[x_feat],
    yaxis_title=FEATURE_LABELS[y_feat],
    title=f"Stability Contour: {FEATURE_LABELS[x_feat]} vs {FEATURE_LABELS[y_feat]}",
)
st.plotly_chart(fig_cont, use_container_width=True)
