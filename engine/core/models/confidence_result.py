"""
ScoutVision Core
Confidence Result Model
"""

from dataclasses import dataclass
from typing import List

from engine.evidence.models.evidence_result import EvidenceResult


@dataclass(frozen=True)
class ConfidenceResult:

    score: float

    level: str

    evidence: List[EvidenceResult]
