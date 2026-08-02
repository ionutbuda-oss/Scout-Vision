"""
scouting_dataset.py

Modelul central de date pentru ScoutVision.

Toate modulele (Visualization, Reports, Club Fit,
Similarity etc.) vor primi un obiect ScoutingDataset,
nu vor citi fișiere Excel.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class ScoutingDataset:
    """
    Containerul principal de date al aplicației.
    """

    # baza pregătită
    prepared: pd.DataFrame

    # jucătorii clasați
    ranked: pd.DataFrame

    # Top 10 pe fiecare post
    shortlist: pd.DataFrame

    # Elite U21
    elite_u21: pd.DataFrame

    # metodologia scorului
    methodology: pd.DataFrame

    @property
    def total_players(self) -> int:
        return len(self.ranked)

    @property
    def average_age(self) -> float:
        return round(
            self.ranked["Age"].mean(),
            1,
        )

    @property
    def average_recruitment_score(self) -> float:
        return round(
            self.ranked["Recruitment Score"].mean(),
            1,
        )

    @property
    def priority_targets(self) -> int:
        return len(
            self.ranked[
                self.ranked["Recruitment Score"] >= 85
            ]
        )

    @property
    def position_distribution(self):
        return (
            self.ranked["Position Group"]
            .value_counts()
            .sort_index()
        )
