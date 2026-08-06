from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class EvidenceResult:
    """
    Immutable result produced by an Evidence Component.
    """

    name: str
    score: float
    explanation: str
    metadata: Dict[str, float] = field(default_factory=dict)
