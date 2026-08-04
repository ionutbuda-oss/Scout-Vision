"""
ScoutVision Competency Engine
"""

from engine.competencies.competency_models import COMPETENCY_MODELS


def calculate_competency(player_row, competency_name):
    """
    Calculate a single competency score from one player row.

    Parameters
    ----------
    player_row : dict-like
        Dictionary or pandas Series containing player KPIs.

    competency_name : str
        Example: "PROGRESSION"

    Returns
    -------
    float
    """

    model = COMPETENCY_MODELS[competency_name]

    score = 0.0

    for kpi, weight in model.items():

        value = float(player_row.get(kpi, 0))

        score += value * weight

    return round(score, 2)


def calculate_all_competencies(player_row):

    results = {}

    for competency in COMPETENCY_MODELS:

        results[competency] = calculate_competency(
            player_row,
            competency
        )

    return results
