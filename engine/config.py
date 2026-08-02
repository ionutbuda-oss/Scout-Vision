from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    base_dir: Path = Path(__file__).resolve().parents[1]
    competition_name: str = "France National"
    input_filename: str = "L3-France.xlsx"
    max_age: int = 25
    minimum_matches: int = 15

    @property
    def database_file(self) -> Path:
        return self.base_dir / "databases" / self.input_filename

    @property
    def prepared_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "prepared"
            / "France_L3_U25_prepared.xlsx"
        )

    @property
    def rankings_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "rankings"
            / "France_L3_U25_rankings.xlsx"
        )

    @property
    def report_file(self) -> Path:
        return (
            self.base_dir
            / "outputs"
            / "reports"
            / "France_National_U25_Scouting_Report.pdf"
        )

    @property
    def charts_dir(self) -> Path:
        return self.base_dir / "outputs" / "charts"
