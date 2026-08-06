"""
ScoutVision DNA Engine v3
Decision Engine
"""

from engine.intelligence.v3.decision_rules import (
    is_clear_specialist,
    is_uncertain_identity,
    should_upgrade_to_complete,
    should_mark_hybrid,
)


def select_final_identity(
    identity_result,
    versatility_result,
    confidence_result,
):

    winner = identity_result.winner
    runner_up = identity_result.runner_up

    identity_type = "Specialist"

    if should_upgrade_to_complete(
        versatility_result,
        confidence_result,
    ):
        identity_type = "Complete Candidate"

    elif should_mark_hybrid(
        versatility_result,
        confidence_result,
    ):
        identity_type = "Hybrid Candidate"

    elif is_clear_specialist(
        confidence_result,
    ):
        identity_type = "Clear Specialist"

    elif is_uncertain_identity(
        confidence_result,
    ):
        identity_type = "Uncertain"

    return {

        "primary_profile": winner.definition,

        "primary_score": winner.score,

        "runner_up_profile": (
            runner_up.definition
            if runner_up
            else None
        ),

        "runner_up_score": (
            runner_up.score
            if runner_up
            else None
        ),

        "difference": identity_result.difference,

        "confidence": confidence_result,

        "identity_type": identity_type,

        "versatility": versatility_result,

    }
