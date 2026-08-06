"""
ScoutVision DNA Engine v3
Versatility Engine

Responsibility:
- Measure how balanced a player's competency profile is.
"""

from typing import Dict


def calculate_versatility(
    competencies: Dict[str, float]
):
    """
    Calculate versatility metrics from competency scores.
    """

    values = list(competencies.values())

    if not values:
        return {
            "score": 0,
            "range": 0,
            "dominance": 0,
            "balanced": False,
        }

    highest = max(values)
    lowest = min(values)

    ordered = sorted(values, reverse=True)

    second = ordered[1] if len(ordered) > 1 else ordered[0]

    value_range = highest - lowest
    dominance = highest - second

    versatility_score = max(
        0,
        round(
            100
            - (value_range * 2)
            - dominance,
            1,
        ),
    )

    balanced = (
        value_range <= 25
        and
        dominance <= 8
    )

    return {
        "score": versatility_score,
        "range": value_range,
        "dominance": dominance,
        "balanced": balanced,
    }
