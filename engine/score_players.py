from __future__ import annotations

import numpy as np
import pandas as pd

from engine.config import Settings
from engine.scoring.profile_models import (
    ROLE_MODELS,
    iter_required_metrics,
    validate_role_models,
)


TOP_N = 10


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

    validate_role_models()
    required.update(iter_required_metrics())

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

    valid = numeric.notna()
    valid_count = int(valid.sum())

    result = pd.Series(
        float("nan"),
        index=series.index,
        dtype="float64",
    )

    if valid_count == 0:
        return result

    if valid_count == 1:
        result.loc[valid] = 50.0
        return result

    result.loc[valid] = (
        numeric.loc[valid].rank(
            method="average",
            pct=True,
        )
        * 100
    )

    return result


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

    # Season Performance is the unweighted arithmetic mean of active
    # position-specific competency scores. Competencies with weight 0 are
    # supporting indicators and do not influence performance evaluation.
    active_category_columns = [
        f"{category_name} Score"
        for category_name, category_config in model.items()
        if float(category_config["weight"]) > 0
    ]

    scored["Performance Score"] = (
        scored[active_category_columns].mean(axis=1).round(1)
    )

    # Scout Score is the weighted mean of competency scores using the
    # position-model competency weights from ROLE_MODELS.
    scout_score = pd.Series(0.0, index=scored.index)
    for category_name, category_config in model.items():
        scout_score += (
            scored[f"{category_name} Score"]
            * float(category_config["weight"])
        )
    scored["Scout Score"] = scout_score.round(1)
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

    # Backward-compatible alias. Recruitment Score must remain numerically
    # identical to Scout Score in ScoutVision v1.0. Age Potential and Sample
    # Confidence are separate contextual indicators and do not alter ranking.
    scored["Recruitment Score"] = scored["Scout Score"]

    scored["Recommendation"] = scored[
        "Scout Score"
    ].apply(recommendation_label)

    scored = scored.sort_values(
        by=[
            "Scout Score",
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
        "Scout Score",
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
            "Scout Score",
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
                ranking.iloc[0]["Scout Score"]
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


if __name__ == "__main__":
    settings = Settings()

    result = score_players(settings)

    print("✅ Rankings generated")
    print(settings.rankings_file)

    for key, value in result.items():
        if key != "top_players":
            print(f"{key}: {value}")
