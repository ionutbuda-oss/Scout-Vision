
"""
Reusable layout helpers for ScoutVision visualizations.

Version: 1.1
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch


@dataclass(frozen=True)
class Box:
    """Normalized figure coordinates."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y + self.height

    def inset(self, horizontal: float, vertical: float | None = None) -> "Box":
        vertical = horizontal if vertical is None else vertical
        return Box(
            self.x + horizontal,
            self.y + vertical,
            self.width - 2 * horizontal,
            self.height - 2 * vertical,
        )


def draw_rounded_panel(
    axis: plt.Axes,
    box: Box,
    *,
    facecolor: str,
    edgecolor: str,
    linewidth: float = 1.0,
    radius: float = 0.02,
) -> None:
    """Draw one rounded panel inside normalized figure coordinates."""

    axis.add_patch(
        FancyBboxPatch(
            (box.x, box.y),
            box.width,
            box.height,
            boxstyle=f"round,pad=0.008,rounding_size={radius}",
            linewidth=linewidth,
            edgecolor=edgecolor,
            facecolor=facecolor,
            transform=axis.transAxes,
            clip_on=False,
        )
    )


def wrap_label(
    text: str,
    *,
    width: int = 14,
    max_lines: int = 2,
) -> str:
    """Wrap text without breaking words."""

    wrapped = textwrap.wrap(
        str(text),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(wrapped[:max_lines])


def text_width_pixels(
    figure: plt.Figure,
    text: str,
    *,
    fontsize: float,
    fontweight: str = "normal",
) -> float:
    """Measure text width using the active Matplotlib renderer."""

    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    properties = FontProperties(size=fontsize, weight=fontweight)
    width, _, _ = renderer.get_text_width_height_descent(
        text,
        properties,
        ismath=False,
    )
    return float(width)


def fit_font_size(
    figure: plt.Figure,
    text: str,
    *,
    max_width_pixels: float,
    start_size: float,
    minimum_size: float = 7.0,
    fontweight: str = "bold",
) -> float:
    """Reduce font size until the text fits the available width."""

    size = float(start_size)

    while size > minimum_size:
        width = text_width_pixels(
            figure,
            text,
            fontsize=size,
            fontweight=fontweight,
        )
        if width <= max_width_pixels:
            return size
        size -= 0.5

    return minimum_size


def truncate_text(text: str, *, max_characters: int) -> str:
    """Shorten text safely for compact UI regions."""

    clean = str(text).strip()
    if len(clean) <= max_characters:
        return clean
    return clean[: max_characters - 1].rstrip() + "…"
