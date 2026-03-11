"""Enhanced Dashboard - Seed Hygrothermal & Mechanical Stability."""
import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.graph_objects as go

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SEED_TYPES, FEATURE_RANGES, COLOR_PRIMARY, COLOR_WARNING, COLOR_DANGER
from src.utils import (
    check_model_available,
    get_status_label,
    init_session_state,
    make_transparent_plotly_layout,
)
from src.seed_science import viability_curve, harrington_hundred_rule

init_session_state()
model = check_model_available()

# ── Sidebar Controls ──────────────────────────────────────────────
st.sidebar.title("🔬 Research Controls")

seed_keys = list(SEED_TYPES.keys())
selected_seed = st.session_state.selected_seed_type
seed_index = seed_keys.index(selected_seed) if selected_seed in seed_keys else 0

seed_type = st.sidebar.selectbox(
    "Seed Type",
    seed_keys,
    format_func=lambda x: SEED_TYPES[x]["name"],
    index=seed_index,
    help="Each seed type has unique degradation characteristics and Ellis-Roberts viability constants.",
)
st.session_state.selected_seed_type = seed_type
seed_cfg = SEED_TYPES[seed_type]

st.sidebar.divider()
st.sidebar.subheader("Hygrothermal Variables")
rh = st.sidebar.slider(
    "Relative Humidity (%)", 30.0, 95.0, 60.0,
    help="Controls vapor diffusion rate into the seed coat. Above 70% RH, enzymatic degradation accelerates."
)
temp = st.sidebar.slider(
    "Ambient Temperature (°C)", 5.0, 45.0, 22.0,
    help="Higher temperature accelerates moisture diffusion and biochemical degradation (Arrhenius-type)."
)

st.sidebar.subheader("Mechanical & Storage")
load = st.sidebar.slider(
    "Mechanical Stress (kPa)", 50.0, 500.0, 150.0,
    help="Compressive/impact loading during handling and storage."
)
duration = st.sidebar.slider(
    "Storage Duration (days)", 0.0, 3650.0, 180.0, step=30.0,
    help="Predicted storage period. Ellis-Roberts sigma governs the decay rate."
)
moisture = st.sidebar.slider(
    "Initial Moisture Content (%)", 5.0, 25.0, 12.0,
    help="Seed moisture at the time of storage. Lower = longer viability."
)

st.sidebar.divider()
comparison_mode = st.sidebar.checkbox("Enable Comparison Mode", value=st.session_state.comparison_mode)
st.session_state.comparison_mode = comparison_mode

if comparison_mode:
    with st.sidebar.expander("Condition B", expanded=True):
        rh_b = st.slider("RH (%) - B", 30.0, 95.0, 80.0, key="rh_b")
        temp_b = st.slider("Temp (°C) - B", 5.0, 45.0, 35.0, key="temp_b")
        load_b = st.slider("Stress (kPa) - B", 50.0, 500.0, 300.0, key="load_b")
        duration_b = st.slider("Duration (days) - B", 0.0, 3650.0, 365.0, step=30.0, key="dur_b")
        moisture_b = st.slider("Moisture (%) - B", 5.0, 25.0, 18.0, key="mc_b")

st.sidebar.divider()
st.sidebar.info(
    f"**{seed_cfg['name']}**\n\n"
    f"Optimal Temp: {seed_cfg['optimal_temp_c'][0]} to {seed_cfg['optimal_temp_c'][1]}°C\n\n"
    f"Optimal MC: {seed_cfg['optimal_moisture_pct'][0]}-{seed_cfg['optimal_moisture_pct'][1]}%\n\n"
    f"Max Storage: ~{seed_cfg['max_storage_years']} years"
)

# ── Header ────────────────────────────────────────────────────────
st.title("🌱 Digital Twin: Seed Hygrothermal & Mechanical Stability")
st.markdown("### Real-Time Surrogate Predictions via ANN Pipeline")

# ── Prediction ────────────────────────────────────────────────────
input_df = pd.DataFrame([{
    "relative_humidity_pct": rh,
    "temperature_c": temp,
    "mechanical_loading_kpa": load,
    "storage_duration_days": duration,
    "initial_moisture_pct": moisture,
    "seed_type": seed_type,
}])

start_t = time.time()
stability_pred = float(model.predict(input_df)[0])
stability_pred = max(0.0, min(1.0, stability_pred))
latency = (time.time() - start_t) * 1000

status_text, status_color = get_status_label(stability_pred, seed_type)

# Viability from Ellis-Roberts
days_v, viab_v = viability_curve(seed_type, moisture, temp, max_days=3650)
idx = np.searchsorted(days_v, duration)
current_viability = viab_v[min(idx, len(viab_v) - 1)]

# Hundred Rule
hundred_sum, hundred_safe = harrington_hundred_rule(temp, rh)

# ── Metrics Row ───────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Effective Stability", f"{stability_pred:.1%}")
with m2:
    st.metric("Material Status", status_text)
with m3:
    st.metric("Surrogate Latency", f"{latency:.2f} ms")
with m4:
    st.metric("Viability (E-R)", f"{current_viability:.1f}%")

# ── Comparison metrics ────────────────────────────────────────────
if comparison_mode:
    input_df_b = pd.DataFrame([{
        "relative_humidity_pct": rh_b,
        "temperature_c": temp_b,
        "mechanical_loading_kpa": load_b,
        "storage_duration_days": duration_b,
        "initial_moisture_pct": moisture_b,
        "seed_type": seed_type,
    }])
    stability_b = float(model.predict(input_df_b)[0])
    stability_b = max(0.0, min(1.0, stability_b))
    status_b, _ = get_status_label(stability_b, seed_type)
    _, viab_b = viability_curve(seed_type, moisture_b, temp_b, max_days=3650)
    idx_b = np.searchsorted(days_v, duration_b)
    viab_b_val = viab_b[min(idx_b, len(viab_b) - 1)]

    st.markdown("##### Condition B Comparison")
    cb1, cb2, cb3, cb4 = st.columns(4)
    with cb1:
        delta = stability_b - stability_pred
        st.metric("Stability B", f"{stability_b:.1%}", delta=f"{delta:+.1%}")
    with cb2:
        st.metric("Status B", status_b)
    with cb3:
        st.metric("RH/Temp B", f"{rh_b}% / {temp_b}°C")
    with cb4:
        st.metric("Viability B", f"{viab_b_val:.1f}%")

st.divider()

# ── Main Visualization Area ───────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Hygrothermal Degradation Logic")
    st.write(
        "This model simulates the **anisotropic diffusion** of moisture into a biological seed coat. "
        "By applying **Inverse Analysis**, we determine the effective properties of the seed structure "
        "under complex environmental wetting-drying cycles."
    )

    thresholds = seed_cfg["stability_thresholds"]
    if stability_pred < thresholds["degraded"]:
        st.error(
            "🚨 **Structural Failure Risk**: The coupling of high RH and loading "
            "has exceeded the material's load-bearing capacity."
        )
    elif stability_pred < thresholds["optimal"]:
        st.warning(
            "⚠️ **Vapor Diffusion Hazard**: Moisture ingress is reducing "
            "structural homogenization efficiency."
        )
    else:
        st.success(
            "✅ **Stable Configuration**: Material characteristics are within "
            "the safe hygrothermal range."
        )

    # Hundred Rule indicator
    if hundred_safe:
        st.info(f"Harrington's Hundred Rule: {hundred_sum:.1f} < 100 — **SAFE**")
    else:
        st.warning(f"Harrington's Hundred Rule: {hundred_sum:.1f} >= 100 — **UNSAFE**")

with col2:
    # Gauge
    bar_color = COLOR_PRIMARY if stability_pred > thresholds["optimal"] else (
        COLOR_WARNING if stability_pred > thresholds["degraded"] else COLOR_DANGER
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=stability_pred * 100,
        number={"suffix": "%", "font": {"color": COLOR_PRIMARY, "size": 50}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2, "tickcolor": COLOR_PRIMARY},
            "bar": {"color": bar_color},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 2,
            "bordercolor": "#34495e",
            "steps": [
                {"range": [0, thresholds["degraded"] * 100], "color": "rgba(255, 75, 43, 0.3)"},
                {"range": [thresholds["degraded"] * 100, thresholds["optimal"] * 100], "color": "rgba(241, 196, 15, 0.3)"},
                {"range": [thresholds["optimal"] * 100, 100], "color": "rgba(0, 255, 135, 0.3)"},
            ],
            "threshold": {
                "line": {"color": COLOR_DANGER, "width": 4},
                "thickness": 0.75,
                "value": 95,
            },
        },
    ))
    fig.update_layout(**make_transparent_plotly_layout(
        margin=dict(l=30, r=30, t=40, b=10),
        font=dict(color=COLOR_PRIMARY, family="Inter, Arial"),
        height=350,
    ))
    st.plotly_chart(fig, use_container_width=True)

# ── Tabbed Advanced Visualizations ────────────────────────────────
st.divider()
tab_surface, tab_heatmap, tab_timeline = st.tabs(["3D Surface", "Heatmap", "Timeline & Uncertainty"])

with tab_surface:
    with st.spinner("Computing stability landscape..."):
        rh_range = np.linspace(30, 95, 35)
        temp_range = np.linspace(5, 45, 35)
        RH_grid, TEMP_grid = np.meshgrid(rh_range, temp_range)
        grid_df = pd.DataFrame({
            "relative_humidity_pct": RH_grid.ravel(),
            "temperature_c": TEMP_grid.ravel(),
            "mechanical_loading_kpa": load,
            "storage_duration_days": duration,
            "initial_moisture_pct": moisture,
            "seed_type": seed_type,
        })
        Z = model.predict(grid_df).reshape(RH_grid.shape)
        Z = np.clip(Z, 0, 1)

    fig3d = go.Figure(data=[
        go.Surface(
            x=rh_range, y=temp_range, z=Z * 100,
            colorscale="Viridis", opacity=0.85,
            colorbar=dict(title="Stability %", ticksuffix="%"),
        ),
        go.Scatter3d(
            x=[rh], y=[temp], z=[stability_pred * 100],
            mode="markers",
            marker=dict(size=8, color=COLOR_PRIMARY, symbol="diamond"),
            name="Current Point",
        ),
    ])
    fig3d.update_layout(
        **make_transparent_plotly_layout(),
        height=550,
        scene=dict(
            xaxis_title="Relative Humidity (%)",
            yaxis_title="Temperature (°C)",
            zaxis_title="Stability (%)",
            bgcolor="rgba(0,0,0,0)",
        ),
        title=f"Stability Landscape — {seed_cfg['name']} @ {load:.0f} kPa",
    )
    st.plotly_chart(fig3d, use_container_width=True)

with tab_heatmap:
    fig_hm = go.Figure(data=go.Heatmap(
        x=rh_range, y=temp_range, z=Z * 100,
        colorscale="Viridis",
        colorbar=dict(title="Stability %"),
    ))
    fig_hm.add_trace(go.Scatter(
        x=[rh], y=[temp], mode="markers",
        marker=dict(size=14, color=COLOR_PRIMARY, symbol="x", line=dict(width=2, color="white")),
        name="Current Point",
    ))
    fig_hm.update_layout(
        **make_transparent_plotly_layout(),
        height=500,
        xaxis_title="Relative Humidity (%)",
        yaxis_title="Temperature (°C)",
        title=f"Stability Heatmap — {seed_cfg['name']}",
    )
    st.plotly_chart(fig_hm, use_container_width=True)

with tab_timeline:
    col_tl, col_mc = st.columns(2)
    with col_tl:
        st.markdown("##### Stability vs Storage Duration")
        dur_sweep = np.linspace(0, 3650, 100)
        dur_df = pd.DataFrame({
            "relative_humidity_pct": rh,
            "temperature_c": temp,
            "mechanical_loading_kpa": load,
            "storage_duration_days": dur_sweep,
            "initial_moisture_pct": moisture,
            "seed_type": seed_type,
        })
        stab_sweep = np.clip(model.predict(dur_df), 0, 1) * 100

        fig_tl = go.Figure()
        fig_tl.add_trace(go.Scatter(
            x=dur_sweep, y=stab_sweep, mode="lines",
            line=dict(color=COLOR_PRIMARY, width=3),
            name="Stability",
        ))
        fig_tl.add_vline(x=duration, line_dash="dash", line_color=COLOR_WARNING, annotation_text="Current")
        fig_tl.update_layout(
            **make_transparent_plotly_layout(),
            height=350,
            xaxis_title="Storage Duration (days)",
            yaxis_title="Stability (%)",
        )
        st.plotly_chart(fig_tl, use_container_width=True)

    with col_mc:
        st.markdown("##### Monte Carlo Uncertainty (n=200)")
        np.random.seed(None)
        n_mc = 200
        mc_df = pd.DataFrame({
            "relative_humidity_pct": rh + np.random.normal(0, 3, n_mc),
            "temperature_c": temp + np.random.normal(0, 2, n_mc),
            "mechanical_loading_kpa": load + np.random.normal(0, 20, n_mc),
            "storage_duration_days": duration + np.random.normal(0, 30, n_mc),
            "initial_moisture_pct": moisture + np.random.normal(0, 1, n_mc),
            "seed_type": seed_type,
        })
        # Clip to valid ranges
        mc_df["relative_humidity_pct"] = mc_df["relative_humidity_pct"].clip(30, 95)
        mc_df["temperature_c"] = mc_df["temperature_c"].clip(5, 45)
        mc_df["mechanical_loading_kpa"] = mc_df["mechanical_loading_kpa"].clip(50, 500)
        mc_df["storage_duration_days"] = mc_df["storage_duration_days"].clip(0, 3650)
        mc_df["initial_moisture_pct"] = mc_df["initial_moisture_pct"].clip(5, 25)

        mc_preds = np.clip(model.predict(mc_df), 0, 1) * 100

        fig_mc = go.Figure(data=[go.Histogram(
            x=mc_preds, nbinsx=30,
            marker_color=COLOR_PRIMARY, opacity=0.75,
        )])
        fig_mc.add_vline(x=stability_pred * 100, line_dash="dash", line_color=COLOR_DANGER,
                         annotation_text=f"Mean: {mc_preds.mean():.1f}%")
        fig_mc.update_layout(
            **make_transparent_plotly_layout(),
            height=350,
            xaxis_title="Stability (%)",
            yaxis_title="Count",
        )
        st.plotly_chart(fig_mc, use_container_width=True)
        st.caption(f"Std Dev: {mc_preds.std():.2f}% | 95% CI: [{np.percentile(mc_preds, 2.5):.1f}%, {np.percentile(mc_preds, 97.5):.1f}%]")

# ── Prediction History ────────────────────────────────────────────
import datetime
record = {
    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    "seed_type": seed_type,
    "RH%": rh, "Temp°C": temp, "Load_kPa": load,
    "Duration_d": duration, "MC%": moisture,
    "stability": round(stability_pred, 4),
    "status": status_text,
}
history = st.session_state.prediction_history
if len(history) == 0 or history[-1] != record:
    history.append(record)
    if len(history) > 50:
        history.pop(0)

with st.expander(f"Prediction History ({len(history)} records)"):
    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)

# ── Scientific Footer ────────────────────────────────────────────
st.divider()
st.subheader("Methodology: Shell-to-Beam Surrogate Mapping")
st.write(
    "This dashboard takes the output of a multi-step numerical homogenization (FEM) "
    "and maps it to a fast Artificial Neural Network (ANN). This enables a "
    "**Real-Time Digital Twin** that bridges Construction 4.0 and Agriculture 4.0."
)
st.caption("Developed for PhD Interview Preparation — Poznań University of Life Sciences")
