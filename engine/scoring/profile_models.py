"""
ScoutVision position-specific competency models.

This module is the single source of truth for:
- position competency definitions;
- KPI weights inside each competency;
- competency weights inside each position model;
- scoring validation;
- methodology exports;
- radar and Player Card category labels.

Methodological principles:
- only metrics available in the Wyscout source database are used;
- cumulative statistics are excluded from scoring;
- per-90 and percentage metrics are preferred;
- quality indicators generally receive greater weight than volume indicators;
- assists per 90 are excluded in favour of xA per 90;
- every weight must be explicit and auditable.

Version: 1.0
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Final, TypedDict


class CategoryConfig(TypedDict):
    """Configuration for one position-specific competency."""

    weight: float
    metrics: dict[str, float]


RoleModel = dict[str, CategoryConfig]


ROLE_MODELS: Final[dict[str, RoleModel]] = {
    "CB": {
        "Defending": {
            "weight": 0.45,
            "metrics": {
                "Defensive duels won, %": 0.45,
                "Interceptions per 90": 0.35,
                "Defensive duels per 90": 0.20,
            },
        },
        "Distribution": {
            "weight": 0.30,
            "metrics": {
                "Accurate passes, %": 0.35,
                "Forward passes per 90": 0.25,
                "Accurate forward passes, %": 0.25,
                "Passes per 90": 0.15,
            },
        },
        "Progression": {
            "weight": 0.25,
            "metrics": {
                "Progressive passes per 90": 0.35,
                "Accurate progressive passes, %": 0.30,
                "Passes to final third per 90": 0.20,
                "Accurate passes to final third, %": 0.15,
            },
        },
    },
    "FB_WB": {
        "Defending": {
            "weight": 0.30,
            "metrics": {
                "Defensive duels won, %": 0.45,
                "Interceptions per 90": 0.35,
                "Defensive duels per 90": 0.20,
            },
        },
        "Progression": {
            "weight": 0.30,
            "metrics": {
                "Progressive passes per 90": 0.35,
                "Accurate progressive passes, %": 0.30,
                "Passes to final third per 90": 0.20,
                "Accurate passes to final third, %": 0.15,
            },
        },
        "Chance Creation": {
            "weight": 0.20,
            "metrics": {
                "xA per 90": 0.35,
                "Accurate crosses, %": 0.25,
                "Crosses per 90": 0.20,
                "Smart passes per 90": 0.20,
            },
        },
        "Ball Carrying": {
            "weight": 0.20,
            "metrics": {
                "Successful dribbles, %": 0.35,
                "Dribbles per 90": 0.25,
                "Offensive duels won, %": 0.25,
                "Offensive duels per 90": 0.15,
            },
        },
    },
    "DM": {
        "Ball Winning": {
            "weight": 0.35,
            "metrics": {
                "Defensive duels won, %": 0.40,
                "Interceptions per 90": 0.35,
                "Defensive duels per 90": 0.25,
            },
        },
        "Distribution": {
            "weight": 0.30,
            "metrics": {
                "Accurate passes, %": 0.35,
                "Forward passes per 90": 0.25,
                "Passes per 90": 0.20,
                "Accurate forward passes, %": 0.20,
            },
        },
        "Progression": {
            "weight": 0.20,
            "metrics": {
                "Progressive passes per 90": 0.40,
                "Accurate progressive passes, %": 0.30,
                "Passes to final third per 90": 0.20,
                "Accurate passes to final third, %": 0.10,
            },
        },
        "Ball Security": {
            "weight": 0.15,
            "metrics": {
                "Accurate passes, %": 0.40,
                "Successful dribbles, %": 0.30,
                "Accurate progressive passes, %": 0.30,
            },
        },
    },
    "CM": {
        "Distribution": {
            "weight": 0.30,
            "metrics": {
                "Accurate passes, %": 0.35,
                "Forward passes per 90": 0.25,
                "Passes per 90": 0.20,
                "Accurate forward passes, %": 0.20,
            },
        },
        "Progression": {
            "weight": 0.30,
            "metrics": {
                "Progressive passes per 90": 0.35,
                "Accurate progressive passes, %": 0.30,
                "Passes to final third per 90": 0.20,
                "Accurate passes to final third, %": 0.15,
            },
        },
        "Creativity": {
            "weight": 0.25,
            "metrics": {
                "xA per 90": 0.30,
                "Smart passes per 90": 0.25,
                "Accurate smart passes, %": 0.20,
                "Through passes per 90": 0.15,
                "Accurate through passes, %": 0.10,
            },
        },
        "Defensive Contribution": {
            "weight": 0.15,
            "metrics": {
                "Defensive duels won, %": 0.45,
                "Interceptions per 90": 0.35,
                "Defensive duels per 90": 0.20,
            },
        },
    },
    "AM": {
        "Creativity": {
            "weight": 0.35,
            "metrics": {
                "xA per 90": 0.35,
                "Smart passes per 90": 0.25,
                "Accurate smart passes, %": 0.20,
                "Through passes per 90": 0.20,
            },
        },
        "Ball Carrying": {
            "weight": 0.25,
            "metrics": {
                "Successful dribbles, %": 0.35,
                "Dribbles per 90": 0.25,
                "Offensive duels won, %": 0.25,
                "Offensive duels per 90": 0.15,
            },
        },
        "Progression": {
            "weight": 0.20,
            "metrics": {
                "Progressive passes per 90": 0.35,
                "Accurate progressive passes, %": 0.30,
                "Passes to final third per 90": 0.20,
                "Accurate passes to final third, %": 0.15,
            },
        },
        "Goal Threat": {
            "weight": 0.20,
            "metrics": {
                "xG per 90": 0.45,
                "Goals per 90": 0.35,
                "Goal conversion, %": 0.20,
            },
        },
    },
    "Winger": {
        "Ball Carrying": {
            "weight": 0.30,
            "metrics": {
                "Successful dribbles, %": 0.35,
                "Dribbles per 90": 0.25,
                "Offensive duels won, %": 0.25,
                "Offensive duels per 90": 0.15,
            },
        },
        "Chance Creation": {
            "weight": 0.25,
            "metrics": {
                "xA per 90": 0.35,
                "Smart passes per 90": 0.25,
                "Accurate smart passes, %": 0.20,
                "Crosses per 90": 0.10,
                "Accurate crosses, %": 0.10,
            },
        },
        "Goal Threat": {
            "weight": 0.25,
            "metrics": {
                "xG per 90": 0.45,
                "Goals per 90": 0.35,
                "Goal conversion, %": 0.20,
            },
        },
        "Combination Play": {
            "weight": 0.20,
            "metrics": {
                "Accurate passes, %": 0.30,
                "Passes per 90": 0.20,
                "Progressive passes per 90": 0.20,
                "Accurate progressive passes, %": 0.20,
                "Through passes per 90": 0.10,
            },
        },
    },
    "ST": {
        "Finishing": {
            "weight": 0.35,
            "metrics": {
                "Goals per 90": 0.40,
                "xG per 90": 0.40,
                "Goal conversion, %": 0.20,
            },
        },
        "Box Threat": {
            "weight": 0.25,
            "metrics": {
                "Touches in box per 90": 0.45,
                "Successful attacking actions per 90": 0.30,
                "Offensive duels per 90": 0.25,
            },
        },
        "Link Play": {
            "weight": 0.20,
            "metrics": {
                "Accurate passes, %": 0.30,
                "Passes per 90": 0.20,
                "Smart passes per 90": 0.20,
                "Accurate smart passes, %": 0.15,
                "xA per 90": 0.15,
            },
        },
        "Offensive Duels": {
            "weight": 0.20,
            "metrics": {
                "Offensive duels won, %": 0.60,
                "Offensive duels per 90": 0.40,
            },
        },
    },
}


def iter_required_metrics(
    role_models: Mapping[str, RoleModel] = ROLE_MODELS,
) -> Iterator[str]:
    """Yield each unique Wyscout metric required by the active models."""

    seen: set[str] = set()

    for model in role_models.values():
        for category in model.values():
            for metric in category["metrics"]:
                if metric not in seen:
                    seen.add(metric)
                    yield metric


def validate_role_models(
    role_models: Mapping[str, RoleModel] = ROLE_MODELS,
    *,
    tolerance: float = 1e-9,
) -> None:
    """Validate all category and KPI weights."""

    if not role_models:
        raise ValueError("ROLE_MODELS cannot be empty.")

    for position_group, model in role_models.items():
        if not model:
            raise ValueError(
                f"Position group '{position_group}' has no competencies."
            )

        category_total = sum(
            float(category["weight"])
            for category in model.values()
        )

        if abs(category_total - 1.0) > tolerance:
            raise ValueError(
                f"Competency weights for '{position_group}' must total 1.0; "
                f"received {category_total:.6f}."
            )

        for category_name, category in model.items():
            metrics = category["metrics"]

            if not metrics:
                raise ValueError(
                    f"Competency '{position_group} / {category_name}' "
                    "has no KPIs."
                )

            metric_total = sum(float(weight) for weight in metrics.values())

            if abs(metric_total - 1.0) > tolerance:
                raise ValueError(
                    f"KPI weights for '{position_group} / {category_name}' "
                    f"must total 1.0; received {metric_total:.6f}."
                )

            invalid_metrics = [
                metric
                for metric, weight in metrics.items()
                if not metric.strip() or float(weight) <= 0
            ]

            if invalid_metrics:
                raise ValueError(
                    f"Invalid KPI configuration in "
                    f"'{position_group} / {category_name}': "
                    f"{invalid_metrics}."
                )


validate_role_models()
