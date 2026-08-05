"""
ScoutVision Generic Profile Engine
Shared scoring engine for DNA, Development,
Club Fit and future intelligence modules.
"""

from __future__ import annotations


def calculate_profile(competencies: dict, profiles: list, mode: str = "max"):

    best_profile = None
    best_score = None
    scored_profiles = []

    for profile in profiles:

        score = 0.0

        for metric, weight in profile["weights"].items():
            score += competencies.get(metric, 0) * weight

        scored_profiles.append({
            "profile": profile,
            "score": round(score,1)
        })

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

    scored_profiles.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    result = best_profile.copy()
    result["profile_score"] = round(best_score,1)
    result["rankings"] = scored_profiles

    return result

