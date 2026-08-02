"""
02_score_france_l3_players.py

Calculează scoruri percentile și clasamente pe post pentru jucătorii U25
din France National (Liga 3 Franța), fără portari.

Fișier de intrare:
    France_L3_U25_prepared.xlsx

Fișier rezultat:
    France_L3_U25_rankings.xlsx
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "France_L3_U25_prepared.xlsx"
OUTPUT_FILE = BASE_DIR / "France_L3_U25_rankings.xlsx"

INPUT_SHEET = "Main Ranking Pool"
TOP_N = 10


# Fiecare categorie conține:
# - weight: ponderea categoriei în Performance Score
# - metrics: indicatorii și ponderile lor interne
ROLE_MODELS: dict[str, dict[str, dict[str, object]]] = {
    "CB": {
        "Defending": {
            "weight": 0.45,
            "metrics": {
                "Defensive duels per 90": 0.20,
                "Defensive duels won, %": 0.45,
                "Interceptions per 90": 0.35,
            },
        },
        "Build-up": {
            "weight": 0.30,
            "metrics": {
                "Passes per 90": 0.20,
                "Accurate passes, %": 0.25,
                "Forward passes per 90": 0.30,
                "Accurate forward passes, %": 0.25,
            },
        },
        "Progression": {
            "weight": 0.25,
            "metrics": {
                "Progressive passes per 90": 0.40,
                "Accurate progressive passes, %": 0.25,
                "Passes to final third per 90": 0.20,
                "Accurate passes to final third, %": 0.15,
            },
        },
    },
    "FB_WB": {
        "Defending": {
            "weight": 0.25,
            "metrics": {
                "Defensive duels per 90": 0.25,
                "Defensive duels won, %": 0.45,
                "Interceptions per 90": 0.30,
            },
        },
        "Progression": {
            "weight": 0.25,
            "metrics": {
                "Progressive passes per 90": 0.35,
                "Accurate progressive passes, %": 0.20,
                "Passes to final third per 90": 0.25,
                "Accurate passes to final third, %": 0.20,
            },
        },
        "Chance Creation": {
            "weight": 0.25,
            "metrics": {
                "Crosses per 90": 0.30,
                "Accurate crosses, %": 0.25,
                "xA per 90": 0.25,
                "Assists per 90": 0.20,
            },
        },
        "Ball Carrying": {
            "weight": 0.25,
            "metrics": {
                "Successful attacking actions per 90": 0.25,
                "Dribbles per 90": 0.30,
                "Successful dribbles, %": 0.25,
                "Offensive duels won, %": 0.20,
            },
        },
    },
    "DM": {
        "Ball Winning": {
            "weight": 0.35,
            "metrics": {
                "Defensive duels per 90": 0.25,
                "Defensive duels won, %": 0.40,
                "Interceptions per 90": 0.35,
            },
        },
        "Distribution": {
            "weight": 0.35,
            "metrics": {
                "Passes per 90": 0.25,
                "Accurate passes, %": 0.25,
                "Forward passes per 90": 0.25,
                "Accurate forward passes, %": 0.25,
            },
        },
        "Progression": {
            "weight": 0.30,
            "metrics": {
                "Progressive passes per 90": 0.35,
                "Accurate progressive passes, %": 0.20,
                "Passes to final third per 90": 0.25,
                "Accurate passes to final third, %": 0.20,
            },
        },
    },
    "CM": {
        "Distribution": {
            "weight": 0.30,
            "metrics": {
                "Passes per 90": 0.25,
                "Accurate passes, %": 0.25,
                "Forward passes per 90": 0.25,
                "Accurate forward passes, %": 0.25,
            },
        },
        "Progression": {
            "weight": 0.30,
            "metrics": {
                "Progressive passes per 90": 0.30,
                "Accurate progressive passes, %": 0.15,
                "Passes to final third per 90": 0.30,
                "Accurate passes to final third, %": 0.15,
                "Through passes per 90": 0.10,
            },
        },
        "Creativity": {
            "weight": 0.25,
            "metrics": {
                "Smart passes per 90": 0.25,
                "Accurate smart passes, %": 0.15,
                "Through passes per 90": 0.20,
                "xA per 90": 0.25,
                "Assists per 90": 0.15,
            },
        },
        "Defensive Contribution": {
            "weight": 0.15,
            "metrics": {
                "Defensive duels won, %": 0.40,
                "Interceptions per 90": 0.40,
                "Defensive duels per 90": 0.20,
            },
        },
    },
    "AM": {
        "Creativity": {
            "weight": 0.40,
            "metrics": {
                "Smart passes per 90": 0.20,
                "Accurate smart passes, %": 0.10,
                "Through passes per 90": 0.20,
                "xA per 90": 0.30,
                "Assists per 90": 0.20,
            },
        },
        "Progression": {
            "weight": 0.20,
            "metrics": {
                "Progressive passes per 90": 0.25,
                "Passes to final third per 90": 0.30,
                "Accurate passes to final third, %": 0.20,
                "Successful attacking actions per 90": 0.25,
            },
        },
        "Ball Carrying": {
            "weight": 0.20,
            "metrics": {
                "Dribbles per 90": 0.40,
                "Successful dribbles, %": 0.30,
                "Offensive duels won, %": 0.30,
            },
        },
        "Goal Threat": {
            "weight": 0.20,
            "metrics": {
                "Goals per 90": 0.25,
                "xG per 90": 0.25,
                "Shots per 90": 0.20,
                "Shots on target, %": 0.15,
                "Touches in box per 90": 0.15,
            },
        },
    },
    "Winger": {
        "Ball Carrying": {
            "weight": 0.30,
            "metrics": {
                "Successful attacking actions per 90": 0.25,
                "Dribbles per 90": 0.35,
                "Successful dribbles, %": 0.20,
                "Offensive duels won, %": 0.20,
            },
        },
        "Chance Creation": {
            "weight": 0.30,
            "metrics": {
                "xA per 90": 0.30,
                "Assists per 90": 0.20,
                "Smart passes per 90": 0.15,
                "Through passes per 90": 0.15,
                "Crosses per 90": 0.10,
                "Accurate crosses, %": 0.10,
            },
        },
        "Goal Threat": {
            "weight": 0.30,
            "metrics": {
                "Goals per 90": 0.25,
                "xG per 90": 0.25,
                "Shots per 90": 0.15,
                "Shots on target, %": 0.15,
                "Touches in box per 90": 0.20,
            },
        },
        "Combination Play": {
            "weight": 0.10,
            "metrics": {
                "Passes to final third per 90": 0.35,
                "Accurate passes to final third, %": 0.25,
                "Progressive passes per 90": 0.20,
                "Accurate progressive passes, %": 0.20,
            },
        },
    },
    "ST": {
        "Finishing": {
            "weight": 0.35,
            "metrics": {
                "Goals per 90": 0.30,
                "xG per 90": 0.25,
                "Shots on target, %": 0.20,
                "Goal conversion, %": 0.25,
            },
        },
        "Box Threat": {
            "weight": 0.25,
            "metrics": {
                "Touches in box per 90": 0.40,
                "Shots per 90": 0.35,
                "Successful attacking actions per 90": 0.25,
            },
        },
        "Duels": {
            "weight": 0.20,
            "metrics": {
                "Offensive duels per 90": 0.35,
                "Offensive duels won, %": 0.65,
            },
        },
        "Link Play": {
            "weight": 0.20,
            "metrics": {
                "Assists per 90": 0.20,
                "xA per 90": 0.20,
                "Smart passes per 90": 0.15,
                "Passes to final third per 90": 0.20,
                "Accurate passes, %": 0.25,
            },
        },
    },
}


BASE_OUTPUT_COLUMNS = [
    "Rank",
    "Player",
    "Team",
    "Position",
    "Position Group",
    "Age",
    "Age Profile",
    "Matches played",
    "Performance Score",
    "Recruitment Score",
    "Age Potential Score",
    "Sample Confidence",
    "Recommendation",
]


def validate_input(df: pd.DataFrame) -> None:
    required = {
        "Player",
        "Team",
        "Position",
        "Position Group",
        "Age",
        "Matches played",
    }

    for model in ROLE_MODELS.values():
        for category in model.values():
            required.update(category["metrics"].keys())

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Lipsesc coloanele necesare pentru scoring:\n"
            + "\n".join(f"- {column}" for column in sorted(missing))
        )


def percentile_series(series: pd.Series) -> pd.Series:
    """
    Calculează percentile 0–100 în cadrul postului.
    Metoda average tratează egal valorile identice.
    """
    numeric = pd.to_numeric(series, errors="coerce")

    if numeric.notna().sum() <= 1:
        return pd.Series(50.0, index=series.index)

    return numeric.rank(
        method="average",
        pct=True,
        na_option="bottom",
    ) * 100


def weighted_score(
    df: pd.DataFrame,
    metric_weights: dict[str, float],
) -> pd.Series:
    total_weight = float(sum(metric_weights.values()))

    if total_weight <= 0:
        raise ValueError("Ponderile indicatorilor trebuie să fie pozitive.")

    result = pd.Series(0.0, index=df.index)

    for metric, weight in metric_weights.items():
        percentile_column = f"PCTL | {metric}"
        result += df[percentile_column] * (weight / total_weight)

    return result


def age_potential_score(age: pd.Series) -> pd.Series:
    """
    Bonus moderat pentru potențial de dezvoltare și revânzare.
    18 ani sau mai puțin = 100; 25 ani = aproximativ 55.
    """
    numeric_age = pd.to_numeric(age, errors="coerce")
    score = 100 - (numeric_age - 18) * (45 / 7)
    return score.clip(lower=55, upper=100)


def sample_confidence(matches: pd.Series) -> pd.Series:
    """
    15 meciuri = 60; 25+ meciuri = 100.
    Nu schimbă radical clasamentul, ci diferențiază robustețea eșantionului.
    """
    numeric_matches = pd.to_numeric(matches, errors="coerce")
    return (numeric_matches / 25 * 100).clip(lower=0, upper=100)


def recommendation_label(score: float) -> str:
    if score >= 85:
        return "A+ | Priority Target"
    if score >= 78:
        return "A | Strong Target"
    if score >= 70:
        return "B+ | Shortlist"
    if score >= 62:
        return "B | Monitor"
    return "C | Secondary Option"


def score_position_group(
    group_df: pd.DataFrame,
    position_group: str,
) -> pd.DataFrame:
    model = ROLE_MODELS[position_group]
    scored = group_df.copy()

    all_metrics = sorted({
        metric
        for category in model.values()
        for metric in category["metrics"].keys()
    })

    for metric in all_metrics:
        scored[f"PCTL | {metric}"] = percentile_series(scored[metric])

    category_columns: list[str] = []

    for category_name, category_config in model.items():
        category_column = f"{category_name} Score"
        category_columns.append(category_column)

        scored[category_column] = weighted_score(
            scored,
            category_config["metrics"],
        )

    performance = pd.Series(0.0, index=scored.index)

    for category_name, category_config in model.items():
        performance += (
            scored[f"{category_name} Score"]
            * float(category_config["weight"])
        )

    scored["Performance Score"] = performance.round(1)
    scored["Age Potential Score"] = age_potential_score(
        scored["Age"]
    ).round(1)
    scored["Sample Confidence"] = sample_confidence(
        scored["Matches played"]
    ).round(1)

    # Performanța rămâne elementul dominant.
    scored["Recruitment Score"] = (
        scored["Performance Score"] * 0.80
        + scored["Age Potential Score"] * 0.15
        + scored["Sample Confidence"] * 0.05
    ).round(1)

    scored["Recommendation"] = scored[
        "Recruitment Score"
    ].apply(recommendation_label)

    scored = scored.sort_values(
        by=[
            "Recruitment Score",
            "Performance Score",
            "Age",
            "Matches played",
        ],
        ascending=[
            False,
            False,
            True,
            False,
        ],
    ).reset_index(drop=True)

    scored.insert(0, "Rank", np.arange(1, len(scored) + 1))

    ordered_columns = (
        BASE_OUTPUT_COLUMNS
        + category_columns
        + [
            column
            for column in scored.columns
            if column.startswith("PCTL | ")
        ]
        + [
            column
            for column in scored.columns
            if column not in (
                BASE_OUTPUT_COLUMNS
                + category_columns
                + [
                    col
                    for col in scored.columns
                    if col.startswith("PCTL | ")
                ]
            )
        ]
    )

    # Elimină eventualele coloane repetate, păstrând ordinea.
    ordered_columns = list(dict.fromkeys(ordered_columns))

    return scored[ordered_columns]


def create_methodology_sheet() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for position_group, model in ROLE_MODELS.items():
        for category_name, category_config in model.items():
            for metric, metric_weight in category_config["metrics"].items():
                rows.append({
                    "Position Group": position_group,
                    "Category": category_name,
                    "Category Weight": category_config["weight"],
                    "Metric": metric,
                    "Metric Weight Within Category": metric_weight,
                })

    return pd.DataFrame(rows)


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Nu am găsit fișierul:\n{INPUT_FILE}"
        )

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=INPUT_SHEET,
    )

    validate_input(df)

    ranked_groups: dict[str, pd.DataFrame] = {}

    for position_group in ROLE_MODELS:
        group_df = df[
            df["Position Group"] == position_group
        ].copy()

        if group_df.empty:
            continue

        ranked_groups[position_group] = score_position_group(
            group_df=group_df,
            position_group=position_group,
        )

    if not ranked_groups:
        raise ValueError("Nu au fost găsite posturi eligibile pentru scoring.")

    all_ranked = pd.concat(
        ranked_groups.values(),
        ignore_index=True,
        sort=False,
    )

    shortlist = pd.concat(
        [
            ranking.head(TOP_N)
            for ranking in ranked_groups.values()
        ],
        ignore_index=True,
        sort=False,
    )

    elite_u21 = all_ranked[
        all_ranked["Age"] <= 21
    ].sort_values(
        by=[
            "Recruitment Score",
            "Performance Score",
        ],
        ascending=False,
    ).reset_index(drop=True)

    methodology = create_methodology_sheet()

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:
        shortlist.to_excel(
            writer,
            sheet_name="Shortlist All Positions",
            index=False,
        )

        elite_u21.to_excel(
            writer,
            sheet_name="Elite U21",
            index=False,
        )

        all_ranked.to_excel(
            writer,
            sheet_name="All Ranked",
            index=False,
        )

        for position_group, ranking in ranked_groups.items():
            safe_sheet_name = position_group[:31]
            ranking.to_excel(
                writer,
                sheet_name=safe_sheet_name,
                index=False,
            )

        methodology.to_excel(
            writer,
            sheet_name="Methodology",
            index=False,
        )

    print("=" * 72)
    print("FRANCE NATIONAL U25 — POSITIONAL SCOUTING RANKINGS")
    print("=" * 72)

    for position_group, ranking in ranked_groups.items():
        top_player = ranking.iloc[0]

        print(
            f"{position_group:8} | "
            f"{len(ranking):3} jucători | "
            f"Nr. 1: {top_player['Player']} "
            f"({top_player['Recruitment Score']:.1f})"
        )

    print(f"\nShortlist: Top {TOP_N} pe fiecare post")
    print(f"Fișier creat:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nEROARE:\n{exc}")
        sys.exit(1)
