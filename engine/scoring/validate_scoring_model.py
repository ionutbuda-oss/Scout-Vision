"""Validate ScoutVision Scoring Methodology v1.0 against a rankings workbook."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from engine.scoring.profile_models import ROLE_MODELS, validate_role_models

DEFAULT_RANKINGS = Path("outputs/rankings/France_L3_U25_rankings.xlsx")
TOLERANCE = 0.11


def validate_rankings(path: Path) -> dict[str, int]:
    validate_role_models()
    df = pd.read_excel(path, sheet_name="All Ranked")
    errors: list[str] = []
    checked = 0

    for position_group, model in ROLE_MODELS.items():
        group = df[df["Position Group"].astype(str) == position_group].copy()
        if group.empty:
            continue
        competency_columns = [f"{name} Score" for name in model]
        missing = [c for c in competency_columns if c not in group.columns]
        if missing:
            errors.append(f"{position_group}: missing {', '.join(missing)}")
            continue

        expected_performance = group[competency_columns].mean(axis=1)
        actual_performance = pd.to_numeric(group["Performance Score"], errors="coerce")
        bad_perf = (expected_performance - actual_performance).abs() > TOLERANCE
        if bad_perf.any():
            errors.append(f"{position_group}: {int(bad_perf.sum())} invalid Performance Scores")

        expected_scout = sum(
            pd.to_numeric(group[f"{name} Score"], errors="coerce") * float(config["weight"])
            for name, config in model.items()
        )
        scout_col = "Scout Score" if "Scout Score" in group.columns else "Recruitment Score"
        actual_scout = pd.to_numeric(group[scout_col], errors="coerce")
        bad_scout = (expected_scout - actual_scout).abs() > TOLERANCE
        if bad_scout.any():
            errors.append(f"{position_group}: {int(bad_scout.sum())} invalid Scout Scores")

        if "Recruitment Score" in group.columns and "Scout Score" in group.columns:
            alias_bad = (
                pd.to_numeric(group["Recruitment Score"], errors="coerce")
                - pd.to_numeric(group["Scout Score"], errors="coerce")
            ).abs() > 0.01
            if alias_bad.any():
                errors.append(f"{position_group}: Recruitment Score alias mismatch")

        score_cols = competency_columns + ["Performance Score", scout_col]
        for column in score_cols:
            values = pd.to_numeric(group[column], errors="coerce")
            if values.isna().any() or ((values < 0) | (values > 100)).any():
                errors.append(f"{position_group}: invalid range/missing values in {column}")
        checked += len(group)

    if errors:
        raise ValueError("ScoutVision scoring validation failed:\n- " + "\n- ".join(errors))
    return {"players_checked": checked, "position_models": len(ROLE_MODELS)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ScoutVision Scoring Methodology v1.0")
    parser.add_argument("--rankings", type=Path, default=DEFAULT_RANKINGS)
    args = parser.parse_args()
    summary = validate_rankings(args.rankings)
    print("=" * 68)
    print("SCOUTVISION SCORING MODEL v1.0 — VALIDATED")
    print(f"Players checked: {summary['players_checked']}")
    print(f"Position models: {summary['position_models']}")
    print("=" * 68)

if __name__ == "__main__":
    main()
