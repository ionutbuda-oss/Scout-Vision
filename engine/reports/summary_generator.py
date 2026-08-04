"""Deterministic executive summaries for ScoutVision recruitment reports.

Every sentence is derived from position group and competency scores.  The
module does not infer traits that are absent from the active position model.
"""

from __future__ import annotations

from typing import Any

ROLE_LABELS = {
    "CB": "Central defender",
    "FB_WB": "Full-back / wing-back",
    "DM": "Defensive midfielder",
    "CM": "Central midfielder",
    "AM": "Attacking midfielder",
    "Winger": "Wide attacker",
    "ST": "Centre-forward",
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

ACTION_PHRASES = {
    "Aerial Defending": "winning aerial contests and protecting central areas",
    "Ball Carrying": "advancing possession through carries and individual actions",
    "Ball Security": "retaining possession through dribbles and offensive duels",
    "Ball Winning": "regaining possession through defensive actions",
    "Box Threat": "arriving and operating in high-value penalty-area zones",
    "Chance Creation": "creating opportunities through passing and crossing",
    "Combination Play": "connecting attacks through passing combinations",
    "Creativity": "creating and accessing advanced passing options",
    "Defending": "protecting space and succeeding in defensive actions",
    "Defensive Contribution": "supporting the team through defensive actions",
    "Distribution": "circulating possession accurately and consistently",
    "Finishing": "converting shooting opportunities",
    "Goal Threat": "producing shooting and scoring output",
    "Link Play": "connecting attacks and supporting possession",
    "Offensive Duels": "competing effectively in attacking duels",
    "Progression": "advancing possession and breaking lines through passing",
}

DEVELOPMENT_PHRASES = {
    "Aerial Defending": "aerial defending remains the main development area",
    "Ball Carrying": "ball carrying remains the main development area",
    "Ball Security": "possession security remains the main development area",
    "Ball Winning": "ball winning remains the main development area",
    "Box Threat": "penalty-area threat remains the main development area",
    "Chance Creation": "chance creation remains the main development area",
    "Combination Play": "combination play remains the main development area",
    "Creativity": "creative output remains the main development area",
    "Defending": "defensive output remains the main development area",
    "Defensive Contribution": "defensive contribution remains the main development area",
    "Distribution": "distribution remains the main development area",
    "Finishing": "finishing remains the main development area",
    "Goal Threat": "goal threat remains the main development area",
    "Link Play": "link play remains the main development area",
    "Offensive Duels": "offensive-duel output remains the main development area",
    "Progression": "progression remains the main development area",
}


def _level(score: float) -> str:
    if score >= 90:
        return "elite"
    if score >= 80:
        return "very strong"
    if score >= 70:
        return "strong"
    if score >= 60:
        return "above-average"
    return "developing"


def generate_executive_summary(
    *,
    position_group: str,
    competencies: list[dict[str, Any]],
) -> str:
    """Return a concise, traceable two-sentence player profile."""

    if not competencies:
        return "Position-specific profile generated from the active ScoutVision model."

    ordered = sorted(competencies, key=lambda item: item["score"], reverse=True)
    strongest = ordered[0]
    supporting = ordered[1] if len(ordered) > 1 else ordered[0]
    weakest = ordered[-1]

    role = ROLE_LABELS.get(position_group, "Player")
    strong_name = strongest["name"]
    support_name = supporting["name"]
    weak_name = weakest["name"]

    strength_phrase = STRENGTH_PHRASES.get(
        strong_name,
        f"{strong_name.lower()} output",
    )
    action_phrase = ACTION_PHRASES.get(
        strong_name,
        f"performing strongly in {strong_name.lower()}",
    )
    support_phrase = STRENGTH_PHRASES.get(
        support_name,
        f"{support_name.lower()} output",
    )
    development_phrase = DEVELOPMENT_PHRASES.get(
        weak_name,
        f"{weak_name.lower()} remains the main development area",
    )

    first_sentence = (
        f"{role} with {_level(strongest['score'])} {strength_phrase} "
        f"and {support_phrase}."
    )
    second_sentence = (
        f"The profile is driven by {action_phrase}, while "
        f"{development_phrase}."
    )
    return f"{first_sentence} {second_sentence}"
