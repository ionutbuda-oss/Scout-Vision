"""
ScoutVision DNA Engine v3
Explainability Engine

Responsibility:
- Explain WHY a player received a specific identity.
"""


def build_explanation(
    competencies,
    identity_result,
    confidence_result,
    versatility_result,
):

    ordered = sorted(
        competencies.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    strengths = [
        {
            "name": name,
            "score": score,
        }
        for name, score in ordered[:3]
    ]

    winner = identity_result["winner"]["profile"]

    return {

        "identity": winner["title"],

        "signature": winner.get("signature"),

        "strengths": strengths,

        "confidence": confidence_result,

        "versatility": versatility_result,

        "summary": winner.get(
            "executive_summary",
            ""
        ),

    }
