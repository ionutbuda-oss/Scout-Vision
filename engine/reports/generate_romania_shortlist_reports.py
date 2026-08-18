from pathlib import Path
import pandas as pd

from .renderer import render_html, render_pdf
from .report_builder_v3 import build_report_context, safe_filename

BASE = Path(__file__).resolve().parents[2]

SHORTLIST = BASE / "outputs/global_scoutvision/scoutvision_romania_shortlist_21_master.xlsx"
IDENTITY = BASE / "outputs/global_scoutvision/scoutvision_romania_transfermarkt_identity_v1.xlsx"

TEMPLATE = BASE / "engine/reports/templates_v3/scoutvision_master_3pages.html"

OUTPUT = BASE / "outputs/global_scoutvision/romania_shortlist_reports"

TEST_PLAYER = "M. Hokke"


def load_data():
    shortlist = pd.read_excel(
        SHORTLIST,
        sheet_name="All Ranked",
    )

    identity = pd.read_excel(
        IDENTITY,
        sheet_name="Transfermarkt Identity",
        dtype=str,
    )

    identity = identity[
        ["Player", "Team", "Transfermarkt URL", "Transfermarkt ID",
         "Verification Status"]
    ].copy()

    identity = identity.drop_duplicates(
        subset=["Player", "Team"],
        keep="first",
    )

    merged = shortlist.merge(
        identity,
        on=["Player", "Team"],
        how="left",
        validate="one_to_one",
    )

    return merged


def generate_player(df, player_name):
    matches = df.loc[
        df["Player"].astype(str).str.strip().str.casefold()
        == player_name.strip().casefold()
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly 1 match for {player_name}, got {len(matches)}"
        )

    row = matches.iloc[0]

    if str(row.get("Verification Status", "")).upper() != "CONFIRMED":
        raise RuntimeError(
            f"{player_name} does not have CONFIRMED Transfermarkt identity."
        )

    context = build_report_context(
        row,
        competition_name="Romania Recruitment Shortlist",
        ranked_frame=df,
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)

    slug = safe_filename(row["Player"])

    html_path = OUTPUT / f"{slug}.html"
    pdf_path = OUTPUT / f"{slug}.pdf"

    render_html(
        TEMPLATE,
        context,
        html_path,
    )

    render_pdf(
        html_path,
        pdf_path,
    )

    return html_path, pdf_path


if __name__ == "__main__":

    print("=" * 110)
    print("SCOUTVISION — ROMANIA SHORTLIST 21 REPORT GENERATOR")
    print("=" * 110)

    df = load_data()

    print(f"Players loaded: {len(df)}")
    print()

    OUTPUT.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = []

    for _, row in df.iterrows():

        player = str(row["Player"]).strip()

        try:
            html, pdf = generate_player(df, player)

            success += 1

            print(f"OK   | {player:<24} | {pdf}")

        except Exception as e:

            failed.append((player, str(e)))

            print(f"FAIL | {player:<24} | {e}")

    print()
    print("=" * 110)
    print("GENERATION COMPLETE")
    print("=" * 110)
    print(f"SUCCESS: {success} / {len(df)}")
    print(f"FAILED : {len(failed)}")

    if failed:
        print()
        print("FAILED PLAYERS:")
        for player, error in failed:
            print(f"  - {player}: {error}")

    print()
    print(f"OUTPUT FOLDER: {OUTPUT}")
    print("=" * 110)
