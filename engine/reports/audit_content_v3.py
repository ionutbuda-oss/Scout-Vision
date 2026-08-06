"""ScoutVision V3 — Report Content Audit."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .report_builder_v3 import build_report_context


VALID_PROFILE_TYPES = {
    "CLEAR SPECIALIST PROFILE",
    "SPECIALIST PROFILE",
    "VERSATILE PROFILE",
    "COMPLETE PROFILE",
    "MULTI-ROLE PROFILE",
}

PLACEHOLDER_MARKERS = (
    "undefined",
    "none",
    "nan",
    "{{",
    "}}",
)


def audit_content(
    *,
    rankings_file: Path,
    competition_name: str,
) -> bool:

    ranked = pd.read_excel(
        rankings_file,
        sheet_name="All Ranked",
    )

    failures = []
    profile_types = {}
    identities = {}

    print("=" * 78)
    print("SCOUTVISION V3 — CONTENT AUDIT")
    print("=" * 78)
    print(f"Competition: {competition_name}")
    print(f"Players:     {len(ranked)}")
    print("=" * 78)

    for index, (_, row) in enumerate(ranked.iterrows(), 1):

        player = str(row["Player"]).strip()

        try:
            context = build_report_context(
                row,
                competition_name=competition_name,
                ranked_frame=ranked,
            )

            dna = context.get("player_dna", {})
            profile_type = context.get("profile_type")
            development = context.get("development")
            summary = context.get("executive_summary", "")

            primary_profile = dna.get("primary_profile")
            primary_score = dna.get("primary_score")

            errors = []

            # Primary Identity
            if primary_profile is None:
                errors.append("missing primary identity")
                identity = None
            else:
                identity = getattr(
                    primary_profile,
                    "title",
                    None,
                )

                if not identity:
                    errors.append(
                        "primary identity has no title"
                    )

            # Primary identity score
            if primary_score is None:
                errors.append(
                    "missing primary identity score"
                )
            else:
                try:
                    score = float(primary_score)

                    if not 0 <= score <= 100:
                        errors.append(
                            f"invalid primary score: {score}"
                        )

                except (TypeError, ValueError):
                    errors.append(
                        "primary score is not numeric"
                    )

            # Profile Type
            if profile_type not in VALID_PROFILE_TYPES:
                errors.append(
                    f"invalid profile type: {profile_type}"
                )

            # Development Area
            if not isinstance(development, dict):
                errors.append(
                    "development area missing"
                )
            else:
                if not development.get("name"):
                    errors.append(
                        "development area has no name"
                    )

                score = development.get("score")

                try:
                    score = float(score)

                    if not 0 <= score <= 100:
                        errors.append(
                            f"invalid development score: {score}"
                        )

                except (TypeError, ValueError):
                    errors.append(
                        "development score invalid"
                    )

            # Executive Summary
            if not isinstance(summary, str):
                errors.append(
                    "executive summary is not text"
                )

            else:
                clean_summary = summary.strip()

                if len(clean_summary) < 40:
                    errors.append(
                        "executive summary too short"
                    )

                lower_summary = clean_summary.lower()

                for marker in PLACEHOLDER_MARKERS:
                    if marker in lower_summary:
                        errors.append(
                            f"summary contains marker: {marker}"
                        )

            # Count distributions
            if profile_type:
                profile_types[profile_type] = (
                    profile_types.get(profile_type, 0) + 1
                )

            if identity:
                identities[identity] = (
                    identities.get(identity, 0) + 1
                )

            if errors:
                failures.append(
                    {
                        "player": player,
                        "errors": errors,
                    }
                )

                print(
                    f"[{index:>3}/{len(ranked)}] "
                    f"{player:<30} REVIEW"
                )

            else:
                print(
                    f"[{index:>3}/{len(ranked)}] "
                    f"{player:<30} OK"
                )

        except Exception as exc:

            failures.append(
                {
                    "player": player,
                    "errors": [
                        f"build failure: {exc}"
                    ],
                }
            )

            print(
                f"[{index:>3}/{len(ranked)}] "
                f"{player:<30} FAILED"
            )

    print("\n" + "=" * 78)
    print("PROFILE TYPE DISTRIBUTION")
    print("=" * 78)

    for name, count in sorted(
        profile_types.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{name:<30} {count:>5}")

    print("\n" + "=" * 78)
    print("PRIMARY IDENTITY DISTRIBUTION")
    print("=" * 78)

    for name, count in sorted(
        identities.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{name:<30} {count:>5}")

    print("\n" + "=" * 78)
    print("CONTENT AUDIT RESULT")
    print("=" * 78)

    print(f"Players checked: {len(ranked)}")
    print(f"Passed:          {len(ranked) - len(failures)}")
    print(f"Review required: {len(failures)}")

    if failures:

        print("\nISSUES")
        print("-" * 78)

        for item in failures:
            print(
                f"{item['player']}: "
                + "; ".join(item["errors"])
            )

        print("\nAUDIT STATUS: REVIEW REQUIRED")
        return False

    print("\nAUDIT STATUS: PASS")
    return True


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Audit ScoutVision V3 report content."
    )

    parser.add_argument(
        "--rankings",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--competition",
        required=True,
    )

    args = parser.parse_args()

    passed = audit_content(
        rankings_file=args.rankings,
        competition_name=args.competition,
    )

    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
