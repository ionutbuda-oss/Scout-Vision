"""
ScoutVision Pipeline Engine
"""

import pandas as pd

from engine.preparation.database_preparation import prepare_database
from engine.normalization.normalization_engine import normalize_dataframe
from engine.competencies.competency_engine import calculate_all_competencies
from engine.competencies.competency_models import COMPETENCY_MODELS
from engine.position.position_engine import calculate_position_score


def run_pipeline(
    dataframe: pd.DataFrame,
    competition: str,
):

    print("=" * 70)
    print("SCOUTVISION PIPELINE")
    print("=" * 70)

    # Preparation
    dataframe = prepare_database(
        dataframe,
        competition=competition,
    )

    # KPI list
    kpis = sorted({
        kpi
        for model in COMPETENCY_MODELS.values()
        for kpi in model.keys()
    })

    # Normalization
    dataframe = normalize_dataframe(
        dataframe,
        kpis,
    )

    results = []

    # Player loop
    for _, player in dataframe.iterrows():

        competencies = calculate_all_competencies(player)

        position_group = player["Position Group"]

        position_result = calculate_position_score(
            position_group,
            competencies,
        )

        row = {

            "Player": player["Player"],
            "Team": player["Team"],
            "Position": player["Position"],
            "Position Group": position_group,

            "Position Score": position_result["score"],
            "Core Score": position_result["core_score"],
            "Primary Score": position_result["primary_score"],
            "Support Score": position_result["support_score"],
            "Multiplier": position_result["multiplier"],

        }

        row.update(competencies)

        results.append(row)

    return pd.DataFrame(results)

