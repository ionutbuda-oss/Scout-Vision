"""
ScoutVision DNA Engine v2
"""

from engine.intelligence.profile_engine import calculate_profile

from engine.intelligence.profiles.am import AM_PROFILES

POSITION_PROFILES = {

    "AM": AM_PROFILES,

}


def build_player_dna(position_group, competencies):

    profiles = POSITION_PROFILES.get(position_group)

    if profiles is None:
        return {
            "key":"UNKNOWN",
            "title":"UNKNOWN PROFILE",
            "description":"No DNA profiles available."
        }

    profile = calculate_profile(
        competencies,
        profiles,
        mode="max"
    )

    return {

        "key":profile["key"],
        "title":profile["title"],
        "description":profile["description"]

    }
