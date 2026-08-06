"""
ScoutVision DNA Engine v3
Confidence Engine

Responsibility:
- Estimate confidence in the selected identity.
"""


def calculate_confidence(score_difference):

    if score_difference >= 15:
        return {
            "level": "Very High",
            "score": 100,
        }

    if score_difference >= 10:
        return {
            "level": "High",
            "score": 80,
        }

    if score_difference >= 5:
        return {
            "level": "Medium",
            "score": 60,
        }

    return {
        "level": "Low",
        "score": 40,
    }
