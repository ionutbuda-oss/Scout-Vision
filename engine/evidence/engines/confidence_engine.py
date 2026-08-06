from engine.core.models.confidence_result import ConfidenceResult

from engine.evidence.components.gap_component import GapComponent
from engine.evidence.components.dominance_component import DominanceComponent
from engine.evidence.components.distribution_component import DistributionComponent


class ConfidenceEngine:
    """
    Produces identity confidence from independent evidence.

    Alpha 0.2 model:
    - Gap is the primary signal.
    - Dominance is supporting evidence.
    - Distribution remains descriptive evidence.
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

        # Normalize the observed evidence ranges to a 0–100 scale.
        gap_score = min(
            100.0,
            max(0.0, gap.score * 6.0),
        )

        dominance_score = min(
            100.0,
            max(0.0, dominance.score * 3.3),
        )

        # Gap is the decisive signal; dominance only confirms it.
        score = (
            gap_score * 0.80
            + dominance_score * 0.20
        )

        # A small winner–runner-up gap limits confidence,
        # regardless of the overall score distribution.
        if gap.score < 2:
            confidence_cap = 40.0
        elif gap.score < 5:
            confidence_cap = 60.0
        elif gap.score < 10:
            confidence_cap = 80.0
        else:
            confidence_cap = 100.0

        score = min(
            score,
            confidence_cap,
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
