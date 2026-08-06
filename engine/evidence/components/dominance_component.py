from typing import List

from engine.core.models.identity_score import IdentityScore
from engine.evidence.models.evidence_result import EvidenceResult


class DominanceComponent:
    """
    Produces evidence describing how dominant the best identity
    is compared to the remaining identities.
    """

    def evaluate(
        self,
        ranking: List[IdentityScore],
    ) -> EvidenceResult:

        if len(ranking) < 2:
            raise ValueError(
                "DominanceComponent requires at least two identity scores."
            )

        winner = ranking[0]

        remaining_scores = [
            identity.score
            for identity in ranking[1:]
        ]

        average = sum(remaining_scores) / len(remaining_scores)

        dominance = winner.score - average

        return EvidenceResult(
            name="Dominance",
            score=dominance,
            explanation=(
                f"The best identity exceeds the average of the remaining "
                f"identities by {dominance:.1f} points."
            ),
        )
