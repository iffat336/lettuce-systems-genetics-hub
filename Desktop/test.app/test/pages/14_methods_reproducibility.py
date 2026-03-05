"""Methods and reproducibility page."""
import streamlit as st

st.title("Methods and Reproducibility")
st.caption("How this demo maps to a real PhD starter workflow")

st.markdown(
    """
## Analysis blueprint
1. Data curation
   - Standardize genotype coding and transcript matrix.
   - Track metadata (habitat/environment batch structure).
2. eQTL scan
   - Linear association for marker-expression pairs.
   - Multiple testing correction via BH-FDR.
3. GxE systems genetics
   - Per-habitat eQTL scans and regulator stability score.
   - Separation of stable vs environment-specific effects.
4. Network inference
   - Correlation-based co-expression map.
   - Species co-occurrence for microbiome structure.
5. Host-microbiome integration
   - Host gene vs species abundance links.
6. AI prediction
   - Trait modeling from transcript profiles.
   - Importance-based interpretation and feedback to biology.
"""
)

st.markdown(
    """
## What to say in interview
- I can start immediately with existing lettuce data and deliver a reproducible baseline.
- I use AI where it adds value, while keeping statistics and biological interpretation central.
- I can produce short-cycle outputs: data audit, first eQTL map, GxE map, network map, and first predictive model.
"""
)

st.code(
    "streamlit run app.py",
    language="bash",
)

st.info(
    "Deployment target: Streamlit Community Cloud. Repository only needs app.py, pages/, src/, and requirements.txt."
)
