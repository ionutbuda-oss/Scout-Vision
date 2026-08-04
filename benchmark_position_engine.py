import pandas as pd

from engine.pipeline.pipeline_engine import run_pipeline

LEAGUES = [

    (
        "Belgium Challenger Pro League",
        "databases/Belgia_L2.xlsx"
    ),

    (
        "France National",
        "databases/L3-France.xlsx"
    ),

    (
        "Germany Regionalliga",
        "databases/L3-Germania.xlsx"
    ),

]

POSITIONS = [
    "CB",
    "FB_WB",
    "DM",
    "CM",
    "AM",
    "Winger",
    "ST"
]


for competition, file in LEAGUES:

    print("\n")
    print("=" * 100)
    print(competition.upper())
    print("=" * 100)

    df = pd.read_excel(file)

    results = run_pipeline(
        df,
        competition=competition
    )

    for position in POSITIONS:

        top = (
            results[
                results["Position Group"] == position
            ]
            .sort_values(
                "Position Score",
                ascending=False
            )
            .head(5)
        )

        print("\n")
        print("-" * 90)
        print(position)
        print("-" * 90)

        print(

            top[
                [

                    "Player",
                    "Team",
                    "Position",
                    "Position Score",

                ]

            ].to_string(index=False)

        )

