"""Generate and validate Top-N ScoutVision reports for every position group."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from .renderer import render_html, render_pdf
from .report_builder import build_report_context, safe_filename

DEFAULT_RANKINGS = Path("outputs/rankings/France_L3_U25_rankings.xlsx")
DEFAULT_OUTPUT_ROOT = Path("outputs/scouting_reports")


@dataclass(frozen=True)
class ReportRecord:
    competition: str
    position_group: str
    rank: int
    player: str
    scout_score: float
    season_performance: float
    html_path: str
    pdf_path: str
    pdf_pages: int
    status: str


def _score_column(frame: pd.DataFrame) -> str:
    for candidate in ("Scout Score", "Recruitment Score"):
        if candidate in frame.columns:
            return candidate
    raise ValueError("Rankings workbook has neither 'Scout Score' nor 'Recruitment Score'.")


def _competition_folder(output_root: Path, competition_name: str) -> Path:
    return output_root / safe_filename(competition_name)


def _clear_output(folder: Path) -> None:
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)


def _pdf_page_count(path: Path) -> int:
    return len(PdfReader(str(path)).pages)


def _validate_pdf(path: Path, expected_pages: int = 2) -> tuple[int, str]:
    if not path.exists() or path.stat().st_size < 10_000:
        return 0, "INVALID_FILE"
    pages = _pdf_page_count(path)
    return pages, "VALID" if pages == expected_pages else f"UNEXPECTED_PAGES_{pages}"


def _write_manifest(records: list[ReportRecord], competition_folder: Path) -> None:
    csv_path = competition_folder / "report_manifest.csv"
    json_path = competition_folder / "report_manifest.json"
    summary_path = competition_folder / "generation_summary.txt"

    rows = [asdict(record) for record in records]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    valid = sum(record.status == "VALID" for record in records)
    groups = sorted({record.position_group for record in records})
    summary_path.write_text(
        "\n".join([
            "SCOUTVISION FRANCE REPORT GENERATION",
            "=" * 44,
            f"Generated at (UTC): {datetime.now(timezone.utc).isoformat()}",
            f"Reports requested: {len(records)}",
            f"Valid two-page PDFs: {valid}",
            f"Position groups: {', '.join(groups)}",
            f"Status: {'VALIDATED' if valid == len(records) else 'CHECK_REQUIRED'}",
        ]) + "\n",
        encoding="utf-8",
    )


def generate_top_reports(
    *,
    rankings_file: Path,
    competition_name: str,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    top_n_per_position: int = 5,
    clear_previous: bool = True,
) -> list[ReportRecord]:
    """Generate Top-N recruitment reports for each position group."""

    if top_n_per_position < 1:
        raise ValueError("top_n_per_position must be at least 1.")
    if not rankings_file.exists():
        raise FileNotFoundError(rankings_file)

    ranked = pd.read_excel(rankings_file, sheet_name="All Ranked")
    score_column = _score_column(ranked)
    ranked[score_column] = pd.to_numeric(ranked[score_column], errors="coerce")
    ranked["Performance Score"] = pd.to_numeric(ranked["Performance Score"], errors="coerce")

    competition_folder = _competition_folder(output_root, competition_name)
    if clear_previous:
        _clear_output(competition_folder)
    else:
        competition_folder.mkdir(parents=True, exist_ok=True)

    records: list[ReportRecord] = []
    groups = ranked["Position Group"].dropna().astype(str).drop_duplicates().tolist()

    for position_group in groups:
        players = ranked.loc[ranked["Position Group"].astype(str) == position_group].copy()
        players = players.sort_values(
            [score_column, "Performance Score"],
            ascending=[False, False],
            na_position="last",
        ).head(top_n_per_position)

        group_folder = competition_folder / safe_filename(position_group)
        group_folder.mkdir(parents=True, exist_ok=True)

        for rank, (_, row) in enumerate(players.iterrows(), start=1):
            prefix = f"{rank:02d}__{safe_filename(row['Player'])}"
            final_html = group_folder / f"{prefix}.html"
            final_pdf = group_folder / f"{prefix}.pdf"

            context = build_report_context(
                row,
                competition_name=competition_name,
                ranked_frame=ranked,
            )
            template_path = (
                Path(__file__).resolve().parent
                / "templates"
                / "recruitment_report.html"
            )
            render_html(template_path, context, final_html)
            render_pdf(final_html, final_pdf)

            pages, status = _validate_pdf(final_pdf)
            records.append(ReportRecord(
                competition=competition_name,
                position_group=position_group,
                rank=rank,
                player=str(row["Player"]),
                scout_score=round(float(row[score_column]), 1),
                season_performance=round(float(row["Performance Score"]), 1),
                html_path=str(final_html),
                pdf_path=str(final_pdf),
                pdf_pages=pages,
                status=status,
            ))

    if not records:
        raise RuntimeError("No reports were generated.")
    _write_manifest(records, competition_folder)

    invalid = [record for record in records if record.status != "VALID"]
    if invalid:
        details = ", ".join(f"{r.player}: {r.status}" for r in invalid)
        raise RuntimeError(f"Report validation failed: {details}")

    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Top-N ScoutVision reports by position.")
    parser.add_argument("--rankings", type=Path, default=DEFAULT_RANKINGS)
    parser.add_argument("--competition", default="France National")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--keep-existing", action="store_true")
    args = parser.parse_args()

    records = generate_top_reports(
        rankings_file=args.rankings,
        competition_name=args.competition,
        output_root=args.output_root,
        top_n_per_position=args.top,
        clear_previous=not args.keep_existing,
    )

    print("=" * 68)
    print("SCOUTVISION TOP REPORTS - VALIDATED")
    print("=" * 68)
    print(f"Competition: {args.competition}")
    print(f"Reports created: {len(records)}")
    for group in sorted({r.position_group for r in records}):
        print(f"- {group}: {sum(r.position_group == group for r in records)}")
    print(f"Output: {_competition_folder(args.output_root, args.competition).resolve()}")
    print("=" * 68)


if __name__ == "__main__":
    main()
