from pathlib import Path
import pandas as pd

from engine.reports.report_builder_v3 import build_report_context
from engine.reports.pdf_renderer_v4 import render_pdf_v4


DEFAULT_RANKINGS = Path(
    "outputs/rankings/France_Ligue_3_U25_rankings.xlsx"
)


def generate_report_v4(
    player_name: str,
    competition_name: str,
    rankings_file: Path = DEFAULT_RANKINGS,
):

    ranked = pd.read_excel(
        rankings_file,
        sheet_name="All Ranked"
    )

    matches = ranked.loc[
        ranked["Player"]
        .astype(str)
        .str.strip()
        .str.casefold()
        ==
        player_name.strip().casefold()
    ]

    if matches.empty:
        raise ValueError(
            f"Player not found: {player_name}"
        )

    row = matches.iloc[0]

    context = build_report_context(
        row,
        competition_name=competition_name,
        ranked_frame=ranked,
    )

    output = Path(
        "outputs/scouting_reports_v4"
    ) / f"{player_name.replace(' ', '_')}.pdf"

    render_pdf_v4(
        output,
        context
    )

    return output


if __name__ == "__main__":

    pdf = generate_report_v4(
        player_name="R. Eh Hadari",
        competition_name="France Ligue 3",
    )

    print("=" * 60)
    print("SCOUTVISION V4 REPORT")
    print("=" * 60)
    print(pdf.resolve())
