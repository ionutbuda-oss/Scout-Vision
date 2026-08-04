"""
ScoutVision Development Engine v1.0
"""

DEVELOPMENT_PROFILES = [

    {
        "key": "FINAL_THIRD_IMPACT",
        "title": "FINAL THIRD IMPACT",
        "weights": {
            "Goal Threat": 0.70,
            "Creativity": 0.30
        }
    },

    {
        "key": "BALL_SECURITY",
        "title": "BALL SECURITY",
        "weights": {
            "Ball Carrying": 0.50,
            "Creativity": 0.50
        }
    },

    {
        "key": "POSSESSION_PROGRESSION",
        "title": "POSSESSION PROGRESSION",
        "weights": {
            "Progression": 0.70,
            "Creativity": 0.30
        }
    }

]


def build_development_profile(competencies):

    lowest = None
    lowest_score = 999

    for profile in DEVELOPMENT_PROFILES:

        score = 0

        for metric, weight in profile["weights"].items():
            score += competencies.get(metric, 100) * weight

        if score < lowest_score:
            lowest_score = score
            lowest = profile

    return {
        "title": lowest["title"]
    }

