"""Direct mapping of candidate fit to lab pain points."""
import streamlit as st

st.title("Lab Fit and Pain Points")
st.caption("How this PhD project supports Prof. Mark's current and future research goals")

st.subheader("Key lab pain points")
pain_points = [
    ("High-dimensional omics complexity", "Large RNA-seq and multi-omics matrices are hard to integrate robustly."),
    ("Environment-specific regulation", "Need to separate stable regulators from habitat-specific effects."),
    ("Cross-level integration", "Genes, traits, and species interactions are often analyzed in separate silos."),
    ("Reproducibility and speed", "Short cycles are needed for hypothesis testing before expensive experiments."),
    ("Actionable prioritization", "Need clear candidate regulators/species for follow-up validation."),
]
for title, detail in pain_points:
    st.markdown(f"- **{title}**: {detail}")

st.subheader("Your fit: what this app proves")
fit_points = [
    "I can build reproducible pipelines from genotype, transcript, trait, and habitat data.",
    "I can run eQTL and GxE analyses to highlight stable and context-dependent regulators.",
    "I can integrate network biology with AI without losing interpretability.",
    "I can add microbiome species co-occurrence and host-link analyses for future expansion.",
    "I can communicate results as dashboards that support rapid supervisor decision-making.",
]
for item in fit_points:
    st.markdown(f"- {item}")

st.subheader("First 12-month execution plan")
plan = [
    ("Month 1-2", "Data audit, metadata harmonization, and reproducible analysis environment."),
    ("Month 3-4", "Baseline eQTL scan and initial co-expression network in lettuce."),
    ("Month 5-6", "GxE analysis across habitats and regulator stability ranking."),
    ("Month 7-9", "Meta-biome integration: species abundance and host-microbe association map."),
    ("Month 10-12", "Candidate shortlist and manuscript-ready results with validation proposals."),
]
for period, objective in plan:
    st.markdown(f"- **{period}**: {objective}")

st.subheader("Interview closing line")
st.code(
    "I can start with existing LettuceKnow-style data, deliver a reproducible systems-genetics "
    "baseline quickly, and extend toward host-microbiome integration in line with the lab's future goals.",
    language="text",
)
