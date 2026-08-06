"""
ScoutVision Core
Identity Definition Model

Represents a football identity definition.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class IdentityDefinition:

    key: str

    title: str

    signature: str

    archetype: str

    description: str

    executive_summary: str

    weights: Dict[str, float]
