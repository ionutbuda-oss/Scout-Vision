"""ScoutVision V3 — Batch Report Audit."""

from __future__ import annotations

from pathlib import Path
import argparse

import pandas as pd

from .report_builder_v3 import safe_filename


MIN_PDF_BYTES = 10_000
MIN_HTML_BYTES = 2_000


def audit_reports(
    *,
    rankings_file: Path,
    reports_folder: Path,
    competition_name: str,
) -> bool:

    ranked = pd.read_excel(
        rankings_file,
        sheet_name="All Ranked",
    )

    players = (
        ranked["Player"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    expected = {}

    for player in players:
        slug = safe_filename(player)
        expected.setdefault(slug, []).append(player)

    pdf_files = {
        path.stem: path
        for path in reports_folder.glob("*.pdf")
    }

    html_files = {
        path.stem: path
        for path in reports_folder.glob("*.html")
    }

    missing_pdf = []
    missing_html = []
    small_pdf = []
    small_html = []

    for slug, names in expected.items():

        player = names[0]

        pdf = pdf_files.get(slug)
        html = html_files.get(slug)

        if pdf is None:
            missing_pdf.append(player)
        elif pdf.stat().st_size < MIN_PDF_BYTES:
            small_pdf.append(
                (player, pdf.stat().st_size)
            )

        if html is None:
            missing_html.append(player)
        elif html.stat().st_size < MIN_HTML_BYTES:
            small_html.append(
                (player, html.stat().st_size)
            )

    slug_collisions = {
        slug: names
        for slug, names in expected.items()
        if len(names) > 1
    }

    unexpected_pdf = sorted(
        set(pdf_files) - set(expected)
    )

    unexpected_html = sorted(
        set(html_files) - set(expected)
    )

    pdf_sizes = [
        path.stat().st_size
        for path in pdf_files.values()
    ]

    print("=" * 78)
    print("SCOUTVISION V3 — REPORT AUDIT")
    print("=" * 78)
    print(f"Competition:      {competition_name}")
    print(f"Expected players: {len(players)}")
    print(f"Expected slugs:   {len(expected)}")
    print(f"PDF files:        {len(pdf_files)}")
    print(f"HTML files:       {len(html_files)}")

    print("\nINTEGRITY")
    print("-" * 78)
    print(f"Missing PDF:      {len(missing_pdf)}")
    print(f"Missing HTML:     {len(missing_html)}")
    print(f"Small PDF:        {len(small_pdf)}")
    print(f"Small HTML:       {len(small_html)}")
    print(f"Slug collisions:  {len(slug_collisions)}")
    print(f"Unexpected PDF:   {len(unexpected_pdf)}")
    print(f"Unexpected HTML:  {len(unexpected_html)}")

    if pdf_sizes:
        sizes_mb = [
            size / (1024 * 1024)
            for size in pdf_sizes
        ]

        series = pd.Series(sizes_mb)

        print("\nPDF SIZE DISTRIBUTION (MB)")
        print("-" * 78)
        print(
            series.describe(
                percentiles=[0.25, 0.5, 0.75, 0.95]
            ).round(3).to_string()
        )

    issues = (
        len(missing_pdf)
        + len(missing_html)
        + len(small_pdf)
        + len(small_html)
        + len(slug_collisions)
    )

    if missing_pdf:
        print("\nMISSING PDF")
        for player in missing_pdf:
            print(f"  - {player}")

    if missing_html:
        print("\nMISSING HTML")
        for player in missing_html:
            print(f"  - {player}")

    if small_pdf:
        print("\nSMALL PDF")
        for player, size in small_pdf:
            print(f"  - {player}: {size} bytes")

    if slug_collisions:
        print("\nSLUG COLLISIONS")
        for slug, names in slug_collisions.items():
            print(
                f"  - {slug}: "
                + " | ".join(names)
            )

    print("\n" + "=" * 78)

    if issues == 0:
        print("AUDIT STATUS: PASS")
        print("All expected reports passed structural integrity checks.")
        passed = True
    else:
        print("AUDIT STATUS: REVIEW REQUIRED")
        print(f"Structural issues detected: {issues}")
        passed = False

    print("=" * 78)

    return passed


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Audit ScoutVision V3 batch reports."
    )

    parser.add_argument(
        "--rankings",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--reports",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--competition",
        required=True,
    )

    args = parser.parse_args()

    passed = audit_reports(
        rankings_file=args.rankings,
        reports_folder=args.reports,
        competition_name=args.competition,
    )

    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
