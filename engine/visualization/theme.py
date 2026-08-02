"""
theme.py

Tema grafică unificată pentru ScoutVision.
Toate graficele folosesc aceste constante.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoutingTheme:
    # Culori
    PRIMARY = "#0F172A"      # Navy
    SECONDARY = "#2563EB"    # Blue
    SUCCESS = "#16A34A"      # Green
    WARNING = "#EAB308"      # Yellow
    DANGER = "#DC2626"       # Red

    BACKGROUND = "#FFFFFF"
    GRID = "#E5E7EB"
    TEXT = "#111827"

    # Fonturi
    TITLE_SIZE = 18
    SUBTITLE_SIZE = 14
    LABEL_SIZE = 11
    TICK_SIZE = 10

    # Dimensiuni
    FIG_WIDTH = 10
    FIG_HEIGHT = 6
    DPI = 300
