"""ScoutVision Tactical Fit V1 scoring engine."""

from __future__ import annotations

from typing import Mapping, Any

from .role_library import ROLE_LIBRARY


class TacticalFitError(ValueError):
    """Raised when Tactical Fit cannot evaluate the supplied profile."""


def calculate_role_fit(
    competencies: Mapping[str, float],
    role: Mapping[str, Any],
    archetype: str | None = None,
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

    # Archetype compatibility bonus
    if archetype:
        preferred = role.get(
            "preferred_archetypes",
            []
        )

        if archetype in preferred:
            score += 5.0

    return round(score, 1)


def evaluate_position_fit(
    formation: str,
    position_group: str,
    competencies: Mapping[str, float],
    archetype: str | None = None,
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
            archetype,
        )

        minimums = role.get("minimums", {})

        missing_minimum_competencies = [
            name
            for name in minimums
            if name not in competencies
        ]

        if missing_minimum_competencies:
            raise TacticalFitError(
                "Missing competencies required for role eligibility: "
                + ", ".join(missing_minimum_competencies)
            )

        eligible = all(
            float(competencies[name]) >= float(minimum)
            for name, minimum in minimums.items()
        )

        failed_minimums = {
            name: {
                "value": float(competencies[name]),
                "minimum": float(minimum),
            }
            for name, minimum in minimums.items()
            if float(competencies[name]) < float(minimum)
        }

        results.append(
            {
                "formation": formation,
                "position_group": position_group,
                "role_key": role_key,
                "role": role["title"],
                "fit_score": score,
                "eligible": eligible,
                "failed_minimums": failed_minimums,
            }
        )

    return sorted(
        results,
        key=lambda item: (
            item["eligible"],
            item["fit_score"],
        ),
        reverse=True,
    )
