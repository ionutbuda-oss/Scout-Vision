"""
base_chart.py

Clasa de bază pentru toate graficele din ScoutVision.
Toate graficele moștenesc această clasă.
"""

from pathlib import Path
import json

import matplotlib.pyplot as plt

from .theme import ScoutingTheme


class BaseChart:

    def __init__(self, title: str):
        self.title = title

    def create_figure(self):
        """
        Creează figura folosind tema aplicației.
        """

        fig, ax = plt.subplots(
            figsize=(
                ScoutingTheme.FIG_WIDTH,
                ScoutingTheme.FIG_HEIGHT,
            ),
            dpi=ScoutingTheme.DPI,
        )

        fig.patch.set_facecolor(
            ScoutingTheme.BACKGROUND
        )

        ax.set_facecolor(
            ScoutingTheme.BACKGROUND
        )

        ax.grid(
            axis="y",
            color=ScoutingTheme.GRID,
            linestyle="--",
            linewidth=0.7,
        )

        ax.set_title(
            self.title,
            fontsize=ScoutingTheme.TITLE_SIZE,
            color=ScoutingTheme.TEXT,
            weight="bold",
            pad=15,
        )

        ax.tick_params(
            labelsize=ScoutingTheme.TICK_SIZE
        )

        return fig, ax

    def save_png(self, figure, output_path: Path):

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=ScoutingTheme.DPI,
            bbox_inches="tight",
        )

        plt.close(figure)

    def save_json(
        self,
        output_path: Path,
        metadata: dict,
    ):

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4,
                ensure_ascii=False,
            )
