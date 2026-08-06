"""
ScoutVision Core
Identity Score Model

Represents the evaluation of one identity.
"""

from dataclasses import dataclass

from engine.core.models.identity_definition import IdentityDefinition


@dataclass(frozen=True)
class IdentityScore:

    definition: IdentityDefinition

    score: float
