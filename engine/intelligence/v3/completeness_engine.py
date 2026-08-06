"""
ScoutVision DNA Engine v3
Completeness Engine

Responsibility:
- Evaluate the overall completeness of a competency profile.
- Keep completeness independent from identity confidence.

Alpha thresholds are experimental and require external validation.
"""

from typing import Dict

from engine.core.models.completeness_result import CompletenessResult


def calculate_completeness(
    competencies: Dict[str, float],
) -> CompletenessResult:

    values = list(competencies.values())

    if not values:
        return CompletenessResult(
            level=0.0,
            minimum=0.0,
            range=0.0,
            is_complete_candidate=False,
        )

    level = sum(values) / len(values)
    minimum = min(values)
    maximum = max(values)
    value_range = maximum - minimum

    is_complete_candidate = (
        level >= 70.0
        and minimum >= 60.0
        and value_range <= 25.0
    )

    return CompletenessResult(
        level=round(level, 1),
        minimum=round(minimum, 1),
        range=round(value_range, 1),
        is_complete_candidate=is_complete_candidate,
    )
