"""ScoutVision Tactical Fit V1 scoring engine."""

from __future__ import annotations

from typing import Mapping, Any

from .role_library import ROLE_LIBRARY


class TacticalFitError(ValueError):
    """Raised when Tactical Fit cannot evaluate the supplied profile."""


def calculate_role_fit(
    competencies: Mapping[str, float],
    role: Mapping[str, Any],
) -> float:
    """Calculate weighted tactical-role fit on a 0-100 scale."""

    weights = role["weights"]

    missing = [
        name for name in weights
        if name not in competencies
    ]

    if missing:
        raise TacticalFitError(
            f"Missing competencies: {', '.join(missing)}"
        )

    score = sum(
        float(competencies[name]) * float(weight)
        for name, weight in weights.items()
    )

    return round(score, 1)


def evaluate_position_fit(
    formation: str,
    position_group: str,
    competencies: Mapping[str, float],
) -> list[dict[str, Any]]:
    """Rank all compatible tactical roles for a position."""

    if formation not in ROLE_LIBRARY:
        raise TacticalFitError(
            f"Unknown formation: {formation}"
        )

    formation_roles = ROLE_LIBRARY[formation]

    if position_group not in formation_roles:
        raise TacticalFitError(
            f"{position_group} is not configured for {formation}"
        )

    results = []

    for role_key, role in formation_roles[position_group].items():

        score = calculate_role_fit(
            competencies,
            role,
        )

        results.append(
            {
                "formation": formation,
                "position_group": position_group,
                "role_key": role_key,
                "role": role["title"],
                "fit_score": score,
            }
        )

    return sorted(
        results,
        key=lambda item: item["fit_score"],
        reverse=True,
    )
