"""
radar_charts.py

Generator de radar charts pentru ScoutVision v1.1.

Fiecare jucător este evaluat prin categoriile specifice grupei sale de post,
folosind scorurile deja calculate de Scoring Engine. Graficul este scalat
între 0 și 100 și poate fi reutilizat ulterior în Player Cards, PDF Reports
și Dashboard.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .theme import ScoutingTheme


GLOBAL_SCORE_COLUMNS = {
    "Performance Score",
    "Recruitment Score",
    "Age Potential Score",
    "Sample Confidence",
}


class RadarChartError(RuntimeError):
    """Eroare controlată produsă de generatorul de radar charts."""


def _safe_filename(value: object) -> str:
    """Transformă un text într-un nume de fișier sigur și predictibil."""

    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", ascii_value)
    cleaned = cleaned.strip("_").lower()

    return cleaned or "unknown_player"


def _load_methodology(rankings_file: Path) -> pd.DataFrame:
    """Încarcă metodologia folosită pentru identificarea categoriilor."""

    try:
        methodology = pd.read_excel(
            rankings_file,
            sheet_name="Methodology",
        )
    except ValueError as exc:
        raise RadarChartError(
            "Sheet 'Methodology' was not found in the rankings file."
        ) from exc
    except Exception as exc:
        raise RadarChartError(
            "The methodology sheet could not be read."
        ) from exc

    required_columns = {
        "Position Group",
        "Category",
    }
    missing_columns = sorted(
        required_columns.difference(methodology.columns)
    )

    if missing_columns:
        raise RadarChartError(
            "Methodology sheet is missing required columns: "
            + ", ".join(missing_columns)
        )

    methodology = methodology.copy()
    methodology["Position Group"] = (
        methodology["Position Group"]
        .astype("string")
        .str.strip()
    )
    methodology["Category"] = (
        methodology["Category"]
        .astype("string")
        .str.strip()
    )

    return methodology.dropna(
        subset=["Position Group", "Category"]
    )


def _category_columns_for_position(
    methodology: pd.DataFrame,
    position_group: str,
) -> list[str]:
    """Returnează coloanele de scor în ordinea definită în metodologie."""

    categories = (
        methodology.loc[
            methodology["Position Group"] == position_group,
            "Category",
        ]
        .drop_duplicates()
        .tolist()
    )

    if not categories:
        raise RadarChartError(
            "No scoring categories were found for position group "
            f"'{position_group}'."
        )

    return [f"{category} Score" for category in categories]


def _validate_player_row(
    player_row: pd.Series,
    category_columns: list[str],
) -> None:
    """Validează câmpurile necesare desenării unui radar."""

    required_columns = {
        "Player",
        "Team",
        "Position Group",
        "Age",
        "Matches played",
        "Performance Score",
        "Recruitment Score",
        *category_columns,
    }

    missing_columns = sorted(
        required_columns.difference(player_row.index)
    )

    if missing_columns:
        raise RadarChartError(
            "Player data is missing required columns: "
            + ", ".join(missing_columns)
        )


def _numeric_score(value: object, label: str) -> float:
    """Convertește un scor la float și îl limitează la intervalul 0-100."""

    numeric = pd.to_numeric(
        pd.Series([value]),
        errors="coerce",
    ).iloc[0]

    if pd.isna(numeric):
        raise RadarChartError(
            f"Invalid numeric score for '{label}'."
        )

    return float(np.clip(float(numeric), 0.0, 100.0))


def create_player_radar(
    player_row: pd.Series,
    category_columns: list[str],
    output_folder: Path,
    competition_name: str | None = None,
) -> dict[str, Path]:
    """
    Creează radarul unui singur jucător și salvează PNG + JSON.

    Parameters
    ----------
    player_row:
        Rândul jucătorului din foaia poziției sau din "All Ranked".
    category_columns:
        Coloanele de tip "<Category> Score" folosite pe axe.
    output_folder:
        Directorul în care se salvează rezultatele.
    competition_name:
        Denumire opțională afișată în subtitlu.
    """

    _validate_player_row(player_row, category_columns)

    labels = [
        column.removesuffix(" Score")
        for column in category_columns
    ]
    values = [
        _numeric_score(player_row[column], column)
        for column in category_columns
    ]

    if len(labels) < 3:
        raise RadarChartError(
            "A radar chart requires at least three scoring categories."
        )

    player_name = str(player_row["Player"]).strip()
    team = str(player_row["Team"]).strip()
    position_group = str(player_row["Position Group"]).strip()
    age = player_row["Age"]
    matches = player_row["Matches played"]
    performance_score = _numeric_score(
        player_row["Performance Score"],
        "Performance Score",
    )
    recruitment_score = _numeric_score(
        player_row["Recruitment Score"],
        "Recruitment Score",
    )

    angles = np.linspace(
        0,
        2 * math.pi,
        len(labels),
        endpoint=False,
    ).tolist()
    closed_angles = angles + angles[:1]
    closed_values = values + values[:1]

    figure = plt.figure(
        figsize=(8, 8),
        dpi=ScoutingTheme.DPI,
        facecolor=ScoutingTheme.BACKGROUND,
    )
    axis = figure.add_subplot(111, polar=True)
    axis.set_facecolor(ScoutingTheme.BACKGROUND)
    axis.set_theta_offset(math.pi / 2)
    axis.set_theta_direction(-1)

    axis.plot(
        closed_angles,
        closed_values,
        color=ScoutingTheme.SECONDARY,
        linewidth=2.4,
    )
    axis.fill(
        closed_angles,
        closed_values,
        color=ScoutingTheme.SECONDARY,
        alpha=0.18,
    )
    axis.scatter(
        angles,
        values,
        color=ScoutingTheme.SECONDARY,
        s=38,
        zorder=3,
    )

    axis.set_ylim(0, 100)
    axis.set_yticks([20, 40, 60, 80, 100])
    axis.set_yticklabels(
        ["20", "40", "60", "80", "100"],
        fontsize=ScoutingTheme.TICK_SIZE,
        color=ScoutingTheme.TEXT,
    )
    axis.set_rlabel_position(0)
    axis.set_xticks(angles)
    axis.set_xticklabels(
        labels,
        fontsize=ScoutingTheme.LABEL_SIZE,
        color=ScoutingTheme.TEXT,
        fontweight="semibold",
    )
    axis.grid(
        color=ScoutingTheme.GRID,
        linewidth=0.8,
        linestyle="--",
    )
    axis.spines["polar"].set_color(ScoutingTheme.GRID)

    figure.suptitle(
        player_name,
        fontsize=ScoutingTheme.TITLE_SIZE + 2,
        color=ScoutingTheme.PRIMARY,
        fontweight="bold",
        y=0.98,
    )

    context_parts = [
        team,
        position_group,
        f"Age {age}",
        f"{matches} matches",
    ]
    if competition_name:
        context_parts.insert(0, competition_name)

    figure.text(
        0.5,
        0.925,
        "  |  ".join(context_parts),
        ha="center",
        va="center",
        fontsize=ScoutingTheme.SUBTITLE_SIZE - 2,
        color=ScoutingTheme.TEXT,
    )

    figure.text(
        0.5,
        0.055,
        (
            f"Performance Score: {performance_score:.1f}   |   "
            f"Recruitment Score: {recruitment_score:.1f}"
        ),
        ha="center",
        va="center",
        fontsize=ScoutingTheme.SUBTITLE_SIZE - 1,
        color=ScoutingTheme.PRIMARY,
        fontweight="bold",
    )

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    filename_stem = (
        f"{_safe_filename(position_group)}__"
        f"{_safe_filename(player_name)}"
    )
    png_path = output_folder / f"{filename_stem}.png"
    json_path = output_folder / f"{filename_stem}.json"

    figure.subplots_adjust(
        top=0.86,
        bottom=0.12,
        left=0.12,
        right=0.88,
    )
    figure.savefig(
        png_path,
        dpi=ScoutingTheme.DPI,
        bbox_inches="tight",
        facecolor=ScoutingTheme.BACKGROUND,
    )
    plt.close(figure)

    metadata: dict[str, Any] = {
        "chart_type": "player_radar",
        "player": player_name,
        "team": team,
        "position_group": position_group,
        "age": age.item() if hasattr(age, "item") else age,
        "matches_played": (
            matches.item() if hasattr(matches, "item") else matches
        ),
        "competition": competition_name,
        "performance_score": round(performance_score, 1),
        "recruitment_score": round(recruitment_score, 1),
        "categories": [
            {
                "name": label,
                "score": round(value, 2),
            }
            for label, value in zip(labels, values)
        ],
    }

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return {
        "png": png_path,
        "json": json_path,
    }


def create_top_player_radars(
    rankings_file: Path,
    output_folder: Path,
    competition_name: str | None = None,
) -> list[dict[str, Path]]:
    """
    Creează câte un radar pentru jucătorul clasat pe locul 1 la fiecare post.
    """

    rankings_file = Path(rankings_file)

    if not rankings_file.exists():
        raise RadarChartError(
            f"Rankings file does not exist: {rankings_file}"
        )

    methodology = _load_methodology(rankings_file)

    try:
        all_ranked = pd.read_excel(
            rankings_file,
            sheet_name="All Ranked",
        )
    except ValueError as exc:
        raise RadarChartError(
            "Sheet 'All Ranked' was not found in the rankings file."
        ) from exc
    except Exception as exc:
        raise RadarChartError(
            "The ranked players sheet could not be read."
        ) from exc

    required_columns = {
        "Player",
        "Position Group",
        "Rank",
    }
    missing_columns = sorted(
        required_columns.difference(all_ranked.columns)
    )

    if missing_columns:
        raise RadarChartError(
            "All Ranked sheet is missing required columns: "
            + ", ".join(missing_columns)
        )

    all_ranked = all_ranked.copy()
    all_ranked["Position Group"] = (
        all_ranked["Position Group"]
        .astype("string")
        .str.strip()
    )
    all_ranked["Rank"] = pd.to_numeric(
        all_ranked["Rank"],
        errors="coerce",
    )

    top_players = (
        all_ranked.dropna(
            subset=["Player", "Position Group", "Rank"]
        )
        .sort_values(
            by=["Position Group", "Rank"],
            ascending=[True, True],
        )
        .groupby(
            "Position Group",
            sort=False,
            as_index=False,
        )
        .head(1)
    )

    if top_players.empty:
        raise RadarChartError(
            "No top-ranked players were available for radar generation."
        )

    generated_files: list[dict[str, Path]] = []

    for _, player_row in top_players.iterrows():
        position_group = str(player_row["Position Group"])
        category_columns = _category_columns_for_position(
            methodology=methodology,
            position_group=position_group,
        )

        generated_files.append(
            create_player_radar(
                player_row=player_row,
                category_columns=category_columns,
                output_folder=output_folder,
                competition_name=competition_name,
            )
        )

    return generated_files
