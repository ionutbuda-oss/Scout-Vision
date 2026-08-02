from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "SuperLiga_2021_2026.xlsx"


def main() -> None:
    df = pd.read_excel(INPUT_FILE)

    print("\nDIMENSIUNEA BAZEI")
    print(f"Rânduri: {df.shape[0]}")
    print(f"Coloane: {df.shape[1]}")

    print("\nNUMĂR DE JUCĂTORI PE SEZON")
    print(df["Season"].value_counts().sort_index())

    print("\nCOLOANE")
    for index, column in enumerate(df.columns, start=1):
        print(f"{index}. {column}")

    print("\nVALORI LIPSĂ PE COLOANE")
    missing = df.isna().sum().sort_values(ascending=False)
    print(missing[missing > 0])

    print("\nTIPURI DE DATE")
    print(df.dtypes)

    duplicate_rows = df.duplicated().sum()

    print("\nDUPLICATE PERFECTE")
    print(duplicate_rows)

    output_summary = BASE_DIR / "dataset_summary.xlsx"

    season_summary = (
        df.groupby("Season")
        .size()
        .reset_index(name="Observations")
    )

    missing_summary = (
        df.isna()
        .sum()
        .reset_index()
    )
    missing_summary.columns = ["Column", "Missing_values"]
    missing_summary["Missing_percentage"] = (
        missing_summary["Missing_values"] / len(df) * 100
    )

    column_types = pd.DataFrame({
        "Column": df.columns,
        "Data_type": df.dtypes.astype(str).values,
    })

    with pd.ExcelWriter(output_summary) as writer:
        season_summary.to_excel(
            writer,
            sheet_name="Seasons",
            index=False,
        )
        missing_summary.to_excel(
            writer,
            sheet_name="Missing_values",
            index=False,
        )
        column_types.to_excel(
            writer,
            sheet_name="Column_types",
            index=False,
        )

    print(f"\nRaport creat: {output_summary}")


if __name__ == "__main__":
    main()
