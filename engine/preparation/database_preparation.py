"""
ScoutVision Database Preparation Engine
"""

import pandas as pd

from engine.preparation.position_mapper import map_position


def prepare_database(
    dataframe: pd.DataFrame,
    competition: str,
):

    df = dataframe.copy()

    # Competition
    df["Competition"] = competition

    # Position Group
    df["Position Group"] = df["Position"].apply(map_position)

    # Remove Goalkeepers
    df = df[df["Position Group"] != "GK"]

    return df
