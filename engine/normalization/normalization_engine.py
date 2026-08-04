"""
ScoutVision Normalization Engine

Transforms raw KPIs into percentile scores
within each competition and position group.
"""

import pandas as pd

from engine.normalization.percentile import percentile


def normalize_dataframe(
    dataframe: pd.DataFrame,
    kpis: list[str],
    competition_column: str = "Competition",
    position_column: str = "Position Group",
) -> pd.DataFrame:

    df = dataframe.copy()

    grouped = df.groupby(
        [competition_column, position_column],
        dropna=False
    )

    for kpi in kpis:

        df[kpi] = grouped[kpi].transform(percentile)

    return df
