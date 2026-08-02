from __future__ import annotations

import numpy as np
import pandas as pd

from engine.config import Settings


TOP_N = 10

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


def validate_columns(df: pd.DataFrame) -> None:
    required = {
        "Player",
        "Team",
        "Position",
        "Position Group",
        "Age",
        "Age Profile",
        "Matches played",
    }

    for role_model in ROLE_MODELS.values():
        for category in role_model.values():
            required.update(category["metrics"].keys())

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Lipsesc coloanele necesare pentru scoring:\n"
            + "\n".join(
                f"- {column}"
                for column in sorted(missing)
            )
        )


def percentile_series(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(
        series,
        errors="coerce",
    )

    if numeric.notna().sum() <= 1:
        return pd.Series(
            50.0,
            index=series.index,
        )

    return (
        numeric.rank(
            method="average",
            pct=True,
            na_option="bottom",
        )
        * 100
    )


def weighted_score(
    df: pd.DataFrame,
    metric_weights: dict[str, float],
) -> pd.Series:
    total_weight = float(
        sum(metric_weights.values())
    )

    result = pd.Series(
        0.0,
        index=df.index,
    )

    for metric, weight in metric_weights.items():
        result += (
            df[f"PCTL | {metric}"]
            * (weight / total_weight)
        )

    return result


def age_potential_score(age: pd.Series) -> pd.Series:
    numeric_age = pd.to_numeric(
        age,
        errors="coerce",
    )

    score = 100 - (
        numeric_age - 18
    ) * (45 / 7)

    return score.clip(
        lower=55,
        upper=100,
    )


def sample_confidence(matches: pd.Series) -> pd.Series:
    numeric_matches = pd.to_numeric(
        matches,
        errors="coerce",
    )

    return (
        numeric_matches / 25 * 100
    ).clip(
        lower=0,
        upper=100,
    )


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

    metrics = sorted({
        metric
        for category in model.values()
        for metric in category["metrics"].keys()
    })

    for metric in metrics:
        scored[f"PCTL | {metric}"] = (
            percentile_series(scored[metric])
        )

    category_columns: list[str] = []

    for category_name, category_config in model.items():
        category_column = (
            f"{category_name} Score"
        )
        category_columns.append(
            category_column
        )

        scored[category_column] = weighted_score(
            scored,
            category_config["metrics"],
        )

    performance = pd.Series(
        0.0,
        index=scored.index,
    )

    for category_name, category_config in model.items():
        performance += (
            scored[f"{category_name} Score"]
            * float(category_config["weight"])
        )

    scored["Performance Score"] = (
        performance.round(1)
    )
    scored["Age Potential Score"] = (
        age_potential_score(
            scored["Age"]
        ).round(1)
    )
    scored["Sample Confidence"] = (
        sample_confidence(
            scored["Matches played"]
        ).round(1)
    )

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

    scored.insert(
        0,
        "Rank",
        np.arange(
            1,
            len(scored) + 1,
        ),
    )

    front_columns = [
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
        *category_columns,
    ]

    percentile_columns = [
        column
        for column in scored.columns
        if column.startswith("PCTL | ")
    ]

    remaining_columns = [
        column
        for column in scored.columns
        if column not in (
            front_columns
            + percentile_columns
        )
    ]

    return scored[
        front_columns
        + percentile_columns
        + remaining_columns
    ]


def create_methodology_sheet() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for position_group, model in ROLE_MODELS.items():
        for category_name, category_config in model.items():
            for metric, metric_weight in category_config[
                "metrics"
            ].items():
                rows.append(
                    {
                        "Position Group": position_group,
                        "Category": category_name,
                        "Category Weight": category_config[
                            "weight"
                        ],
                        "Metric": metric,
                        "Metric Weight Within Category": (
                            metric_weight
                        ),
                    }
                )

    return pd.DataFrame(rows)


def score_players(
    settings: Settings,
) -> dict[str, object]:
    df = pd.read_excel(
        settings.prepared_file,
        sheet_name="Main Ranking Pool",
    )

    validate_columns(df)

    ranked_groups: dict[
        str,
        pd.DataFrame,
    ] = {}

    for position_group in ROLE_MODELS:
        group_df = df[
            df["Position Group"]
            == position_group
        ].copy()

        if group_df.empty:
            continue

        ranked_groups[position_group] = (
            score_position_group(
                group_df=group_df,
                position_group=position_group,
            )
        )

    if not ranked_groups:
        raise ValueError(
            "Nu există grupe de posturi eligibile."
        )

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

    settings.rankings_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        settings.rankings_file,
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
            ranking.to_excel(
                writer,
                sheet_name=position_group[:31],
                index=False,
            )

        methodology.to_excel(
            writer,
            sheet_name="Methodology",
            index=False,
        )

    top_players = {
        position_group: {
            "player": ranking.iloc[0]["Player"],
            "score": float(
                ranking.iloc[0]["Recruitment Score"]
            ),
            "count": len(ranking),
        }
        for position_group, ranking in ranked_groups.items()
    }

    return {
        "ranked_players": len(all_ranked),
        "elite_u21": len(elite_u21),
        "position_groups": len(ranked_groups),
        "top_players": top_players,
    }
