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

    trace = [

        {
            "step": "Identity Engine",
            "winner": identity_result["winner"]["profile"]["title"],
            "winner_score": identity_result["winner"]["score"],
            "runner_up": identity_result["runner_up"]["profile"]["title"],
            "runner_up_score": identity_result["runner_up"]["score"],
            "difference": identity_result["difference"],
        },

        {
            "step": "Confidence Engine",
            "level": confidence_result["level"],
            "score": confidence_result["score"],
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
            "final_identity": decision_result["primary_profile"]["title"],
        },

    ]

    return trace
