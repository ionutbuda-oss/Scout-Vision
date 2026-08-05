from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]+", "_", ascii_value).strip("_")


@dataclass(frozen=True)
class Settings:
    """Competition-specific ScoutVision settings.

    A new league now requires only a database filename and competition name;
    output filenames are derived automatically and remain isolated by league.
    """

    base_dir: Path = Path(__file__).resolve().parents[1]
    competition_name: str = "Germany Regionalliga"
    input_filename: str = "L3-Germania.xlsx"
    max_age: int = 25
    minimum_matches: int = 15

    @property
    def competition_slug(self) -> str:
        return _slug(self.competition_name)

    @property
    def database_file(self) -> Path:
        return self.base_dir / "databases" / self.input_filename

    @property
    def prepared_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "prepared"
            / f"{self.competition_slug}_U25_prepared.xlsx"
        )

    @property
    def rankings_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "rankings"
            / f"{self.competition_slug}_U25_rankings.xlsx"
        )

    @property
    def report_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "reports"
            / f"{self.competition_slug}_U25_Scouting_Report.pdf"
        )

    @property
    def charts_dir(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "charts"
            / self.competition_slug
        )
