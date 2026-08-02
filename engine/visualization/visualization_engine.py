"""
visualization_engine.py

Orchestratorul central pentru ScoutVision v1.1 Visualization Engine.

Responsabilități:
- validează fișierul de rankings;
- creează structura standard de directoare pentru grafice;
- încarcă și normalizează datele necesare vizualizărilor;
- execută generatoarele de grafice într-un mod controlat;
- întoarce un rezumat standardizat către pipeline.

Acest modul nu conține logica grafică specifică fiecărui chart. Graficele
individuale rămân în module dedicate, iar acest fișier le coordonează.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from .distributions import create_position_distribution


ChartGenerator = Callable[[Path, Path], Any]


class VisualizationEngineError(RuntimeError):
    """Eroare controlată produsă de Visualization Engine."""


@dataclass(frozen=True)
class VisualizationPaths:
    """Structura standard de directoare folosită de ScoutVision."""

    root: Path

    @property
    def distributions(self) -> Path:
        return self.root / "distributions"

    @property
    def player_profiles(self) -> Path:
        return self.root / "player_profiles"

    @property
    def radar_charts(self) -> Path:
        return self.player_profiles / "radar_charts"

    @property
    def percentile_bars(self) -> Path:
        return self.player_profiles / "percentile_bars"

    @property
    def position_rankings(self) -> Path:
        return self.root / "position_rankings"

    @property
    def metadata(self) -> Path:
        return self.root / "metadata"

    def create_all(self) -> None:
        """Creează toate directoarele standard dacă nu există."""

        directories = (
            self.root,
            self.distributions,
            self.player_profiles,
            self.radar_charts,
            self.percentile_bars,
            self.position_rankings,
            self.metadata,
        )

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@dataclass
class VisualizationResult:
    """Rezultatul standard al unei rulări Visualization Engine."""

    generated_charts: list[Path] = field(default_factory=list)
    failed_charts: dict[str, str] = field(default_factory=dict)
    ranked_players: int = 0
    position_groups: int = 0

    @property
    def generated_count(self) -> int:
        return len(self.generated_charts)

    @property
    def failed_count(self) -> int:
        return len(self.failed_charts)

    @property
    def success(self) -> bool:
        return self.failed_count == 0

    def to_dict(self) -> dict[str, Any]:
        """Returnează rezultatul într-un format potrivit pentru pipeline."""

        return {
            "success": self.success,
            "generated_count": self.generated_count,
            "failed_count": self.failed_count,
            "generated_charts": [
                str(path) for path in self.generated_charts
            ],
            "failed_charts": self.failed_charts.copy(),
            "ranked_players": self.ranked_players,
            "position_groups": self.position_groups,
        }


class VisualizationEngine:
    """Coordonează toate vizualizările produse de ScoutVision."""

    REQUIRED_SHEET = "All Ranked"
    REQUIRED_COLUMNS = {
        "Player",
        "Team",
        "Position Group",
        "Performance Score",
        "Recruitment Score",
    }

    def __init__(
        self,
        rankings_file: Path,
        output_folder: Path,
    ) -> None:
        self.rankings_file = Path(rankings_file)
        self.paths = VisualizationPaths(Path(output_folder))

    def run(self) -> dict[str, Any]:
        """
        Rulează toate vizualizările active și returnează un rezumat.

        Graficele sunt executate independent. O eroare la un chart este
        raportată în rezultat fără să ascundă celelalte rezultate generate.
        """

        ranked_players = self._load_and_validate_rankings()
        self.paths.create_all()

        result = VisualizationResult(
            ranked_players=len(ranked_players),
            position_groups=int(
                ranked_players["Position Group"].nunique(dropna=True)
            ),
        )

        chart_jobs: tuple[
            tuple[str, ChartGenerator, Path], ...
        ] = (
            (
                "position_distribution",
                create_position_distribution,
                self.paths.distributions,
            ),
        )

        for chart_name, generator, output_directory in chart_jobs:
            self._execute_chart(
                chart_name=chart_name,
                generator=generator,
                output_directory=output_directory,
                result=result,
            )

        return result.to_dict()

    def _load_and_validate_rankings(self) -> pd.DataFrame:
        """Încarcă foaia principală și validează schema minimă necesară."""

        if not self.rankings_file.exists():
            raise VisualizationEngineError(
                "Rankings file does not exist: "
                f"{self.rankings_file}"
            )

        if self.rankings_file.suffix.lower() not in {".xlsx", ".xls"}:
            raise VisualizationEngineError(
                "Rankings file must be an Excel file: "
                f"{self.rankings_file}"
            )

        try:
            excel_file = pd.ExcelFile(self.rankings_file)
        except Exception as exc:
            raise VisualizationEngineError(
                "Rankings file could not be opened: "
                f"{self.rankings_file}"
            ) from exc

        if self.REQUIRED_SHEET not in excel_file.sheet_names:
            raise VisualizationEngineError(
                f"Required sheet '{self.REQUIRED_SHEET}' was not found. "
                f"Available sheets: {', '.join(excel_file.sheet_names)}"
            )

        try:
            dataframe = pd.read_excel(
                self.rankings_file,
                sheet_name=self.REQUIRED_SHEET,
            )
        except Exception as exc:
            raise VisualizationEngineError(
                f"Sheet '{self.REQUIRED_SHEET}' could not be read."
            ) from exc

        missing_columns = sorted(
            self.REQUIRED_COLUMNS.difference(dataframe.columns)
        )

        if missing_columns:
            raise VisualizationEngineError(
                "Rankings file is missing required columns: "
                f"{', '.join(missing_columns)}"
            )

        if dataframe.empty:
            raise VisualizationEngineError(
                f"Sheet '{self.REQUIRED_SHEET}' contains no players."
            )

        dataframe = dataframe.copy()
        dataframe["Position Group"] = (
            dataframe["Position Group"]
            .astype("string")
            .str.strip()
        )

        dataframe = dataframe.dropna(
            subset=["Player", "Position Group"]
        )

        if dataframe.empty:
            raise VisualizationEngineError(
                "No valid players remained after rankings validation."
            )

        return dataframe

    def _execute_chart(
        self,
        chart_name: str,
        generator: ChartGenerator,
        output_directory: Path,
        result: VisualizationResult,
    ) -> None:
        """Execută în siguranță un generator individual de grafice."""

        try:
            generator(
                self.rankings_file,
                output_directory,
            )
        except Exception as exc:
            result.failed_charts[chart_name] = (
                f"{type(exc).__name__}: {exc}"
            )
            return

        generated_files = sorted(
            path
            for path in output_directory.glob(f"{chart_name}.*")
            if path.is_file()
        )

        result.generated_charts.extend(generated_files)


def create_visualizations(
    rankings_file: Path,
    output_folder: Path,
) -> dict[str, Any]:
    """Interfață funcțională simplă pentru integrarea în pipeline."""

    engine = VisualizationEngine(
        rankings_file=rankings_file,
        output_folder=output_folder,
    )

    return engine.run()
