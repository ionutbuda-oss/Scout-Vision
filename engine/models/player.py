from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd


@dataclass(slots=True)
class Player:
    """
    Core player model used across ScoutVision.

    Every module (Visualization, Reports, Club Fit, Dashboard)
    should receive a Player object instead of a pandas row.
    """

    name: str
    club: str
    position: str
    age: int
    matches: int
    scout_score: float

    raw: Dict[str, Any]

    @classmethod
    def from_series(cls, row: pd.Series) -> "Player":
        """
        Create a Player instance from a dataframe row.
        """

        return cls(
            name=str(row.get("Player", "")),
            club=str(row.get("Team", "")),
            position=str(row.get("Position", "")),
            age=int(row.get("Age", 0)),
            matches=int(row.get("Matches played", 0)),
            scout_score=float(row.get("Scout Score", 0)),
            raw=row.to_dict(),
        )

    def get(self, column: str, default=None):
        """
        Safe access to any original dataframe column.
        """
        return self.raw.get(column, default)

    @property
    def short_description(self) -> str:
        return (
            f"{self.position} | "
            f"{self.club} | "
            f"{self.age} yrs"
        )

    @property
    def score_label(self) -> str:

        score = self.scout_score

        if score >= 85:
            return "Elite"

        if score >= 75:
            return "Excellent"

        if score >= 65:
            return "Good"

        if score >= 55:
            return "Average"

        return "Development"

    def __str__(self) -> str:
        return (
            f"{self.name} "
            f"({self.position}) "
            f"- {self.scout_score:.1f}"
        )
