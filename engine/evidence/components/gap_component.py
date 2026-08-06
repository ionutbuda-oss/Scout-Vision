from typing import List

from engine.core.models.identity_score import IdentityScore
from engine.evidence.models.evidence_result import EvidenceResult


class GapComponent:
    """
    Produces evidence based on the separation between the
    highest-ranked and second-ranked identities.
    """

    def evaluate(
        self,
        ranking: List[IdentityScore],
    ) -> EvidenceResult:

        if len(ranking) < 2:
            raise ValueError(
                "GapComponent requires at least two identity scores."
            )

        gap = ranking[0].score - ranking[1].score

        return EvidenceResult(
            name="Gap",
            score=gap,
            explanation=(
                f"The best identity exceeds the second-ranked identity "
                f"by {gap:.1f} points."
            ),
        )
