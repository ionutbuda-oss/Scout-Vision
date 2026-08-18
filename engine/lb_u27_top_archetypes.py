from pathlib import Path
import pandas as pd

from engine.reports.archetype_ranking import (
    ARCHETYPE_WEIGHTS,
    ARCHETYPE_POSITIONS,
    calculate_archetype_score,
)

DATABASE_FILES = [
    "databases/L2_Spain.xlsx",
    "databases/L2-Belgia.xlsx",
    "databases/L2-France.xlsx",
    "databases/L3-France.xlsx",
    "databases/L3-Germania.xlsx",
    "databases/Liga 1-Cehia.xlsx",
    "databases/Liga 1-Serbia.xlsx",
    "databases/Liga 2-Portugal.xlsx",
]

OUTPUT_FILE = Path(
    "outputs/free_agents/lb_u27_top_archetypes.xlsx"
)

TARGET_PLAYERS = [
    "N. May",
    "Rodrigo Rêgo",
    "F. Mabani",
    "A. Avdić",
    "I. Diallo",
    "A. Koum",
    "S. Bukinac",
    "Lucas Calodat",
    "S. de Grand",
    "D. Jurásek",
]


def extract_metrics(row):
    metrics = {}

    for col in row.index:
        if not str(col).endswith(" Score"):
            continue

        if col in {
            "Scout Score",
            "Performance Score",
            "Age Potential Score",
            "Recruitment Score",
        }:
            continue

        if pd.notna(row[col]):
            metrics[
                str(col).replace(" Score", "")
            ] = float(row[col])

    return metrics


def top_archetypes(row):

    position = str(
        row["Position Group"]
    ).strip()

    metrics = extract_metrics(row)

    results = []

    for archetype in ARCHETYPE_WEIGHTS:

        allowed = ARCHETYPE_POSITIONS.get(
            archetype
        )

        if allowed and position not in allowed:
            continue

        score = calculate_archetype_score(
            metrics,
            archetype,
        )

        if score > 0:
            results.append(
                (
                    archetype,
                    score,
                )
            )

    return sorted(
        results,
        key=lambda x: x[1],
        reverse=True,
    )[:3]


def main():

    from engine.config import Settings
    from engine.score_players import score_position_group
    from engine.prepare_database import classify_position

    frames = []

    for database in DATABASE_FILES:

        path = Path(database)

        if not path.exists():
            continue

        df = pd.read_excel(path)
        df.columns = df.columns.astype(str).str.strip()

        if "Player" not in df.columns:
            continue

        df["Player"] = df["Player"].astype(str).str.strip()

        target = df[
            df["Player"].isin(TARGET_PLAYERS)
        ].copy()

        if target.empty:
            continue

        target["Age"] = pd.to_numeric(
            target["Age"],
            errors="coerce"
        )

        target = target[
            target["Age"] < 27
        ].copy()

        if target.empty:
            continue

        target["Position Group"] = target[
            "Position"
        ].apply(classify_position)

        from engine.prepare_database import (
            classify_age_profile,
            classify_sample,
        )

        target["Age Profile"] = target[
            "Age"
        ].apply(classify_age_profile)

        target["Sample Category"] = target[
            "Matches played"
        ].apply(
            lambda matches: classify_sample(
                matches,
                Settings(),
            )
        )

        target["Source Database"] = path.name

        frames.append(target)

    if not frames:
        raise ValueError(
            "Nu a fost găsit niciun candidat în bazele originale."
        )

    candidates = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    # Eliminăm duplicatele dacă același jucător apare în mai multe baze.
    candidates = candidates.drop_duplicates(
        subset=["Player"],
        keep="first",
    ).copy()

    ranked = []

    for position_group, group in candidates.groupby(
        "Position Group"
    ):

        scored = score_position_group(
            group_df=group.copy(),
            position_group=position_group,
        )

        ranked.append(scored)

    if not ranked:
        raise ValueError(
            "Nu există candidați eligibili pentru scoring."
        )

    scored_all = pd.concat(
        ranked,
        ignore_index=True,
        sort=False,
    )

    # ============================================================
    # SCOUTVISION V3 REPORT DATASET
    # ============================================================

    REPORT_RANKINGS = Path(
        "outputs/rankings/LB_U27_Bulgaria_Targets_rankings.xlsx"
    )

    REPORT_RANKINGS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        REPORT_RANKINGS,
        engine="openpyxl",
    ) as writer:

        scored_all.to_excel(
            writer,
            sheet_name="All Ranked",
            index=False,
        )

        fb_wb = scored_all[
            scored_all["Position Group"].astype(str).str.strip()
            == "FB_WB"
        ].copy()

        fb_wb.to_excel(
            writer,
            sheet_name="FB_WB",
            index=False,
        )

    print()
    print("=" * 100)
    print("SCOUTVISION — V3 REPORT RANKINGS GENERATED")
    print("=" * 100)
    print(
        "Output:",
        REPORT_RANKINGS
    )

    output = []

    print("=" * 100)
    print("SCOUTVISION — U27 ATTACKING LEFT-BACK SEARCH")
    print("=" * 100)

    for _, row in scored_all.iterrows():

        archetypes = top_archetypes(row)

        result = {
            "Player": row["Player"],
            "Team": row.get("Team", ""),
            "Age": row["Age"],
            "Position": row["Position"],
            "Position Group": row["Position Group"],
            "Matches played": row["Matches played"],
            "Minutes played": row["Minutes played"],
            "Scout Score": row["Scout Score"],
            "Performance Score": row["Performance Score"],
            "Recommendation": row["Recommendation"],
            "Source Database": row.get(
                "Source Database",
                "",
            ),
        }

        for i in range(3):

            if i < len(archetypes):

                result[
                    f"Archetype {i+1}"
                ] = archetypes[i][0]

                result[
                    f"Archetype {i+1} Score"
                ] = archetypes[i][1]

            else:

                result[
                    f"Archetype {i+1}"
                ] = ""

                result[
                    f"Archetype {i+1} Score"
                ] = ""

        output.append(result)

        print()
        print(
            f'{row["Player"]:<24} '
            f'{int(row["Age"])} ani | '
            f'{row["Position"]} | '
            f'Scout {row["Scout Score"]}'
        )

        for i, (name, score) in enumerate(
            archetypes,
            start=1
        ):
            print(
                f"   {i}. {name:<30} {score}"
            )

    result_df = pd.DataFrame(output)

    result_df = result_df.sort_values(
        "Scout Score",
        ascending=False,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        result_df.to_excel(
            writer,
            sheet_name="LB U27",
            index=False,
        )

    print()
    print("=" * 100)
    print("✅ U27 ATTACKING LB ARCHETYPE BOARD GENERATED")
    print("=" * 100)
    print(
        "Candidates analysed:",
        len(result_df)
    )
    print(
        "Output:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
