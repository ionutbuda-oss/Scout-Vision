from math import sqrt
from typing import List

from engine.core.models.identity_score import IdentityScore
from engine.evidence.models.evidence_result import EvidenceResult


class DistributionComponent:
    """
    Produces evidence describing how concentrated or dispersed
    the identity scores are.
    """

    def evaluate(
        self,
        ranking: List[IdentityScore],
    ) -> EvidenceResult:

        if len(ranking) < 2:
            raise ValueError(
                "DistributionComponent requires at least two identity scores."
            )

        scores = [
            identity.score
            for identity in ranking
        ]

        mean = sum(scores) / len(scores)

        variance = sum(
            (score - mean) ** 2
            for score in scores
        ) / len(scores)

        distribution = sqrt(variance)

        return EvidenceResult(
            name="Distribution",
            score=distribution,
            explanation=(
                f"The identity score distribution has a standard "
                f"deviation of {distribution:.2f}."
            ),
        )
