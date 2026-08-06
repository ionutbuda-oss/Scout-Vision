from engine.core.models.confidence_result import ConfidenceResult

from engine.evidence.components.gap_component import GapComponent
from engine.evidence.components.dominance_component import DominanceComponent
from engine.evidence.components.distribution_component import DistributionComponent


class ConfidenceEngine:
    """
    Produces the overall confidence for an identity ranking.
    """

    def evaluate(
        self,
        ranking,
    ) -> ConfidenceResult:

        gap = GapComponent().evaluate(ranking)

        dominance = DominanceComponent().evaluate(ranking)

        distribution = DistributionComponent().evaluate(ranking)

        evidence = [
            gap,
            dominance,
            distribution,
        ]

        score = (
            gap.score * 0.40
            + dominance.score * 0.35
            + distribution.score * 0.25
        )

        score = max(
            0.0,
            min(
                score,
                100.0,
            ),
        )

        if score >= 90:
            level = "Very High"
        elif score >= 75:
            level = "High"
        elif score >= 55:
            level = "Medium"
        else:
            level = "Low"

        return ConfidenceResult(
            score=round(score, 1),
            level=level,
            evidence=evidence,
        )
