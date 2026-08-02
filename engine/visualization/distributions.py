"""
distributions.py

Grafice de distribuție pentru ScoutVision.
"""

from pathlib import Path
import pandas as pd

from .base_chart import BaseChart
from .theme import ScoutingTheme


def create_position_distribution(
    rankings_file: Path,
    output_folder: Path,
):
    """
    Creează distribuția jucătorilor pe posturi.
    """

    df = pd.read_excel(
        rankings_file,
        sheet_name="All Ranked",
    )

    counts = (
        df["Position Group"]
        .value_counts()
        .sort_index()
    )

    chart = BaseChart(
        "Position Distribution"
    )

    fig, ax = chart.create_figure()

    ax.bar(
        counts.index,
        counts.values,
        color=ScoutingTheme.SECONDARY,
    )

    ax.set_xlabel("Position Group")
    ax.set_ylabel("Players")

    chart.save_png(
        fig,
        output_folder / "position_distribution.png",
    )

    chart.save_json(
        output_folder / "position_distribution.json",
        {
            "title": "Position Distribution",
            "data": counts.to_dict(),
        },
    )
