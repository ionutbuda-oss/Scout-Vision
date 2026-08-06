"""Generate ScoutVision V3 recruitment reports for an entire ranking pool."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .generate_report_v3 import generate_report


def generate_batch_reports(
    *,
    rankings_file: Path,
    competition_name: str,
    output_folder: Path,
) -> None:

    if not rankings_file.exists():
        raise FileNotFoundError(rankings_file)

    ranked = pd.read_excel(
        rankings_file,
        sheet_name="All Ranked",
    )

    if "Player" not in ranked.columns:
        raise RuntimeError(
            "Rankings file does not contain a Player column."
        )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    players = (
        ranked["Player"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    players = [
        player
        for player in players
        if player
    ]

    print("=" * 72)
    print("SCOUTVISION V3 — BATCH REPORT GENERATOR")
    print("=" * 72)
    print(f"Competition: {competition_name}")
    print(f"Rankings:    {rankings_file}")
    print(f"Players:     {len(players)}")
    print(f"Output:      {output_folder}")
    print("=" * 72)

    successful = []
    failures = []

    for index, player in enumerate(players, 1):

        print(
            f"[{index:>3}/{len(players)}] "
            f"{player:<30}",
            end=" ",
            flush=True,
        )

        try:

            html_path, pdf_path = generate_report(
                rankings_file=rankings_file,
                player_name=player,
                competition_name=competition_name,
                output_folder=output_folder,
            )

            successful.append(
                {
                    "player": player,
                    "html": str(html_path),
                    "pdf": str(pdf_path),
                }
            )

            print("OK")

        except Exception as exc:

            failures.append(
                {
                    "player": player,
                    "error": str(exc),
                }
            )

            print(f"FAILED — {exc}")

    print("\n" + "=" * 72)
    print("BATCH COMPLETE")
    print("=" * 72)
    print(f"Successful: {len(successful)}")
    print(f"Failures:   {len(failures)}")

    if failures:

        print("\nFAILURES")
        print("-" * 72)

        for item in failures:
            print(
                f"{item['player']}: "
                f"{item['error']}"
            )

    print("=" * 72)


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Generate ScoutVision V3 recruitment reports "
            "for an entire competition."
        )
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

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    generate_batch_reports(
        rankings_file=args.rankings,
        competition_name=args.competition,
        output_folder=args.output,
    )


if __name__ == "__main__":
    main()
