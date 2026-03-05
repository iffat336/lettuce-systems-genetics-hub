# Lettuce Systems Genetics Hub (Interview Demo)

Streamlit project for PhD interview discussions around:
- Genetics and natural variation
- RNA-seq and multi-omics integration
- eQTL mapping
- Network biology
- AI-assisted trait prediction

## Modules
- `Project Overview`: synthetic lettuce genotype-expression-phenotype dataset
- `eQTL Explorer`: marker-transcript associations with FDR
- `Network Biology`: co-expression edge map and hub genes
- `AI Trait Predictor`: baseline model for stress tolerance
- `GxE Systems Genetics`: environment-specific regulatory effects
- `Meta-Biome Integration`: species abundance and host-microbiome links
- `Lab Fit and Pain Points`: explicit contribution plan for PhD lab fit
- `Methods`: reproducibility and project-fit notes

## Local Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this project to a GitHub repository.
2. Open https://share.streamlit.io/
3. Click **New app**.
4. Select your repository and branch.
5. Set **Main file path** to `app.py`.
6. Click **Deploy**.

## Suggested interview framing
Use this app to present a realistic first-year PhD workflow:
1. Start from available lettuce omics data.
2. Build eQTL maps for regulatory loci.
3. Quantify environment-dependent regulation (GxE).
4. Derive co-expression and microbial co-occurrence modules.
5. Use interpretable ML for trait prioritization.
6. Validate top candidates in collaboration with genetics/statistics/AI supervisors.
