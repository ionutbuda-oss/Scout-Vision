"""Generate a two-page ScoutVision Recruitment Report for one player."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .renderer import render_html, render_pdf
from .report_builder import build_report_context, safe_filename

DEFAULT_RANKINGS = Path("outputs/rankings/France_L3_U25_rankings.xlsx")
DEFAULT_OUTPUT = Path("outputs/scouting_reports")


def generate_report(
    *,
    rankings_file: Path,
    player_name: str,
    competition_name: str,
    output_folder: Path,
) -> tuple[Path, Path]:
    if not rankings_file.exists():
        raise FileNotFoundError(rankings_file)

    ranked = pd.read_excel(rankings_file, sheet_name="All Ranked")
    matches = ranked.loc[
        ranked["Player"].astype(str).str.strip().str.casefold()
        == player_name.strip().casefold()
    ]
    if matches.empty:
        raise ValueError(f"Player not found: {player_name}")

    row = matches.iloc[0]
    context = build_report_context(
        row,
        competition_name=competition_name,
        ranked_frame=ranked,
    )
    module_dir = Path(__file__).resolve().parent
    template_path = module_dir / "templates" / "recruitment_report.html"

    slug = safe_filename(row["Player"])
    html_path = output_folder / f"{slug}.html"
    pdf_path = output_folder / f"{slug}.pdf"

    render_html(template_path, context, html_path)
    render_pdf(html_path, pdf_path)
    return html_path, pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a ScoutVision Recruitment Report.")
    parser.add_argument("--player", required=True)
    parser.add_argument("--rankings", type=Path, default=DEFAULT_RANKINGS)
    parser.add_argument("--competition", default="France National")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    html_path, pdf_path = generate_report(
        rankings_file=args.rankings,
        player_name=args.player,
        competition_name=args.competition,
        output_folder=args.output,
    )
    print("=" * 68)
    print("SCOUTVISION RECRUITMENT REPORT - DELIVERY 1")
    print("=" * 68)
    print(f"HTML: {html_path.resolve()}")
    print(f"PDF:  {pdf_path.resolve()}")
    print("=" * 68)


if __name__ == "__main__":
    main()
