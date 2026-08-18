from pathlib import Path
import pandas as pd

DATABASES = {
    "SPAIN 2": "L2_Spain.xlsx",
    "BELGIUM 2": "L2-Belgia.xlsx",
    "FRANCE 2": "L2-France.xlsx",
    "FRANCE 3": "L3-France.xlsx",
    "GERMANY 3": "L3-Germania.xlsx",
    "CZECHIA 1": "Liga 1-Cehia.xlsx",
    "SERBIA 1": "Liga 1-Serbia.xlsx",
    "PORTUGAL 2": "Liga 2-Portugal.xlsx",
}

TODAY = pd.Timestamp("2026-08-17")

MIN_MINUTES = 900
MIN_MATCHES = 10


def main():

    all_candidates = []

    print("=" * 80)
    print("SCOUTVISION — FREE AGENTS ALL LEAGUES")
    print("=" * 80)

    for league, filename in DATABASES.items():

        path = Path("databases") / filename
        df = pd.read_excel(path)

        print()
        print("-" * 80)
        print(league)
        print("Players:", len(df))

        if "Contract expires" not in df.columns:
            print("⚠ CONTRACT DATA UNAVAILABLE")
            continue

        df["Contract expires"] = pd.to_datetime(
            df["Contract expires"],
            errors="coerce"
        )

        candidates = df[
            df["Contract expires"].notna()
            & (df["Contract expires"] <= TODAY)
        ].copy()

        if "Minutes played" in candidates.columns:
            candidates["Minutes played"] = pd.to_numeric(
                candidates["Minutes played"],
                errors="coerce"
            ).fillna(0)

        if "Matches played" in candidates.columns:
            candidates["Matches played"] = pd.to_numeric(
                candidates["Matches played"],
                errors="coerce"
            ).fillna(0)

        candidates["League"] = league

        candidates["Sample Status"] = "LOW SAMPLE"

        candidates.loc[
            (candidates["Minutes played"] >= MIN_MINUTES)
            & (candidates["Matches played"] >= MIN_MATCHES),
            "Sample Status"
        ] = "ADEQUATE SAMPLE"

        all_candidates.append(candidates)

        print("Expired contracts:", len(candidates))

        adequate = candidates[
            candidates["Sample Status"] == "ADEQUATE SAMPLE"
        ]

        print("Adequate sample:", len(adequate))

    if not all_candidates:
        print()
        print("No contract-based candidates found.")
        return

    result = pd.concat(
        all_candidates,
        ignore_index=True,
        sort=False
    )

    columns = [
        "League",
        "Player",
        "Team",
        "Position",
        "Age",
        "Market value",
        "Contract expires",
        "Matches played",
        "Minutes played",
        "Goals",
        "xG",
        "Assists",
        "xA",
        "Sample Status",
    ]

    columns = [
        c for c in columns
        if c in result.columns
    ]

    result = result[columns]

    result = result.sort_values(
        ["Sample Status", "Minutes played"],
        ascending=[True, False]
    )

    output_dir = Path("outputs/free_agents")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "free_agents_contract_confirmed.xlsx"
    )

    result.to_excel(
        output_file,
        index=False
    )

    print()
    print("=" * 80)
    print("FREE AGENT SCREENING COMPLETE")
    print("=" * 80)

    print("Total contract-expired:", len(result))

    print(
        "Adequate sample:",
        len(
            result[
                result["Sample Status"] == "ADEQUATE SAMPLE"
            ]
        )
    )

    print()
    print("Output:")
    print(output_file)


if __name__ == "__main__":
    main()
