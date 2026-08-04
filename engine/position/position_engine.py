"""
ScoutVision Position Engine v4.0
"""

from math import pow

from engine.position.position_models import POSITION_MODELS


PRIMARY_WEIGHT = 0.75
SUPPORT_WEIGHT = 0.25
CORE_EXPONENT = 1.5


def weighted_average(values, weights):

    if not weights:
        return 0.0

    total = sum(weights.values())

    if total == 0:
        return 0.0

    score = 0.0

    for competency, weight in weights.items():
        score += values.get(competency, 0) * weight

    return score / total


def calculate_position_score(position, competencies):

    model = POSITION_MODELS[position]

    core_score = weighted_average(
        competencies,
        model["core"]
    )

    primary_score = weighted_average(
        competencies,
        model["primary"]
    )

    support_score = weighted_average(
        competencies,
        model["support"]
    )

    multiplier = pow(core_score / 100.0, CORE_EXPONENT)

    recruitment_score = multiplier * (

        primary_score * PRIMARY_WEIGHT +

        support_score * SUPPORT_WEIGHT

    )

    return {

        "position": position,

        "score": round(recruitment_score, 2),

        "core_score": round(core_score, 2),

        "primary_score": round(primary_score, 2),

        "support_score": round(support_score, 2),

        "multiplier": round(multiplier, 3),

    }


def calculate_all_positions(competencies):

    results = []

    for position in POSITION_MODELS:

        results.append(
            calculate_position_score(
                position,
                competencies,
            )
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return results
