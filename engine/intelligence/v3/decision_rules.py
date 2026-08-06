"""
ScoutVision DNA Engine v3
Decision Rules

Business rules for player identity selection.
"""


def is_clear_specialist(confidence):

    return confidence["score"] >= 80


def is_uncertain_identity(confidence):

    return confidence["score"] <= 40


def should_upgrade_to_complete(
    versatility,
    confidence,
):

    return (
        versatility["balanced"]
        and
        confidence["score"] <= 60
    )


def should_mark_hybrid(
    versatility,
    confidence,
):

    return (
        not versatility["balanced"]
        and
        confidence["score"] <= 40
    )
