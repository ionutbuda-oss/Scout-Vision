"""
ScoutVision Percentile Engine
"""

import pandas as pd


def percentile(series: pd.Series) -> pd.Series:
    """
    Convert a numeric Series into percentile scores (0-100).

    Higher values receive higher percentiles.
    """

    return series.rank(method="average", pct=True) * 100
