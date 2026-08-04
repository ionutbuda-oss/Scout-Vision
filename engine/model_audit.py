"""
ScoutVision Model Audit.

Audits the active scoring methodology and the latest rankings output.

Checks:
- competency weights total 100%;
- KPI weights total 100%;
- every required KPI exists in the prepared database;
- repeated KPIs inside the same position model;
- missing or invalid competency scores;
- score ranges and distributions;
- top, middle and bottom players by position;
- sample confidence based on minutes played.

Run from the project root:

    python3 -m engine.validation.model_audit

Optional paths:

    python3 -m engine.validation.model_audit \
        --prepared outputs/prepared/France_L3_U25_prepared.xlsx \
        --rankings outputs/rankings/France_L3_U25_rankings.xlsx

Output:

    outputs/audit/ScoutVision_Model_Audit.md
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from engine.scoring.profile_models import (
    ROLE_MODELS,
    iter_required_metrics,
    validate_role_models,
)


DEFAULT_PREPARED = Path(
    "outputs/prepared/France_L3_U25_prepared.xlsx"
)
DEFAULT_RANKINGS = Path(
    "outputs/rankings/France_L3_U25_rankings.xlsx"
)
DEFAULT_OUTPUT = Path(
    "outputs/audit/ScoutVision_Model_Audit.md"
)


def _confidence_label(minutes: float) -> str:
    """Return a simple sample-confidence label."""

    if pd.isna(minutes):
        return "Unknown"
    if minutes >= 1800:
        return "High"
    if minutes >= 900:
        return "Medium"
    return "Low"


def _safe_float(value: Any) -> float:
    number = pd.to_numeric(
        pd.Series([value]),
        errors="coerce",
    ).iloc[0]
    return float(number) if not pd.isna(number) else math.nan


def _format_number(value: Any, decimals: int = 1) -> str:
    number = _safe_float(value)
    if math.isnan(number):
        return "N/A"
    return f"{number:.{decimals}f}"


def _load_excel_sheet(
    path: Path,
    preferred_sheet: str | None = None,
) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if preferred_sheet is None:
        return pd.read_excel(path)

    try:
        return pd.read_excel(path, sheet_name=preferred_sheet)
    except ValueError:
        return pd.read_excel(path)


def _audit_methodology(
    prepared: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Return methodology report lines and critical errors."""

    lines: list[str] = []
    critical: list[str] = []

    lines.append("## 1. Methodology integrity")
    lines.append("")

    try:
        validate_role_models()
        lines.append("- ✅ All competency and KPI weights total 100%.")
    except ValueError as exc:
        critical.append(str(exc))
        lines.append(f"- ❌ Weight validation failed: `{exc}`")

    required_metrics = list(iter_required_metrics())
    missing_metrics = [
        metric
        for metric in required_metrics
        if metric not in prepared.columns
    ]

    lines.append(
        f"- Required scoring KPIs: **{len(required_metrics)}**."
    )

    if missing_metrics:
        critical.extend(
            f"Missing KPI: {metric}"
            for metric in missing_metrics
        )
        lines.append(
            f"- ❌ Missing KPIs: **{len(missing_metrics)}**."
        )
        for metric in missing_metrics:
            lines.append(f"  - `{metric}`")
    else:
        lines.append(
            "- ✅ Every required KPI exists in the prepared database."
        )

    lines.append("")
    lines.append("### Repeated KPIs inside each position model")
    lines.append("")
    lines.append(
        "Repeated KPIs are not automatically errors, but they should be "
        "reviewed because they can influence more than one competency."
    )
    lines.append("")

    for position_group, model in ROLE_MODELS.items():
        metrics: list[str] = []

        for category in model.values():
            metrics.extend(category["metrics"].keys())

        repeated = sorted(
            metric
            for metric, count in Counter(metrics).items()
            if count > 1
        )

        if repeated:
            lines.append(
                f"- **{position_group}:** "
                + ", ".join(f"`{metric}`" for metric in repeated)
            )
        else:
            lines.append(
                f"- **{position_group}:** no repeated KPIs."
            )

    lines.append("")
    return lines, critical


def _find_minutes_column(df: pd.DataFrame) -> str | None:
    candidates = [
        "Minutes played",
        "Minutes",
        "Minutes Played",
    ]
    return next(
        (column for column in candidates if column in df.columns),
        None,
    )


def _audit_position_scores(
    rankings: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Audit score distributions and player ranking samples."""

    lines: list[str] = []
    critical: list[str] = []

    required_columns = {
        "Player",
        "Position Group",
        "Recruitment Score",
        "Performance Score",
    }
    missing = sorted(required_columns.difference(rankings.columns))

    lines.append("## 2. Score integrity")
    lines.append("")

    if missing:
        message = (
            "Rankings file is missing columns: "
            + ", ".join(missing)
        )
        critical.append(message)
        lines.append(f"- ❌ {message}")
        lines.append("")
        return lines, critical

    rankings = rankings.copy()
    rankings["Recruitment Score"] = pd.to_numeric(
        rankings["Recruitment Score"],
        errors="coerce",
    )
    rankings["Performance Score"] = pd.to_numeric(
        rankings["Performance Score"],
        errors="coerce",
    )

    invalid_recruitment = rankings[
        rankings["Recruitment Score"].isna()
        | (rankings["Recruitment Score"] < 0)
        | (rankings["Recruitment Score"] > 100)
    ]

    invalid_performance = rankings[
        rankings["Performance Score"].isna()
        | (rankings["Performance Score"] < 0)
        | (rankings["Performance Score"] > 100)
    ]

    if invalid_recruitment.empty:
        lines.append(
            "- ✅ All Recruitment Scores are valid values from 0 to 100."
        )
    else:
        critical.append(
            f"{len(invalid_recruitment)} invalid Recruitment Scores."
        )
        lines.append(
            f"- ❌ Invalid Recruitment Scores: "
            f"**{len(invalid_recruitment)}**."
        )

    if invalid_performance.empty:
        lines.append(
            "- ✅ All Performance Scores are valid values from 0 to 100."
        )
    else:
        critical.append(
            f"{len(invalid_performance)} invalid Performance Scores."
        )
        lines.append(
            f"- ❌ Invalid Performance Scores: "
            f"**{len(invalid_performance)}**."
        )

    lines.append("")
    lines.append("### Score distribution by position")
    lines.append("")
    lines.append(
        "| Position | Players | Minimum | Median | Mean | Maximum |"
    )
    lines.append(
        "|---|---:|---:|---:|---:|---:|"
    )

    grouped = rankings.groupby(
        "Position Group",
        dropna=False,
    )

    for position_group, group in grouped:
        scores = group["Recruitment Score"].dropna()

        if scores.empty:
            continue

        lines.append(
            f"| {position_group} | {len(scores)} | "
            f"{scores.min():.1f} | {scores.median():.1f} | "
            f"{scores.mean():.1f} | {scores.max():.1f} |"
        )

    lines.append("")
    return lines, critical


def _player_sample_table(
    group: pd.DataFrame,
    minutes_column: str | None,
) -> list[str]:
    """Create top/middle/bottom validation samples."""

    group = group.sort_values(
        "Recruitment Score",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    count = len(group)
    if count == 0:
        return []

    indices: list[int] = []

    indices.extend(range(min(5, count)))

    middle_start = max(
        0,
        min(
            count - 5,
            (count // 2) - 2,
        ),
    )
    indices.extend(
        range(
            middle_start,
            min(middle_start + 5, count),
        )
    )

    indices.extend(
        range(max(0, count - 5), count)
    )

    indices = list(dict.fromkeys(indices))

    lines = [
        "| Rank | Player | Recruitment | Performance | Minutes | Confidence |",
        "|---:|---|---:|---:|---:|---|",
    ]

    for index in indices:
        row = group.iloc[index]
        minutes = (
            _safe_float(row.get(minutes_column))
            if minutes_column
            else math.nan
        )

        lines.append(
            f"| {index + 1} | {row['Player']} | "
            f"{_format_number(row['Recruitment Score'])} | "
            f"{_format_number(row['Performance Score'])} | "
            f"{'N/A' if math.isnan(minutes) else f'{minutes:.0f}'} | "
            f"{_confidence_label(minutes)} |"
        )

    return lines


def _audit_player_samples(
    rankings: pd.DataFrame,
) -> list[str]:
    """Create football-review samples for every position."""

    lines: list[str] = [
        "## 3. Player validation samples",
        "",
        (
            "Review the top five, five middle-ranked and bottom five "
            "players for every position using video and football judgement."
        ),
        "",
    ]

    minutes_column = _find_minutes_column(rankings)

    for position_group in ROLE_MODELS:
        group = rankings[
            rankings["Position Group"].astype(str)
            == position_group
        ].copy()

        if group.empty:
            lines.extend(
                [
                    f"### {position_group}",
                    "",
                    "No players found.",
                    "",
                ]
            )
            continue

        lines.extend(
            [
                f"### {position_group}",
                "",
                *_player_sample_table(
                    group,
                    minutes_column,
                ),
                "",
                "**Analyst review:**",
                "",
                "- Does the top five make football sense?",
                "- Is any player clearly overvalued?",
                "- Is any player clearly undervalued?",
                "- Does the strongest competency match the video profile?",
                "- Does sample confidence affect interpretation?",
                "",
            ]
        )

    return lines


def _audit_competency_columns(
    rankings: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    lines: list[str] = [
        "## 4. Competency-column audit",
        "",
    ]
    critical: list[str] = []

    for position_group, model in ROLE_MODELS.items():
        missing: list[str] = []
        invalid: list[str] = []

        for competency in model:
            column = f"{competency} Score"

            if column not in rankings.columns:
                missing.append(column)
                continue

            values = pd.to_numeric(
                rankings.loc[
                    rankings["Position Group"].astype(str)
                    == position_group,
                    column,
                ],
                errors="coerce",
            )

            if values.isna().any():
                invalid.append(
                    f"{column}: {int(values.isna().sum())} missing"
                )

            outside = values[
                (values < 0) | (values > 100)
            ]
            if not outside.empty:
                invalid.append(
                    f"{column}: {len(outside)} outside 0-100"
                )

        if missing or invalid:
            lines.append(f"- ❌ **{position_group}**")
            for item in missing:
                lines.append(f"  - Missing column: `{item}`")
                critical.append(
                    f"{position_group}: missing {item}"
                )
            for item in invalid:
                lines.append(f"  - {item}")
                critical.append(
                    f"{position_group}: {item}"
                )
        else:
            lines.append(
                f"- ✅ **{position_group}:** all competency columns valid."
            )

    lines.append("")
    return lines, critical


def generate_audit_report(
    prepared_path: Path,
    rankings_path: Path,
    output_path: Path,
) -> Path:
    prepared = _load_excel_sheet(prepared_path)
    rankings = _load_excel_sheet(
        rankings_path,
        preferred_sheet="All Ranked",
    )

    sections: list[str] = [
        "# ScoutVision Model Audit",
        "",
        "## Audit scope",
        "",
        f"- Prepared database: `{prepared_path}`",
        f"- Rankings database: `{rankings_path}`",
        f"- Prepared players: **{len(prepared)}**",
        f"- Ranked players: **{len(rankings)}**",
        "",
    ]
    critical_errors: list[str] = []

    methodology_lines, methodology_errors = _audit_methodology(
        prepared
    )
    sections.extend(methodology_lines)
    critical_errors.extend(methodology_errors)

    score_lines, score_errors = _audit_position_scores(
        rankings
    )
    sections.extend(score_lines)
    critical_errors.extend(score_errors)

    competency_lines, competency_errors = (
        _audit_competency_columns(rankings)
    )
    sections.extend(competency_lines)
    critical_errors.extend(competency_errors)

    sections.extend(_audit_player_samples(rankings))

    sections.extend(
        [
            "## 5. Audit conclusion",
            "",
        ]
    )

    if critical_errors:
        sections.append(
            f"**Status: FAILED — {len(critical_errors)} critical issue(s).**"
        )
        sections.append("")
        for error in critical_errors:
            sections.append(f"- {error}")
    else:
        sections.append(
            "**Status: PASSED — no critical mathematical or structural "
            "issues detected.**"
        )
        sections.append("")
        sections.append(
            "The next step is qualitative football validation of the "
            "player samples listed above."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        "\n".join(sections),
        encoding="utf-8",
    )

    return output_path.resolve()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit the active ScoutVision model."
    )
    parser.add_argument(
        "--prepared",
        type=Path,
        default=DEFAULT_PREPARED,
    )
    parser.add_argument(
        "--rankings",
        type=Path,
        default=DEFAULT_RANKINGS,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    try:
        report_path = generate_audit_report(
            prepared_path=args.prepared,
            rankings_path=args.rankings,
            output_path=args.output,
        )
    except Exception as exc:
        print(
            f"ScoutVision model audit failed: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    print("=" * 68)
    print("SCOUTVISION MODEL AUDIT")
    print("=" * 68)
    print("Audit completed successfully:")
    print(report_path)
    print("=" * 68)


if __name__ == "__main__":
    main()
