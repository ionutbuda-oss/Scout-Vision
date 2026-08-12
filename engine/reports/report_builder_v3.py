"""Build transparent ScoutVision recruitment-report data from real rankings."""

from __future__ import annotations

import base64
import html
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

from .summary_generator_v3 import generate_executive_summary_v3

import pandas as pd

from engine.tactical_fit.v1.fit_engine import (
    TacticalFitError,
    evaluate_position_fit,
)
from engine.tactical_fit.v1.role_library import ROLE_LIBRARY
from engine.intelligence.v3.dna_engine_v3 import build_player_dna_v3

try:
    from engine.scoring.profile_models import ROLE_MODELS
except ModuleNotFoundError:
    from engine.score_players import ROLE_MODELS


class ReportDataError(RuntimeError):
    """Raised when a report cannot be built truthfully from available data."""


SCORE_ALIASES = {
    "Distribution": ("Distribution Score", "Build-up Score"),
    "Offensive Duels": ("Offensive Duels Score", "Duels Score"),
}


def safe_filename(value: object) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]+", "_", ascii_value).strip("_").lower() or "unknown"


def clean_text(value: object, default: str = "N/A") -> str:
    if value is None or pd.isna(value):
        return default
    result = str(value).strip()
    return default if not result or result.lower() in {"nan", "none", "<na>"} else result


def number(value: object, default: float = 0.0) -> float:
    converted = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return float(default if pd.isna(converted) else converted)


def integer(value: object, default: int = 0) -> int:
    return int(round(number(value, default)))


def format_metric(metric: str, value: object) -> str:
    converted = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(converted):
        return "N/A"
    numeric = float(converted)
    if "%" in metric:
        return f"{numeric:.1f}%"
    if "per 90" in metric.lower():
        return f"{numeric:.2f}"
    return f"{numeric:.2f}"


def metric_display_name(metric: str) -> str:
    names = {
        "Accurate progressive passes, %": "Accurate progressive passes",
        "Accurate passes to final third, %": "Accurate final-third passes",
        "Accurate forward passes, %": "Accurate forward passes",
        "Accurate smart passes, %": "Accurate smart passes",
        "Accurate through passes, %": "Accurate through passes",
        "Successful dribbles, %": "Successful dribbles",
        "Defensive duels won, %": "Defensive duels won",
        "Offensive duels won, %": "Offensive duels won",
        "Accurate crosses, %": "Accurate crosses",
        "Goal conversion, %": "Goal conversion",
    }
    return names.get(metric, metric)


def _score_column(row: pd.Series, competency: str) -> str:
    candidates = SCORE_ALIASES.get(competency, (f"{competency} Score",))
    for candidate in candidates:
        if candidate in row.index and not pd.isna(row[candidate]):
            return candidate
    expected = ", ".join(candidates)
    raise ReportDataError(
        f"Missing score for '{competency}'. Expected one of: {expected}. "
        "Regenerate the rankings workbook after methodology changes."
    )


def _percentile(row: pd.Series, metric: str) -> float | None:
    column = f"PCTL | {metric}"
    if column not in row.index or pd.isna(row[column]):
        return None
    return number(row[column])


def _confidence(row: pd.Series) -> dict[str, Any]:
    if "Sample Confidence" in row.index and not pd.isna(row["Sample Confidence"]):
        value = number(row["Sample Confidence"])
    else:
        minutes = integer(row.get("Minutes played"))
        value = min(100.0, minutes / 18.0) if minutes else 0.0

    if value >= 75:
        label = "HIGH"
    elif value >= 50:
        label = "MEDIUM"
    else:
        label = "LOW"
    return {"value": round(value, 1), "display": f"{value:.0f}", "label": label}


def _label_lines(label: str) -> list[str]:
    words = label.split()
    if len(label) <= 15 or len(words) == 1:
        return [label]
    midpoint = max(1, len(words) // 2)
    return [" ".join(words[:midpoint]), " ".join(words[midpoint:])]


def radar_svg_data_uri(competencies: list[dict[str, Any]]) -> str:
    width, height, cx, cy, radius, label_radius = 620, 450, 310, 220, 125, 205
    count = len(competencies)
    angles = [(-math.pi / 2) + (2 * math.pi * i / count) for i in range(count)]

    def point(angle: float, scale: float) -> tuple[float, float]:
        return cx + math.cos(angle) * radius * scale, cy + math.sin(angle) * radius * scale

    grids = []
    for level in (0.25, 0.5, 0.75, 1.0):
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in [point(a, level) for a in angles])
        grids.append(f'<polygon points="{coords}" fill="none" stroke="#28445f" stroke-width="1"/>')

    axes = []
    for angle in angles:
        x, y = point(angle, 1.0)
        axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#28445f" stroke-width="1"/>')

    score_points = [point(a, c["score"] / 100.0) for a, c in zip(angles, competencies)]
    score_coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in score_points)

    labels, nodes = [], []
    for angle, competency, (x, y) in zip(angles, competencies, score_points):
        nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#2f80ff" stroke="#90c2ff" stroke-width="2"/>')
        lx = cx + math.cos(angle) * label_radius
        ly = cy + math.sin(angle) * label_radius
        anchor = "middle"
        if math.cos(angle) > 0.30:
            anchor = "start"
        elif math.cos(angle) < -0.30:
            anchor = "end"
        lines = _label_lines(competency["name"])
        first_y = ly - (8 if len(lines) == 2 else 0)
        tspans = "".join(
            f'<tspan x="{lx:.1f}" dy="{0 if idx == 0 else 16}">{html.escape(line)}</tspan>'
            for idx, line in enumerate(lines)
        )
        score_y = first_y + (29 if len(lines) == 2 else 20)
        labels.append(
            f'<text x="{lx:.1f}" y="{first_y:.1f}" text-anchor="{anchor}" fill="#edf6ff" '
            f'font-family="Arial, sans-serif" font-size="14" font-weight="600">{tspans}</text>'
            f'<text x="{lx:.1f}" y="{score_y:.1f}" text-anchor="{anchor}" fill="#55a3ff" '
            f'font-family="Arial, sans-serif" font-size="14" font-weight="800">{competency["score_display"]}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2388ff" stop-opacity=".43"/><stop offset="100%" stop-color="#123b77" stop-opacity=".28"/></linearGradient></defs>
    {''.join(grids)}{''.join(axes)}
    <polygon points="{score_coords}" fill="url(#area)" stroke="#2f80ff" stroke-width="3"/>
    {''.join(nodes)}{''.join(labels)}</svg>'''
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def display_formation(formation: str) -> str:
    if formation and not formation.startswith("1-"):
        return f"1-{formation}"
    return formation


def build_report_context(
    row: pd.Series,
    *,
    competition_name: str,
    ranked_frame: pd.DataFrame | None = None,
) -> dict[str, Any]:
    required = {"Player", "Team", "Position", "Position Group", "Age", "Matches played", "Performance Score"}
    missing = sorted(required.difference(row.index))
    if missing:
        raise ReportDataError("Missing required columns: " + ", ".join(missing))

    position_group = clean_text(row["Position Group"])
    if position_group not in ROLE_MODELS:
        raise ReportDataError(f"No active model for position group '{position_group}'.")

    competencies: list[dict[str, Any]] = []
    kpi_groups: list[dict[str, Any]] = []
    supporting_indicators: list[dict[str, Any]] = []

    for competency_name, config in ROLE_MODELS[position_group].items():

        competency_weight = float(config["weight"])

        # All competencies remain available for DNA and tactical evaluation.
        score = number(row[_score_column(row, competency_name)])

        competencies.append({
            "name": competency_name,
            "score": round(score, 2),
            "score_display": f"{score:.0f}",
            "weight": f"{competency_weight * 100:.0f}%",
        })

        metrics = []

        for metric_name, metric_weight in config["metrics"].items():

            if metric_name not in row.index:
                metric_entry = {
                    "source_name": metric_name,
                    "name": metric_display_name(metric_name),
                    "value": "N/A",
                    "weight": f"{float(metric_weight) * 100:.0f}%",
                    "percentile": None,
                }
            else:
                percentile = _percentile(row, metric_name)

                metric_entry = {
                    "source_name": metric_name,
                    "name": metric_display_name(metric_name),
                    "value": format_metric(metric_name, row[metric_name]),
                    "weight": f"{float(metric_weight) * 100:.0f}%",
                    "percentile": None if percentile is None else round(percentile),
                }

            metrics.append(metric_entry)

            # Weight 0 metrics are displayed only as supporting information.
            if competency_weight == 0 and metric_entry["value"] != "N/A":
                supporting_indicators.append({
                    "name": metric_entry["name"],
                    "value": metric_entry["value"],
                    "percentile": metric_entry["percentile"],
                })

        # Only weighted competencies are recruitment KPIs.
        if competency_weight > 0:
            kpi_groups.append({
                "name": competency_name,
                "weight": f"{competency_weight * 100:.0f}%",
                "metrics": metrics,
            })


    dna_v3 = build_player_dna_v3(
        position_group,
        {
            item["name"]: item["score"]
            for item in competencies
        },
    )
    # Convert internal DNA classification into club-facing language.
    identity_type = dna_v3["identity_type"]

    profile_type_map = {
        "Clear Specialist": "CLEAR SPECIALIST PROFILE",
        "Specialist": "SPECIALIST PROFILE",
        "Hybrid Candidate": "VERSATILE PROFILE",
        "Complete Candidate": "COMPLETE PROFILE",
        "Uncertain": "MULTI-ROLE PROFILE",
    }

    profile_type = profile_type_map.get(
        identity_type,
        "PLAYER PROFILE",
    )

    development = min(competencies, key=lambda item: item["score"])
    score_column = "Scout Score" if "Scout Score" in row.index else "Recruitment Score"
    if score_column not in row.index:
        raise ReportDataError("Missing Scout Score / Recruitment Score column.")
    recruitment = number(row[score_column])
    performance = number(row["Performance Score"])

    position_rank = None
    position_pool = None
    top_percent = None
    if ranked_frame is not None and "Position Group" in ranked_frame.columns:
        pool = ranked_frame.loc[
            ranked_frame["Position Group"].astype(str) == position_group
        ].copy()
        if not pool.empty:
            pool_score_column = (
                "Scout Score"
                if "Scout Score" in pool.columns
                else "Recruitment Score"
            )
            pool[pool_score_column] = pd.to_numeric(
                pool[pool_score_column], errors="coerce"
            )
            pool["Performance Score"] = pd.to_numeric(
                pool["Performance Score"], errors="coerce"
            )
            pool = pool.sort_values(
                [pool_score_column, "Performance Score"],
                ascending=[False, False],
                na_position="last",
            ).reset_index(drop=True)
            names = pool["Player"].astype(str).str.strip().str.casefold()
            target = clean_text(row["Player"]).casefold()
            matches = names[names == target]
            if not matches.empty:
                position_rank = int(matches.index[0]) + 1
                position_pool = int(len(pool))
                top_percent = max(1, math.ceil(position_rank / position_pool * 100))

    executive_summary = generate_executive_summary_v3(
        competencies=competencies,
        dna_v3=dna_v3,
        profile_type=profile_type,
    )

    # --------------------------------------------------------
    # TACTICAL FIT
    # --------------------------------------------------------

    competency_scores = {
        item["name"]: float(item["score"])
        for item in competencies
    }

    tactical_formations = []

    for formation in ROLE_LIBRARY:

        if position_group not in ROLE_LIBRARY[formation]:
            continue

        try:
            role_results = evaluate_position_fit(
                formation=formation,
                position_group=position_group,
                competencies=competency_scores,
            )
        except TacticalFitError:
            continue

        tactical_roles = []

        for result in role_results:
            tactical_roles.append({
                "role_key": result["role_key"],
                "role": result["role"],
                "fit_score": float(result["fit_score"]),
                "fit_display": f"{float(result['fit_score']):.1f}",
                "eligible": bool(result["eligible"]),
                "failed_minimums": result["failed_minimums"],
            })

        eligible_roles = [
            role
            for role in tactical_roles
            if role["eligible"]
        ]

        best_role = (
            eligible_roles[0]
            if eligible_roles
            else None
        )

        tactical_formations.append({
            "formation": display_formation(formation),
            "roles": tactical_roles,
            "best_role": best_role,
        })

    eligible_tactical_roles = [
        {
            "formation": formation["formation"],
            **role,
        }
        for formation in tactical_formations
        for role in formation["roles"]
        if role["eligible"]
    ]

    best_tactical_fit = (
        max(
            eligible_tactical_roles,
            key=lambda item: item["fit_score"],
        )
        if eligible_tactical_roles
        else None
    )

    tactical_fit = {
        "available": bool(tactical_formations),
        "formations": tactical_formations,
        "best_overall": best_tactical_fit,
    }

    context = {
        "player": {
            "name": clean_text(row["Player"]),
            "team": clean_text(row["Team"]),
            "position": clean_text(row["Position"]),
            "position_group": position_group,
            "competition": competition_name,
            "age": integer(row["Age"]),
            "foot": clean_text(row.get("Foot")).title(),
            "minutes": f"{integer(row.get('Minutes played')):,}" if integer(row.get("Minutes played")) > 0 else "N/A",
            "matches": integer(row["Matches played"]),
            "recommendation": clean_text(row.get("Recommendation")),
            "position_rank": position_rank,
            "position_pool": position_pool,
            "top_percent": top_percent,
        },
        "score": {
            "value": recruitment,
            "display": f"{recruitment:.1f}",
            "performance": f"{performance:.1f}",
        },
        "confidence": _confidence(row),
        "competencies": competencies,
        "kpi_groups": kpi_groups,
        "supporting_indicators": supporting_indicators,
        "player_dna": dna_v3,
        "profile_type": profile_type,
        "development": development,
        "executive_summary": executive_summary,
        "tactical_fit": tactical_fit,
    }
    minutes = integer(row.get("Minutes played"))
    matches_played = integer(row.get("Matches played"))
    available_percentiles = sum(
        metric["percentile"] is not None
        for group in kpi_groups
        for metric in group["metrics"]
    )
    total_metrics = sum(len(group["metrics"]) for group in kpi_groups)
    completeness = round(available_percentiles / total_metrics * 100) if total_metrics else 0
    context["evidence_note"] = (
        f"Based on {minutes:,} minutes across {matches_played} matches; "
        f"percentile coverage is available for {completeness}% of model KPIs."
    )
    context["radar_uri"] = radar_svg_data_uri(competencies)
    return context
