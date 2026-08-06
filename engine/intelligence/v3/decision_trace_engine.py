"""
ScoutVision DNA Engine v3
Decision Trace Engine

Responsibility:
- Record every decision made by the DNA pipeline.
"""


def build_decision_trace(
    identity_result,
    confidence_result,
    versatility_result,
    decision_result,
):

    winner = identity_result.winner
    runner_up = identity_result.runner_up

    trace = [

        {
            "step": "Identity Engine",
            "winner": winner.definition.title,
            "winner_score": winner.score,
            "runner_up": (
                runner_up.definition.title
                if runner_up
                else None
            ),
            "runner_up_score": (
                runner_up.score
                if runner_up
                else None
            ),
            "difference": identity_result.difference,
        },

        {
            "step": "Confidence Engine",
            "level": confidence_result.level,
            "score": confidence_result.score,
        },

        {
            "step": "Versatility Engine",
            "balanced": versatility_result["balanced"],
            "score": versatility_result["score"],
            "range": versatility_result["range"],
            "dominance": versatility_result["dominance"],
        },

        {
            "step": "Decision Engine",
            "identity_type": decision_result["identity_type"],
            "final_identity": decision_result["primary_profile"].title,
        },

    ]

    return trace
