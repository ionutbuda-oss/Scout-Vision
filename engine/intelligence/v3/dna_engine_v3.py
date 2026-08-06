"""
ScoutVision DNA Engine v3
"""

from engine.intelligence.profiles.am import AM_PROFILES
from engine.intelligence.profiles.cb import CB_PROFILES
from engine.intelligence.profiles.cm import CM_PROFILES
from engine.intelligence.profiles.dm import DM_PROFILES
from engine.intelligence.profiles.fb import FB_PROFILES
from engine.intelligence.profiles.st import ST_PROFILES
from engine.intelligence.profiles.winger import WINGER_PROFILES

from engine.intelligence.v3.identity_engine import choose_specialist_identity
from engine.intelligence.v3.versatility_engine import calculate_versatility
from engine.intelligence.v3.confidence_engine import calculate_confidence
from engine.intelligence.v3.decision_engine import select_final_identity
from engine.intelligence.v3.explainability_engine import build_explanation
from engine.intelligence.v3.decision_trace_engine import build_decision_trace


POSITION_PROFILES = {
    "AM": AM_PROFILES,
    "CB": CB_PROFILES,
    "CM": CM_PROFILES,
    "DM": DM_PROFILES,
    "FB_WB": FB_PROFILES,
    "ST": ST_PROFILES,
    "Winger": WINGER_PROFILES,
}


def build_player_dna_v3(position_group, competencies):

    profiles = POSITION_PROFILES.get(position_group)

    if profiles is None:
        raise ValueError(
            f"Unknown position group: {position_group}"
        )

    identity = choose_specialist_identity(
        competencies,
        profiles,
    )

    versatility = calculate_versatility(
        competencies,
    )

    confidence = calculate_confidence(
        identity.difference,
    )

    decision = select_final_identity(
        identity,
        versatility,
        confidence,
    )

    explanation = build_explanation(
        competencies,
        identity,
        confidence,
        versatility,
    )

    trace = build_decision_trace(
        identity,
        confidence,
        versatility,
        decision,
    )

    decision["explanation"] = explanation
    decision["trace"] = trace

    return decision
