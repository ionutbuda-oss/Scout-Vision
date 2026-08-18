from pathlib import Path
import pandas as pd

from engine.reports.archetype_descriptions import ARCHETYPE_DESCRIPTIONS
from engine.reports.archetype_ranking import ARCHETYPE_WEIGHTS


INPUT_FILE = Path(
    "outputs/rankings/Serbia_1_ALL_archetype_rankings.xlsx"
)

RANKED_FILE = Path(
    "outputs/rankings/Serbia_1_ALL_rankings.xlsx"
)

TEMPLATE_FILE = Path(
    "engine/reports/templates_v3/recruitment_board.html"
)

CSS_FILE = Path(
    "engine/reports/templates_v3/recruitment_board.css"
)

OUTPUT_FILE = Path(
    "outputs/recruitment_boards/"
    "Serbia_1_ALL_Recruitment_Board_V3.html"
)

TOP_N = 5


def build_sections():

    excel = pd.ExcelFile(INPUT_FILE)

    sections = ""

    for archetype in excel.sheet_names:

        # Skip consolidated sheet
        if archetype == "TOP 5 ALL ARCHETYPES":
            continue

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=archetype
        )

        if df.empty:
            continue

        info = ARCHETYPE_DESCRIPTIONS.get(
            archetype,
            {}
        )

        description = info.get(
            "description",
            ""
        )

        profile = info.get(
            "profile",
            ""
        )

        weights = ARCHETYPE_WEIGHTS.get(
            archetype,
            {}
        )

        weight_html = ""

        for metric, value in weights.items():

            weight_html += f"""
            <div class="competency-row">
                <span>{metric}</span>
                <strong>{int(value * 100)}%</strong>
            </div>
            """

        table_rows = ""

        for rank, (_, row) in enumerate(
            df.head(TOP_N).iterrows(),
            start=1
        ):

            team = (
                ""
                if pd.isna(row.get("Team"))
                else row.get("Team", "")
            )

            player = (
                ""
                if pd.isna(row.get("Player"))
                else row.get("Player", "")
            )

            position = (
                ""
                if pd.isna(row.get("Position"))
                else row.get("Position", "")
            )

            age = (
                ""
                if pd.isna(row.get("Age"))
                else int(row.get("Age"))
            )

            archetype_score = row.get(
                "Archetype Score",
                ""
            )

            scout_score = row.get(
                "Scout Score",
                ""
            )

            table_rows += f"""
            <tr>
                <td>{rank}</td>
                <td>{player}</td>
                <td>{team}</td>
                <td>{position}</td>
                <td>{age}</td>
                <td>{archetype_score}</td>
                <td>{scout_score}</td>
            </tr>
            """

        players = f"""
        <table class="recruitment-table">

            <thead>

                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th>Team</th>
                    <th>Position</th>
                    <th>Age</th>
                    <th>Archetype Score</th>
                    <th>Scout Score</th>
                </tr>

            </thead>

            <tbody>

                {table_rows}

            </tbody>

        </table>
        """

        sections += f"""

        <div class="report-page">

        <header class="topbar">

        <div class="brand">

        <div class="brand-mark">
        SV
        </div>

        SCOUTVISION

        </div>


        <div class="document-type">

        <span>
        RECRUITMENT BOARD
        </span>

        <small>
        ARCHETYPE PROFILE
        </small>

        </div>

        </header>


        <section class="panel">

        <div class="section-kicker">
        ARCHETYPE INTELLIGENCE
        </div>


        <h1>
        {archetype}
        </h1>


        <h3>
        {profile}
        </h3>


        <p>
        {description}
        </p>


        <h4>
        COMPETENCY MODEL
        </h4>


        <div class="competency-list">

        {weight_html}

        </div>


        <h4>
        TOP CANDIDATES
        </h4>


        {players}


        </section>

        </div>

        """

    return sections


def main():

    print("=" * 70)
    print("SCOUTVISION — SERBIA 1 ALL PLAYERS RECRUITMENT BOARD")
    print("=" * 70)

    template = TEMPLATE_FILE.read_text(
        encoding="utf-8"
    )

    css = CSS_FILE.read_text(
        encoding="utf-8"
    )

    template = template.replace(
        '<link rel="stylesheet" href="recruitment_board.css">',
        f"<style>{css}</style>"
    )

    excel = pd.ExcelFile(INPUT_FILE)

    ranked_df = pd.read_excel(
        RANKED_FILE,
        sheet_name="All Ranked"
    )

    players_analysed = len(ranked_df)

    archetype_count = sum(
        1
        for sheet in excel.sheet_names
        if sheet != "TOP 5 ALL ARCHETYPES"
    )

    position_count = (
        ranked_df["Position Group"].nunique()
        if "Position Group" in ranked_df.columns
        else 0
    )

    html = template.replace(
        "{{ARCHETYPE_SECTIONS}}",
        build_sections()
    )

    html = html.replace(
        "{{COMPETITION_U25}}",
        "Serbia 1 ALL PLAYERS"
    )

    html = html.replace(
        "{{COMPETITION}}",
        "Serbia 1"
    )

    html = html.replace(
        "{{PLAYERS_ANALYSED}}",
        str(players_analysed)
    )

    html = html.replace(
        "{{ARCHETYPE_COUNT}}",
        str(archetype_count)
    )

    html = html.replace(
        "{{POSITION_COUNT}}",
        str(position_count)
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        html,
        encoding="utf-8"
    )

    print()
    print("Players analysed:", players_analysed)
    print("Archetypes:", archetype_count)
    print("Position groups:", position_count)
    print()
    print("✅ Serbia ALL Recruitment Board V3 built")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
