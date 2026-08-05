"""
ScoutVision DNA Engine v2
"""

from engine.intelligence.profile_engine import calculate_profile

from engine.intelligence.profiles.am import AM_PROFILES
from engine.intelligence.profiles.cb import CB_PROFILES
from engine.intelligence.profiles.dm import DM_PROFILES
from engine.intelligence.profiles.cm import CM_PROFILES
from engine.intelligence.profiles.fb import FB_PROFILES
from engine.intelligence.profiles.winger import WINGER_PROFILES
from engine.intelligence.profiles.st import ST_PROFILES

POSITION_PROFILES = {

    "AM": AM_PROFILES,
    "CB": CB_PROFILES,
    "DM": DM_PROFILES,
    "CM": CM_PROFILES,
    "FB_WB": FB_PROFILES,
    "Winger": WINGER_PROFILES,
    "ST": ST_PROFILES,

}


# ============================================================
# Identity Engine Configuration
# ============================================================

IDENTITY_TIE_THRESHOLD = 2.0

IDENTITY_LEVELS = [

    (20, "Specialist"),
    (12, "Strong Identity"),
    (6, "Balanced Profile"),
    (0, "Hybrid Profile"),

]





from engine.intelligence.attributes import ATTRIBUTE_LABELS


def build_player_dna(position_group, competencies):

    profiles = POSITION_PROFILES.get(position_group)

    if profiles is None:
        return {
            "key":"UNKNOWN",
            "title":"UNKNOWN PROFILE",
            "description":"No DNA profiles available."
        }

    scored_profiles = []

    for profile in profiles:

        score = 0.0

        for metric, weight in profile["weights"].items():
            score += competencies.get(metric,0) * weight

        scored_profiles.append({

            "profile":profile,
            "score":round(score,1)

        })

    scored_profiles.sort(
        key=lambda x:x["score"],
        reverse=True
    )

    primary = scored_profiles[0]
    second = scored_profiles[1]

    difference = primary["score"] - second["score"]

    # Intelligent tie-breaker
    if difference <= IDENTITY_TIE_THRESHOLD:

        dominant_metric = max(
            competencies,
            key=competencies.get
        )

        primary_signature = primary["profile"].get("signature")
        second_signature = second["profile"].get("signature")

        if second_signature == dominant_metric:
            primary, second = second, primary
            difference = primary["score"] - second["score"]

    identity_profile = "Hybrid Profile"

    for threshold, label in IDENTITY_LEVELS:
        if difference >= threshold:
            identity_profile = label
            break

    ordered = sorted(
        competencies.items(),
        key=lambda x:x[1],
        reverse=True
    )

    secondary_metric = ordered[1][0]

    return {

        "key":primary["profile"]["key"],
        "title":primary["profile"]["title"],
        "description":primary["profile"]["description"],
        "executive_summary":primary["profile"].get("executive_summary"),
        "archetype":primary["profile"].get("archetype"),
        "identity_profile": identity_profile,
        "secondary_attribute":ATTRIBUTE_LABELS.get(
            secondary_metric,
            secondary_metric
        ),
        "profile_scores":scored_profiles

    }

