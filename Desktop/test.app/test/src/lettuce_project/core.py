"""Synthetic multi-omics generators and analysis helpers for Streamlit pages."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import linregress
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split


@dataclass(frozen=True)
class ProjectData:
    genotype: pd.DataFrame
    expression: pd.DataFrame
    metadata: pd.DataFrame
    causal_map: pd.DataFrame
    microbiome: pd.DataFrame


def generate_synthetic_multiomics(
    n_samples: int = 180,
    n_snps: int = 55,
    n_genes: int = 26,
    seed: int = 42,
) -> ProjectData:
    """Generate a compact, interview-ready synthetic lettuce multi-omics dataset."""
    rng = np.random.default_rng(seed)

    sample_ids = [f"L{i:03d}" for i in range(1, n_samples + 1)]
    snp_names = [f"SNP_{i:02d}" for i in range(1, n_snps + 1)]
    gene_names = [f"Gene_{i:02d}" for i in range(1, n_genes + 1)]

    genotype = rng.binomial(2, rng.uniform(0.15, 0.85, n_snps), size=(n_samples, n_snps))
    genotype_df = pd.DataFrame(genotype, columns=snp_names, index=sample_ids)

    habitat = rng.choice(["greenhouse", "field", "drought_stress"], size=n_samples, p=[0.35, 0.35, 0.30])
    population = rng.choice(["RIL", "Introgression", "Natural"], size=n_samples, p=[0.4, 0.3, 0.3])
    habitat_effect = np.select(
        [habitat == "greenhouse", habitat == "field", habitat == "drought_stress"],
        [0.4, 0.1, -0.5],
    )

    expression = np.zeros((n_samples, n_genes))
    causal_rows = []
    for gene_idx in range(n_genes):
        snp_idx = (gene_idx * 2) % n_snps
        snp_name = snp_names[snp_idx]
        effect = rng.uniform(0.25, 0.9) * rng.choice([-1.0, 1.0])
        noise = rng.normal(0, 1.0, n_samples)
        expression[:, gene_idx] = 7.0 + effect * genotype[:, snp_idx] + habitat_effect + noise
        causal_rows.append({"gene": gene_names[gene_idx], "causal_snp": snp_name, "sim_effect": effect})

    expression_df = pd.DataFrame(expression, columns=gene_names, index=sample_ids)
    causal_map_df = pd.DataFrame(causal_rows)

    key_genes = expression_df[["Gene_01", "Gene_03", "Gene_07", "Gene_11", "Gene_18"]]
    stress_score = (
        0.28 * key_genes["Gene_01"]
        - 0.24 * key_genes["Gene_03"]
        + 0.33 * key_genes["Gene_07"]
        + 0.19 * key_genes["Gene_11"]
        + 0.21 * key_genes["Gene_18"]
        + 0.15 * genotype_df["SNP_04"]
        - 0.18 * genotype_df["SNP_12"]
        + rng.normal(0, 0.7, n_samples)
    )

    metadata_df = pd.DataFrame(
        {
            "sample_id": sample_ids,
            "habitat": habitat,
            "population": population,
            "stress_tolerance_index": stress_score,
        }
    ).set_index("sample_id")

    species_names = [f"Microbe_{i:02d}" for i in range(1, 19)]
    base_alpha = np.full(len(species_names), 1.2)
    base_alpha[:6] = 2.5
    microbiome_matrix = []
    for i in range(n_samples):
        env_shift = {
            "greenhouse": np.array([0.8, 0.6, 0.4] + [0.0] * (len(species_names) - 3)),
            "field": np.array([0.1, 0.2, 0.1, 0.6, 0.5, 0.4] + [0.0] * (len(species_names) - 6)),
            "drought_stress": np.array([0.0] * 6 + [0.9, 0.7, 0.6] + [0.0] * (len(species_names) - 9)),
        }[habitat[i]]
        alpha = np.clip(base_alpha + env_shift, 0.1, None)
        comp = rng.dirichlet(alpha)
        microbiome_matrix.append(comp)
    microbiome_df = pd.DataFrame(microbiome_matrix, columns=species_names, index=sample_ids)

    # Additional trait targets to support supervisor-aligned discussions.
    photo_gene = expression_df.columns[min(1, n_genes - 1)]
    zinc_gene_up = expression_df.columns[min(4, n_genes - 1)]
    zinc_gene_down = expression_df.columns[min(13, n_genes - 1)]
    photo_snp = genotype_df.columns[min(8, n_snps - 1)]
    zinc_snp = genotype_df.columns[min(19, n_snps - 1)]
    zinc_microbe = microbiome_df.columns[min(2, len(species_names) - 1)]

    photosynthesis_index = (
        50.0
        + 1.8 * expression_df[photo_gene]
        - 1.2 * (metadata_df["habitat"] == "drought_stress").astype(float)
        + 0.35 * genotype_df[photo_snp]
        + rng.normal(0, 1.0, n_samples)
    )
    zinc_homeostasis_index = (
        48.0
        + 1.4 * expression_df[zinc_gene_up]
        - 1.1 * expression_df[zinc_gene_down]
        + 0.4 * genotype_df[zinc_snp]
        + 8.0 * microbiome_df[zinc_microbe]
        + rng.normal(0, 1.0, n_samples)
    )
    metadata_df["photosynthesis_efficiency_index"] = photosynthesis_index
    metadata_df["zinc_homeostasis_index"] = zinc_homeostasis_index

    return ProjectData(
        genotype=genotype_df,
        expression=expression_df,
        metadata=metadata_df,
        causal_map=causal_map_df,
        microbiome=microbiome_df,
    )


def benjamini_hochberg(pvals: pd.Series) -> pd.Series:
    """Compute BH-FDR adjusted p-values."""
    p = pvals.to_numpy()
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.empty(n)
    running = 1.0
    for i in range(n - 1, -1, -1):
        rank = i + 1
        running = min(running, ranked[i] * n / rank)
        adjusted[i] = running
    out = np.empty(n)
    out[order] = adjusted
    return pd.Series(out, index=pvals.index)


def run_eqtl_scan(
    genotype: pd.DataFrame,
    expression: pd.DataFrame,
    min_abs_effect: float = 0.05,
) -> pd.DataFrame:
    """Run a simple gene x SNP linear scan and return ranked association table."""
    records = []
    for gene in expression.columns:
        y = expression[gene].values
        for snp in genotype.columns:
            x = genotype[snp].values
            slope, _, r_value, p_value, _ = linregress(x, y)
            if abs(slope) < min_abs_effect:
                continue
            records.append(
                {
                    "gene": gene,
                    "snp": snp,
                    "effect_size": slope,
                    "r2": float(r_value**2),
                    "p_value": p_value,
                }
            )

    if not records:
        return pd.DataFrame(columns=["gene", "snp", "effect_size", "r2", "p_value", "fdr"])

    result = pd.DataFrame(records).sort_values("p_value").reset_index(drop=True)
    result["fdr"] = benjamini_hochberg(result["p_value"])
    return result


def build_coexpression_edges(expression: pd.DataFrame, threshold: float = 0.65) -> pd.DataFrame:
    """Create undirected gene-gene edges from Pearson correlation threshold."""
    corr = expression.corr()
    genes = expression.columns.to_list()
    edges = []
    for i in range(len(genes)):
        for j in range(i + 1, len(genes)):
            weight = corr.iloc[i, j]
            if abs(weight) >= threshold:
                edges.append({"source": genes[i], "target": genes[j], "weight": float(weight)})
    return pd.DataFrame(edges)


def summarize_network(edges: pd.DataFrame, genes: list[str]) -> pd.DataFrame:
    """Compute a simple degree table from edge list."""
    degree = {g: 0 for g in genes}
    for _, row in edges.iterrows():
        degree[row["source"]] += 1
        degree[row["target"]] += 1
    out = pd.DataFrame({"gene": list(degree.keys()), "degree": list(degree.values())})
    return out.sort_values("degree", ascending=False).reset_index(drop=True)


def train_trait_model(
    expression: pd.DataFrame,
    target: pd.Series,
    seed: int = 42,
) -> tuple[RandomForestRegressor, pd.DataFrame, dict[str, float]]:
    """Train an interpretable baseline model for stress tolerance prediction."""
    X_train, X_test, y_train, y_test = train_test_split(
        expression, target, test_size=0.25, random_state=seed
    )
    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=8,
        min_samples_leaf=3,
        random_state=seed,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    metrics = {
        "r2": float(r2_score(y_test, pred)),
        "mae": float(mean_absolute_error(y_test, pred)),
    }
    importances = pd.DataFrame(
        {"gene": expression.columns, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    return model, importances.reset_index(drop=True), metrics


def run_environment_eqtl_scan(
    genotype: pd.DataFrame,
    expression: pd.DataFrame,
    metadata: pd.DataFrame,
    min_group_size: int = 25,
) -> pd.DataFrame:
    """Run per-habitat eQTL scans to expose environment-dependent effects."""
    records = []
    for habitat, env_idx in metadata.groupby("habitat").groups.items():
        if len(env_idx) < min_group_size:
            continue
        g_env = genotype.loc[env_idx]
        e_env = expression.loc[env_idx]
        env_res = run_eqtl_scan(g_env, e_env, min_abs_effect=0.05)
        if env_res.empty:
            continue
        env_res = env_res.sort_values("p_value").head(60).copy()
        env_res["habitat"] = habitat
        records.append(env_res)

    if not records:
        return pd.DataFrame(columns=["gene", "snp", "effect_size", "r2", "p_value", "fdr", "habitat"])

    merged = pd.concat(records, ignore_index=True)
    return merged.sort_values(["gene", "snp", "p_value"]).reset_index(drop=True)


def summarize_eqtl_stability(env_eqtl: pd.DataFrame) -> pd.DataFrame:
    """Summarize eQTL consistency across habitats."""
    if env_eqtl.empty:
        return pd.DataFrame(columns=["gene", "snp", "habitats_detected", "effect_sign_consistent"])
    grouped = []
    for (gene, snp), sub in env_eqtl.groupby(["gene", "snp"]):
        signs = np.sign(sub["effect_size"].values)
        sign_consistent = int(np.all(signs == signs[0]))
        grouped.append(
            {
                "gene": gene,
                "snp": snp,
                "habitats_detected": int(sub["habitat"].nunique()),
                "effect_sign_consistent": sign_consistent,
                "best_p": float(sub["p_value"].min()),
                "mean_abs_effect": float(sub["effect_size"].abs().mean()),
            }
        )
    return pd.DataFrame(grouped).sort_values(
        ["habitats_detected", "best_p"], ascending=[False, True]
    ).reset_index(drop=True)


def build_species_cooccurrence_edges(
    microbiome: pd.DataFrame,
    threshold: float = 0.35,
) -> pd.DataFrame:
    """Create species co-occurrence edges from abundance correlations."""
    corr = microbiome.corr()
    species = microbiome.columns.to_list()
    edges = []
    for i in range(len(species)):
        for j in range(i + 1, len(species)):
            weight = corr.iloc[i, j]
            if abs(weight) >= threshold:
                edges.append({"source": species[i], "target": species[j], "weight": float(weight)})
    return pd.DataFrame(edges)


def host_microbiome_links(
    expression: pd.DataFrame,
    microbiome: pd.DataFrame,
    top_n: int = 40,
) -> pd.DataFrame:
    """Compute host gene vs species abundance correlations."""
    pairs = []
    for gene in expression.columns:
        x = expression[gene].values
        for species in microbiome.columns:
            y = microbiome[species].values
            corr = float(np.corrcoef(x, y)[0, 1])
            if np.isnan(corr):
                continue
            pairs.append({"gene": gene, "species": species, "corr": corr, "abs_corr": abs(corr)})
    if not pairs:
        return pd.DataFrame(columns=["gene", "species", "corr", "abs_corr"])
    out = pd.DataFrame(pairs).sort_values("abs_corr", ascending=False).head(top_n).reset_index(drop=True)
    return out


def benchmark_trait_models(
    expression: pd.DataFrame,
    target: pd.Series,
    seed: int = 42,
    n_splits: int = 5,
) -> pd.DataFrame:
    """Compare baseline models with CV mean/std for R2 and MAE."""
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    models = {
        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=3,
            random_state=seed,
        ),
        "Ridge": Ridge(alpha=1.0),
        "GradientBoosting": GradientBoostingRegressor(random_state=seed),
    }

    rows = []
    for model_name, model in models.items():
        r2 = cross_val_score(model, expression, target, cv=cv, scoring="r2")
        mae = -cross_val_score(model, expression, target, cv=cv, scoring="neg_mean_absolute_error")
        rows.append(
            {
                "model": model_name,
                "cv_r2_mean": float(np.mean(r2)),
                "cv_r2_std": float(np.std(r2)),
                "cv_mae_mean": float(np.mean(mae)),
                "cv_mae_std": float(np.std(mae)),
            }
        )
    return pd.DataFrame(rows).sort_values("cv_r2_mean", ascending=False).reset_index(drop=True)


def _bootstrap_ci(values: np.ndarray, seed: int = 42, n_boot: int = 500) -> tuple[float, float]:
    """Bootstrap 95% CI from a metric vector."""
    rng = np.random.default_rng(seed)
    if len(values) == 0:
        return float("nan"), float("nan")
    draws = []
    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        draws.append(float(np.mean(sample)))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(lo), float(hi)


def evaluate_model_robustness(
    expression: pd.DataFrame,
    target: pd.Series,
    seed: int = 42,
    n_splits: int = 5,
    permutations: int = 40,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | str]]:
    """Return model comparison, permutation null distribution, and robustness summary."""
    benchmark = benchmark_trait_models(expression, target, seed=seed, n_splits=n_splits)
    best_model_name = str(benchmark.iloc[0]["model"])

    model_map = {
        "RandomForest": RandomForestRegressor(
            n_estimators=220,
            max_depth=8,
            min_samples_leaf=3,
            random_state=seed,
        ),
        "Ridge": Ridge(alpha=1.0),
        "GradientBoosting": GradientBoostingRegressor(random_state=seed),
    }
    best_model = model_map[best_model_name]
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=seed)

    real_r2 = cross_val_score(best_model, expression, target, cv=cv, scoring="r2")
    real_mae = -cross_val_score(best_model, expression, target, cv=cv, scoring="neg_mean_absolute_error")
    r2_ci_low, r2_ci_high = _bootstrap_ci(real_r2, seed=seed)

    rng = np.random.default_rng(seed + 17)
    perm_scores = []
    y = target.to_numpy()
    for _ in range(permutations):
        perm_y = rng.permutation(y)
        perm_r2 = cross_val_score(clone(best_model), expression, perm_y, cv=cv, scoring="r2")
        perm_scores.append(float(np.mean(perm_r2)))
    perm_df = pd.DataFrame({"perm_cv_r2_mean": perm_scores})

    actual_score = float(np.mean(real_r2))
    p_value = float((np.sum(perm_df["perm_cv_r2_mean"] >= actual_score) + 1) / (len(perm_df) + 1))
    summary = {
        "best_model": best_model_name,
        "cv_r2_mean": actual_score,
        "cv_r2_ci_low": r2_ci_low,
        "cv_r2_ci_high": r2_ci_high,
        "cv_mae_mean": float(np.mean(real_mae)),
        "permutation_p_value": p_value,
    }
    return benchmark, perm_df, summary


def build_candidate_validation_plan(
    genotype: pd.DataFrame,
    expression: pd.DataFrame,
    metadata: pd.DataFrame,
    seed: int = 42,
    target_trait: str = "stress_tolerance_index",
    top_n_genes: int = 8,
) -> pd.DataFrame:
    """Create a practical candidate-to-validation table for interview discussion."""
    if target_trait not in metadata.columns:
        return pd.DataFrame(columns=["gene", "ai_rank", "priority_score", "recommended_validation"])

    _, importances, _ = train_trait_model(expression, metadata[target_trait], seed=seed)
    eqtl = run_eqtl_scan(genotype, expression, min_abs_effect=0.05)
    env = run_environment_eqtl_scan(genotype, expression, metadata)
    stability = summarize_eqtl_stability(env)

    top_genes = importances.head(top_n_genes).copy().reset_index(drop=True)
    top_genes["ai_rank"] = np.arange(1, len(top_genes) + 1)

    records = []
    for _, row in top_genes.iterrows():
        gene = row["gene"]
        ai_importance = float(row["importance"])
        ai_rank = int(row["ai_rank"])

        gene_eqtl = eqtl[eqtl["gene"] == gene].sort_values("p_value")
        has_eqtl = int(not gene_eqtl.empty)
        best_snp = str(gene_eqtl.iloc[0]["snp"]) if has_eqtl else "n/a"
        best_p = float(gene_eqtl.iloc[0]["p_value"]) if has_eqtl else 1.0

        stable_hits = stability[stability["gene"] == gene]
        habitats_detected = int(stable_hits["habitats_detected"].max()) if not stable_hits.empty else 0

        priority = ai_importance + (0.15 if has_eqtl else 0.0) + (0.10 if habitats_detected >= 2 else 0.0)
        if has_eqtl and habitats_detected >= 2:
            rec = "qPCR across habitats + marker validation for best SNP"
        elif has_eqtl:
            rec = "marker validation under matched habitat + expression profiling"
        else:
            rec = "expression perturbation test and network-context validation"

        records.append(
            {
                "gene": gene,
                "ai_rank": ai_rank,
                "ai_importance": ai_importance,
                "best_snp": best_snp,
                "best_eqtl_p": best_p,
                "habitats_detected": habitats_detected,
                "priority_score": priority,
                "recommended_validation": rec,
            }
        )

    return pd.DataFrame(records).sort_values("priority_score", ascending=False).reset_index(drop=True)
