"""Supervisor profile links and project alignment."""
import streamlit as st

st.title("Supervisor Alignment")
st.caption("Profiles, research fit, and interview framing")

st.subheader("Prof. Mark - research alignment")
st.markdown(
    """
- Genetic and phenotypic variation across individuals
- High-throughput omics (RNA-seq) and large-scale computational analysis
- Genetical genomics and systems genetics (eQTL, regulatory loci, networks)
- Model-system grounding in Arabidopsis and C. elegans for mechanism discovery
- Multi-environment expression analysis in lettuce populations
- Future direction: integrate genetics of expression with meta-biome sequencing
"""
)

st.subheader("Dr. L.B. (Basten) Snoek - profile links")
st.markdown(
    """
- Utrecht University staff profile: https://www.uu.nl/staff/LBSnoek  
- UU Research Portal profile: https://research-portal.uu.nl/en/persons/basten-snoek
"""
)

st.subheader("Why this project fits this supervision team")
st.markdown(
    """
1. eQTL and GxE modules map regulatory loci and environment-dependent effects.
2. Network module supports systems-level interpretation and hub prioritization.
3. The workflow is transferable from Arabidopsis/C. elegans-style genetical genomics logic to lettuce populations.
4. AI module supports predictive ranking with interpretable feature importance.
5. Meta-biome module supports future host-microbiome integration goals.
6. Reproducible pipeline design supports fast iteration across supervisors.
"""
)

st.subheader("Interview one-liner")
st.code(
    "I can start with existing lettuce data, deliver robust eQTL and network results quickly, "
    "and extend into host-microbiome integration with strong statistical support.",
    language="text",
)
