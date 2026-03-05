"""Landing page for Lettuce Systems Genetics Hub."""
import streamlit as st

st.set_page_config(
    page_title="Lettuce Systems Genetics Hub",
    page_icon="L",
    layout="wide",
)

st.title("Lettuce Systems Genetics Hub")
st.caption("PhD interview demo: systems genetics, network biology, and meta-biome integration")

st.markdown(
    """
Use the left sidebar to open pages:

1. Project Overview
2. eQTL Explorer
3. Network Biology
4. AI Trait Predictor
5. GxE Systems Genetics
6. Meta-Biome Integration
7. Methods
8. Lab Fit and Pain Points
"""
)

st.info(
    "If pages are not visible, verify Streamlit Cloud main file path and ensure this app runs from the project folder."
)
