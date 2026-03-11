"""Project overview page for interview-focused systems genetics demo."""
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lettuce_project.workflow_io import get_active_or_synthetic, get_data_mode_label


st.title("Lettuce Systems Genetics Hub")
st.caption("Interview demo: genetics + bioinformatics + statistics + AI")

with st.sidebar:
    st.header("Dataset setup")
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)

data, source = get_active_or_synthetic(seed=seed)
st.info(f"Active data source: {source}")
st.caption(f"Mode: {get_data_mode_label(source)}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Samples", data.genotype.shape[0])
col2.metric("Genetic markers (SNPs)", data.genotype.shape[1])
col3.metric("Transcript features", data.expression.shape[1])
col4.metric("Habitats", data.metadata["habitat"].nunique())

col5, col6 = st.columns(2)
col5.metric("Population designs", data.metadata["population"].nunique())
col6.metric("Microbial species", data.microbiome.shape[1])

if "photosynthesis_efficiency_index" in data.metadata.columns and "zinc_homeostasis_index" in data.metadata.columns:
    col7, col8 = st.columns(2)
    col7.metric("Mean photosynthesis index", f"{data.metadata['photosynthesis_efficiency_index'].mean():.2f}")
    col8.metric("Mean zinc-homeostasis index", f"{data.metadata['zinc_homeostasis_index'].mean():.2f}")

st.markdown(
    """
This app demonstrates a realistic PhD starter workflow:

1. Build a clean genotype-expression-phenotype matrix.
2. Run eQTL-style association scans to map regulatory loci.
3. Quantify GxE behavior across different habitats.
4. Build co-expression and species co-occurrence networks.
5. Train an interpretable AI model to predict stress-tolerance traits.
6. Prioritize host genes and microbial species for validation.

All pages use the same dataset and can be reproduced by seed.
"""
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Metadata", "Genotype Preview", "Expression Preview", "Microbiome Preview"]
)

with tab1:
    st.dataframe(data.metadata.head(20), use_container_width=True)
    st.caption(
        "Metadata interpretation: each row is one lettuce sample and each column describes context "
        "(habitat/population) or target traits. Use this table to understand grouping before analysis."
    )
with tab2:
    st.dataframe(data.genotype.head(12), use_container_width=True)
    st.caption(
        "Genotype interpretation: columns are SNP markers and values are allele dosage (0/1/2). "
        "These markers are used to map regulatory loci in eQTL and GxE modules."
    )
with tab3:
    st.dataframe(data.expression.head(12), use_container_width=True)
    st.caption(
        "Expression interpretation: columns are transcript features and numbers are expression levels. "
        "Higher/lower values across samples capture regulatory variation for downstream modeling."
    )
with tab4:
    st.dataframe(data.microbiome.head(20), use_container_width=True)
    st.caption(
        "Microbiome interpretation: columns are microbial species abundance features per sample. "
        "This supports host-microbe correlation and co-occurrence network analysis."
    )

st.subheader("Known simulated causal map")
st.dataframe(data.causal_map, use_container_width=True)
st.caption(
    "Causal map interpretation: this links each simulated gene to its primary causal SNP. "
    "Use it as a reference to explain how recovered signals compare with known ground truth."
)

st.info(
    "Interview talking point: you can explain that this synthetic dataset represents "
    "the same workflow you would apply to real lettuce RIL/introgression data, while "
    "remaining conceptually consistent with Arabidopsis and C. elegans systems-genetics studies."
)
