"""
ScoutVision V3
Cross-League Stability Engine

Responsibility:
- Compare numerical model behaviour across competitions.
- Measure stability without imposing arbitrary pass/fail thresholds.
"""

from typing import Iterable

import pandas as pd

from engine.validation.cross_league.models import (
    CrossLeagueResult,
    MetricStabilityResult,
)


DEFAULT_METRICS = (
    "Primary Score",
    "Gap",
    "Dominance",
    "Distribution",
    "Confidence Raw",
    "Versatility Score",
    "Completeness Level",
)


class CrossLeagueStabilityEngine:

    def evaluate(
        self,
        league_a: str,
        league_b: str,
        data_a: pd.DataFrame,
        data_b: pd.DataFrame,
        metrics: Iterable[str] = DEFAULT_METRICS,
    ) -> CrossLeagueResult:

        if data_a.empty or data_b.empty:
            raise ValueError(
                "Cross-league validation requires "
                "non-empty datasets."
            )

        results = {}

        for metric in metrics:

            if metric not in data_a.columns:
                raise ValueError(
                    f"Metric '{metric}' missing from {league_a}."
                )

            if metric not in data_b.columns:
                raise ValueError(
                    f"Metric '{metric}' missing from {league_b}."
                )

            mean_a = float(data_a[metric].mean())
            mean_b = float(data_b[metric].mean())

            absolute_difference = abs(
                mean_a - mean_b
            )

            reference = (
                (abs(mean_a) + abs(mean_b)) / 2
            )

            relative_difference = (
                absolute_difference / reference * 100
                if reference > 0
                else 0.0
            )

            results[metric] = MetricStabilityResult(
                metric=metric,
                league_a_mean=round(mean_a, 2),
                league_b_mean=round(mean_b, 2),
                absolute_difference=round(
                    absolute_difference,
                    2,
                ),
                relative_difference=round(
                    relative_difference,
                    2,
                ),
            )

        return CrossLeagueResult(
            league_a=league_a,
            league_b=league_b,
            players_a=len(data_a),
            players_b=len(data_b),
            metric_stability=results,
        )


def evaluate_position_stability(
    data_a: pd.DataFrame,
    data_b: pd.DataFrame,
    metrics=DEFAULT_METRICS,
):
    """
    Compare model behaviour within matching position groups.
    """

    positions_a = set(
        data_a["Position Group"].dropna().unique()
    )

    positions_b = set(
        data_b["Position Group"].dropna().unique()
    )

    common_positions = sorted(
        positions_a.intersection(positions_b)
    )

    results = {}

    for position in common_positions:

        group_a = data_a[
            data_a["Position Group"] == position
        ]

        group_b = data_b[
            data_b["Position Group"] == position
        ]

        metric_results = {}

        for metric in metrics:

            mean_a = float(group_a[metric].mean())
            mean_b = float(group_b[metric].mean())

            absolute_difference = abs(
                mean_a - mean_b
            )

            reference = (
                abs(mean_a) + abs(mean_b)
            ) / 2

            relative_difference = (
                absolute_difference / reference * 100
                if reference > 0
                else 0.0
            )

            metric_results[metric] = {
                "league_a_mean": round(mean_a, 2),
                "league_b_mean": round(mean_b, 2),
                "absolute_difference": round(
                    absolute_difference,
                    2,
                ),
                "relative_difference": round(
                    relative_difference,
                    2,
                ),
            }

        results[position] = {
            "players_a": len(group_a),
            "players_b": len(group_b),
            "metrics": metric_results,
        }

    return results
