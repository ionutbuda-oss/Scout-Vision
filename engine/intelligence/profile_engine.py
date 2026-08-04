"""
ScoutVision Generic Profile Engine
Shared scoring engine for DNA, Development,
Club Fit and future intelligence modules.
"""

from __future__ import annotations


def calculate_profile(competencies: dict, profiles: list, mode: str = "max"):

    best_profile = None
    best_score = None

    for profile in profiles:

        score = 0.0

        for metric, weight in profile["weights"].items():
            score += competencies.get(metric, 0) * weight

        if best_score is None:
            best_score = score
            best_profile = profile
            continue

        if mode == "max":
            if score > best_score:
                best_score = score
                best_profile = profile

        else:
            if score < best_score:
                best_score = score
                best_profile = profile

    result = best_profile.copy()
    result["profile_score"] = round(best_score, 1)

    return result

