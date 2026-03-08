"""Supervisor profile links and project alignment matrix."""
import pandas as pd
import streamlit as st

st.title("Supervisor Alignment")
st.caption("Profile-grounded fit, current gaps, and concrete upgrades")

st.subheader("Profile links")
st.markdown(
    """
- Prof. Dr. Mark Aarts (WUR): https://www.wur.nl/en/persons/profdr-mgm-mark-aarts
- Dr. L.B. (Basten) Snoek (UU): https://www.uu.nl/staff/LBSnoek
- Prof. Dr. Ricardo da Silva Torres (WUR): https://www.wur.nl/en/persons/profdr-r-ricardo-da-silva-torres
"""
)

st.subheader("Alignment matrix")
matrix = pd.DataFrame(
    [
        {
            "Supervisor": "Prof. Dr. Mark Aarts",
            "Primary focus": "Plant genetics, natural variation, systems-genetics integration",
            "Covered in app": "eQTL, GxE, network biology, host-microbiome links",
            "Current gap": "No wet-lab validation plan page yet",
            "Next modification": "Add candidate-prioritization to validation checklist (qPCR/knockout follow-up)",
        },
        {
            "Supervisor": "Dr. L.B. (Basten) Snoek",
            "Primary focus": "Quantitative/statistical genetics and reproducible analysis workflows",
            "Covered in app": "FDR control, per-environment scans, reproducibility methods page",
            "Current gap": "No explicit cross-validation diagnostics page",
            "Next modification": "Add residual diagnostics and bootstrap confidence intervals for top hits",
        },
        {
            "Supervisor": "Prof. Dr. Ricardo da Silva Torres",
            "Primary focus": "AI/ML, scalable data analytics, decision-support systems",
            "Covered in app": "Interpretable trait modeling, feature importance, workflow export",
            "Current gap": "No model-robustness stress tests",
            "Next modification": "Add model comparison panel + out-of-distribution checks across habitats",
        },
    ]
)
st.dataframe(matrix, use_container_width=True, hide_index=True)

st.subheader("Deep-check outcome")
st.markdown(
    """
The project is already strong for interview demonstration, but three upgrades will make it tighter for this team:

1. Add a validation-bridge page from in-silico candidate genes to feasible lab verification.
2. Add statistical robustness diagnostics (bootstrap CI, permutation sanity checks, split-by-habitat validation).
3. Add an AI benchmarking panel (RF vs linear baseline vs boosting) with explicit interpretability trade-offs.
"""
)

st.subheader("Interview one-liner")
st.code(
    "I can deliver robust eQTL and GxE outputs quickly, keep the statistics transparent, and extend to "
    "AI-ready decision support and host-microbiome integration for lettuce systems genetics.",
    language="text",
)
