"""Upload/download utilities for full workflow data exchange."""
from __future__ import annotations

from datetime import datetime, timezone
import io
import zipfile

import pandas as pd
import streamlit as st

from src.lettuce_project.core import (
    ProjectData,
    build_coexpression_edges,
    build_species_cooccurrence_edges,
    generate_synthetic_multiomics,
    host_microbiome_links,
    run_environment_eqtl_scan,
    run_eqtl_scan,
    summarize_eqtl_stability,
    summarize_network,
    train_trait_model,
)

REQUIRED_UPLOAD_FILES = ["genotype.csv", "expression.csv", "metadata.csv", "microbiome.csv"]
OPTIONAL_UPLOAD_FILES = ["causal_map.csv"]
SESSION_DATA_KEY = "active_project_data"
SESSION_SOURCE_KEY = "active_project_source"


def _resolve_member_name(members: list[str], target_name: str) -> str | None:
    """Find a zip member by exact basename match (case-insensitive)."""
    target = target_name.lower()
    for member in members:
        if member.endswith("/") or member.endswith("\\"):
            continue
        if member.split("/")[-1].split("\\")[-1].lower() == target:
            return member
    return None


def _coerce_index(df: pd.DataFrame, preferred: str = "sample_id") -> pd.DataFrame:
    """Use sample_id/ID-like first column as index if present."""
    if preferred in df.columns:
        return df.set_index(preferred)

    if not len(df.columns):
        return df

    first_col = df.columns[0]
    first_series = df[first_col]
    first_lower = str(first_col).strip().lower()
    has_id_like_name = "sample" in first_lower or "id" in first_lower or first_lower.startswith("unnamed")
    id_like_values = first_series.astype(str).str.match(r"^[A-Za-z_]+[0-9]+$").mean() > 0.6
    if has_id_like_name or id_like_values:
        return df.set_index(first_col)
    return df


def _validate_project_data(data: ProjectData) -> None:
    """Validate minimum schema and cross-table sample alignment."""
    required_meta = {"habitat", "population"}
    missing_meta = required_meta - set(data.metadata.columns)
    if missing_meta:
        raise ValueError(f"metadata.csv is missing required columns: {sorted(missing_meta)}")

    common = (
        set(data.genotype.index)
        & set(data.expression.index)
        & set(data.metadata.index)
        & set(data.microbiome.index)
    )
    if len(common) < 20:
        raise ValueError("Not enough overlapping sample IDs across uploaded tables (minimum 20).")


def parse_uploaded_bundle(file_bytes: bytes) -> ProjectData:
    """Parse project bundle zip into ProjectData."""
    with zipfile.ZipFile(io.BytesIO(file_bytes), mode="r") as zf:
        members = zf.namelist()
        missing = [name for name in REQUIRED_UPLOAD_FILES if _resolve_member_name(members, name) is None]
        if missing:
            raise ValueError(f"Upload zip is missing required files: {missing}")

        frames: dict[str, pd.DataFrame] = {}
        for name in REQUIRED_UPLOAD_FILES + OPTIONAL_UPLOAD_FILES:
            member = _resolve_member_name(members, name)
            if member is None:
                continue
            frames[name] = pd.read_csv(io.BytesIO(zf.read(member)))

    genotype = _coerce_index(frames["genotype.csv"])
    expression = _coerce_index(frames["expression.csv"])
    metadata = _coerce_index(frames["metadata.csv"])
    microbiome = _coerce_index(frames["microbiome.csv"])

    if "causal_map.csv" in frames:
        causal_map = frames["causal_map.csv"]
    else:
        causal_map = pd.DataFrame(columns=["gene", "causal_snp", "sim_effect"])

    data = ProjectData(
        genotype=genotype.sort_index(),
        expression=expression.sort_index(),
        metadata=metadata.sort_index(),
        causal_map=causal_map,
        microbiome=microbiome.sort_index(),
    )
    _validate_project_data(data)
    return data


def set_active_project_data(data: ProjectData, source_label: str) -> None:
    """Store active data in session state."""
    st.session_state[SESSION_DATA_KEY] = data
    st.session_state[SESSION_SOURCE_KEY] = source_label


def clear_active_project_data() -> None:
    """Switch app back to synthetic generator mode."""
    st.session_state.pop(SESSION_DATA_KEY, None)
    st.session_state.pop(SESSION_SOURCE_KEY, None)


def get_active_or_synthetic(seed: int) -> tuple[ProjectData, str]:
    """Return session-uploaded data if present; otherwise synthetic data."""
    if SESSION_DATA_KEY in st.session_state:
        source = st.session_state.get(SESSION_SOURCE_KEY, "Uploaded bundle")
        return st.session_state[SESSION_DATA_KEY], str(source)
    return generate_synthetic_multiomics(seed=seed), f"Synthetic dataset (seed={seed})"


def _write_df(zip_file: zipfile.ZipFile, name: str, df: pd.DataFrame) -> None:
    """Write DataFrame as UTF-8 CSV into zip."""
    zip_file.writestr(name, df.to_csv(index=True).encode("utf-8"))


def build_procedure_bundle(data: ProjectData, seed: int = 42) -> bytes:
    """Build downloadable zip with full workflow input/output artifacts."""
    eqtl = run_eqtl_scan(data.genotype, data.expression, min_abs_effect=0.05)
    env_eqtl = run_environment_eqtl_scan(data.genotype, data.expression, data.metadata)
    eqtl_stability = summarize_eqtl_stability(env_eqtl)
    coexp_edges = build_coexpression_edges(data.expression, threshold=0.65)
    coexp_degree = summarize_network(coexp_edges, data.expression.columns.tolist())
    microbe_edges = build_species_cooccurrence_edges(data.microbiome, threshold=0.35)
    host_microbe = host_microbiome_links(data.expression, data.microbiome, top_n=80)

    ai_rows = []
    ai_tables = {}
    target_candidates = [
        "stress_tolerance_index",
        "photosynthesis_efficiency_index",
        "zinc_homeostasis_index",
    ]
    for target in target_candidates:
        if target not in data.metadata.columns:
            continue
        _, importances, metrics = train_trait_model(data.expression, data.metadata[target], seed=seed)
        ai_rows.append({"target": target, "r2": metrics["r2"], "mae": metrics["mae"]})
        ai_tables[target] = importances
    ai_metrics = pd.DataFrame(ai_rows)

    out = io.BytesIO()
    with zipfile.ZipFile(out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Inputs
        _write_df(zf, "inputs/genotype.csv", data.genotype)
        _write_df(zf, "inputs/expression.csv", data.expression)
        _write_df(zf, "inputs/metadata.csv", data.metadata)
        _write_df(zf, "inputs/microbiome.csv", data.microbiome)
        _write_df(zf, "inputs/causal_map.csv", data.causal_map)

        # Outputs
        _write_df(zf, "outputs/eqtl_scan.csv", eqtl)
        _write_df(zf, "outputs/environment_eqtl.csv", env_eqtl)
        _write_df(zf, "outputs/eqtl_stability.csv", eqtl_stability)
        _write_df(zf, "outputs/coexpression_edges.csv", coexp_edges)
        _write_df(zf, "outputs/coexpression_degree.csv", coexp_degree)
        _write_df(zf, "outputs/species_cooccurrence_edges.csv", microbe_edges)
        _write_df(zf, "outputs/host_microbiome_links.csv", host_microbe)
        _write_df(zf, "outputs/ai_metrics.csv", ai_metrics)
        for target, table in ai_tables.items():
            _write_df(zf, f"outputs/ai_importance_{target}.csv", table)

        created = datetime.now(timezone.utc).isoformat()
        readme = f"""# Workflow Procedure Export

Created (UTC): {created}
Samples: {data.genotype.shape[0]}
SNPs: {data.genotype.shape[1]}
Genes: {data.expression.shape[1]}
Microbial species: {data.microbiome.shape[1]}

## Included folders
- `inputs/`: uploaded or synthetic input matrices
- `outputs/`: eQTL, GxE, network, host-microbiome, and AI outputs

## Notes
- AI metrics are generated for each available target trait column in metadata.
- This package is designed for reproducible review, interview walkthrough, and handoff.
"""
        zf.writestr("README_procedure.md", readme.encode("utf-8"))

    out.seek(0)
    return out.getvalue()
