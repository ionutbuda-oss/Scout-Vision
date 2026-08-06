"""ScoutVision V3 deterministic executive summary generator.

Builds club-facing summaries from:
- DNA V3 primary identity
- strongest competency
- supporting competency
- development area
- club-facing profile type

No traits are inferred outside the active position model.
"""

from __future__ import annotations

from typing import Any


ACTION_PHRASES = {
    "Aerial Defending": "winning aerial contests and protecting central areas",
    "Ball Carrying": "advancing possession through carries and individual actions",
    "Ball Security": "retaining possession under attacking pressure",
    "Ball Winning": "regaining possession through defensive actions",
    "Box Threat": "operating in high-value penalty-area zones",
    "Chance Creation": "creating opportunities through passing and crossing",
    "Combination Play": "connecting attacks through passing combinations",
    "Creativity": "creating and accessing advanced passing options",
    "Defending": "protecting space and succeeding in defensive actions",
    "Defensive Contribution": "supporting the team through defensive actions",
    "Distribution": "circulating possession accurately and consistently",
    "Finishing": "converting shooting opportunities",
    "Goal Threat": "producing shooting and scoring output",
    "Link Play": "connecting attacks and retaining possession",
    "Offensive Duels": "competing effectively in attacking duels",
    "Progression": "advancing possession and breaking lines through passing",
}


STRENGTH_PHRASES = {
    "Aerial Defending": "aerial-defending output",
    "Ball Carrying": "ball-carrying output",
    "Ball Security": "possession security",
    "Ball Winning": "ball-winning output",
    "Box Threat": "penalty-area threat",
    "Chance Creation": "chance-creation output",
    "Combination Play": "combination play",
    "Creativity": "creative output",
    "Defending": "defensive output",
    "Defensive Contribution": "defensive contribution",
    "Distribution": "distribution",
    "Finishing": "finishing output",
    "Goal Threat": "goal threat",
    "Link Play": "link play",
    "Offensive Duels": "offensive-duel output",
    "Progression": "progression",
}


PROFILE_PHRASES = {
    "CLEAR SPECIALIST PROFILE": "a clearly defined specialist profile",
    "SPECIALIST PROFILE": "a specialist profile",
    "VERSATILE PROFILE": "a versatile profile",
    "COMPLETE PROFILE": "a complete profile",
    "MULTI-ROLE PROFILE": "a multi-role profile",
    "PLAYER PROFILE": "the overall player profile",
}


def _level(score: float) -> str:
    if score >= 90:
        return "outstanding"
    if score >= 80:
        return "very strong"
    if score >= 70:
        return "strong"
    if score >= 60:
        return "above-average"
    return "developing"


def generate_executive_summary_v3(
    *,
    competencies: list[dict[str, Any]],
    dna_v3: dict[str, Any],
    profile_type: str,
) -> str:
    """Return a deterministic club-facing V3 player summary."""

    if not competencies:
        return (
            "Player profile generated from the active "
            "ScoutVision position model."
        )

    ordered = sorted(
        competencies,
        key=lambda item: item["score"],
        reverse=True,
    )

    primary = ordered[0]
    secondary = ordered[1] if len(ordered) > 1 else ordered[0]
    development = ordered[-1]

    identity = dna_v3["primary_profile"].title.title()

    primary_action = ACTION_PHRASES.get(
        primary["name"],
        f"performing strongly in {primary['name'].lower()}",
    )

    secondary_phrase = STRENGTH_PHRASES.get(
        secondary["name"],
        f"{secondary['name'].lower()} output",
    )

    secondary_level = _level(float(secondary["score"]))

    profile_phrase = PROFILE_PHRASES.get(
        profile_type,
        "the overall player profile",
    )

    first_sentence = (
        f"{identity} whose strongest impact comes from "
        f"{primary_action}, supported by {secondary_level} "
        f"{secondary_phrase}."
    )

    second_sentence = (
        f"{development['name']} remains the main development area "
        f"within {profile_phrase}."
    )

    return f"{first_sentence} {second_sentence}"
