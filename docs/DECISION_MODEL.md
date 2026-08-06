# ScoutVision Core
## Decision Model Specification
Version: 1.0

---

# Philosophy

ScoutVision does not classify players.

ScoutVision produces a Decision Model.

Every decision made by the engine must be:

- Deterministic
- Explainable
- Traceable
- Reproducible
- Position-agnostic

---

# Decision Model

Every player evaluation returns a single Decision Object.

```python
DecisionModel

{

    primary_identity,

    alternative_identity,

    identity_confidence,

    versatility,

    development_area,

    decision_trace

}
mkdir -p engine/intelligence/v3/models
touch engine/intelligence/v3/models/__init__.py
touch engine/intelligence/v3/models/player_intelligence_model.py
cat > engine/intelligence/v3/models/player_intelligence_model.py << 'EOF'
"""
ScoutVision Core

Player Intelligence Model (PIM)

The official output contract of the ScoutVision Core.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerIntelligenceModel:

    primary_identity: dict

    alternative_identity: Optional[dict]

    identity_confidence: dict

    versatility: dict

    development_area: dict

    explanation: dict

    trace: list
