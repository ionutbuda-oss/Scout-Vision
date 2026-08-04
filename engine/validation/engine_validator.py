"""
ScoutVision Engine Validator
"""

from engine.intelligence.profile_engine import calculate_profile


def validate_profile_engine():

    profiles = [

        {
            "title": "PROFILE A",
            "weights": {
                "A": 0.7,
                "B": 0.3
            }
        },

        {
            "title": "PROFILE B",
            "weights": {
                "A": 0.2,
                "B": 0.8
            }
        }

    ]

    competencies = {
        "A": 90,
        "B": 60
    }

    result = calculate_profile(competencies, profiles)

    assert result["title"] == "PROFILE A"

    print("✅ Profile Engine: PASSED")


if __name__ == "__main__":
    validate_profile_engine()
