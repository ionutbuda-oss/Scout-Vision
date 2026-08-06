"""
ScoutVision V3
Cross-League Validation Models
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MetricStabilityResult:
    metric: str
    league_a_mean: float
    league_b_mean: float
    absolute_difference: float
    relative_difference: float


@dataclass(frozen=True)
class CrossLeagueResult:
    league_a: str
    league_b: str
    players_a: int
    players_b: int
    metric_stability: Dict[str, MetricStabilityResult]
