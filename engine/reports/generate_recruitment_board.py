"""
ScoutVision V3 - Recruitment Board Generator

Creates archetype-based recruitment shortlists.
"""

from pathlib import Path

import pandas as pd

from engine.config import Settings

from engine.reports.archetype_descriptions import (
    ARCHETYPE_DESCRIPTIONS,
)

from engine.reports.archetype_ranking import (
    ARCHETYPE_WEIGHTS,
)


SETTINGS = Settings()

INPUT_FILE = (
    SETTINGS.rankings_file.parent
    / f"{SETTINGS.competition_slug}_U25_archetype_rankings.xlsx"
)

OUTPUT_DIR = Path("outputs/recruitment_boards")

OUTPUT_FILE = (
    OUTPUT_DIR
    / f"{SETTINGS.competition_slug}_U25_Archetype_Top5.html"
)


TOP_N = 5


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    excel = pd.ExcelFile(INPUT_FILE)

    sections = []

    for sheet in excel.sheet_names:

        df = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet
        )

        if df.empty:
            continue


        top = df.head(TOP_N)


        rows = ""

        for _, player in top.iterrows():

            rows += f"""
            <tr>
                <td>{player.get('Rank','')}</td>
                <td>{player.get('Player','')}</td>
                <td>{player.get('Team','')}</td>
                <td>{player.get('Position','')}</td>
                <td>{player.get('Archetype Score','')}</td>
                <td>{player.get('Scout Score','')}</td>
            </tr>
            """


        archetype_info = ARCHETYPE_DESCRIPTIONS.get(
            sheet,
            {}
        )

        description = archetype_info.get(
            "description",
            ""
        )

        profile = archetype_info.get(
            "profile",
            ""
        )

        weights = ARCHETYPE_WEIGHTS.get(
            sheet,
            {}
        )

        weight_html = ""

        for metric, weight in weights.items():
            weight_html += f"<li>{metric}: {int(weight*100)}%</li>"


        sections.append(
            f"""
            <h2>{sheet}</h2>

            <h3>{profile}</h3>

            <p>{description}</p>

            <h4>Evaluation model</h4>

            <ul>
            {weight_html}
            </ul>


            <table>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th>Team</th>
                    <th>Position</th>
                    <th>Archetype Score</th>
                    <th>Scout Score</th>
                </tr>

                {rows}

            </table>
            """
        )


    html = f"""
    <html>
    <head>

    <title>ScoutVision Recruitment Board</title>

    <style>

    body {{
        font-family: Arial;
        margin:40px;
    }}

    h1 {{
        font-size:32px;
    }}

    h2 {{
        margin-top:40px;
    }}

    table {{
        border-collapse: collapse;
        width:100%;
        margin-bottom:30px;
    }}

    td, th {{
        border:1px solid #ccc;
        padding:8px;
        text-align:left;
    }}

    </style>

    </head>

    <body>

    <h1>ScoutVision Recruitment Board</h1>

    <p>
    {SETTINGS.competition_name} — U25 Recruitment Board<br>
    Top 5 players by ScoutVision archetype.
    </p>

    {"".join(sections)}

    </body>
    </html>
    """


    OUTPUT_FILE.write_text(
        html,
        encoding="utf-8"
    )


    print("✅ Recruitment Board generated")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
