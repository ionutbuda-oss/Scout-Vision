"""
ScoutVision DNA Engine v3
Decision Rules

Responsibility:
- Classify identity certainty.
- Keep identity certainty independent from profile completeness.
"""


def is_clear_specialist(confidence):
    return confidence.score >= 80


def is_uncertain_identity(confidence):
    return confidence.score <= 20


def should_mark_hybrid(confidence):
    return (
        confidence.score > 20
        and confidence.score <= 40
    )
