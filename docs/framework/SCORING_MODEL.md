# ScoutVision Scoring Model v1.0

## Philosophy

ScoutVision evaluates football players through a transparent, deterministic and explainable methodology.

Every conclusion must be traceable to measurable Wyscout KPIs.

---

# Layer 1 — Raw KPIs

Input data consists of standardized Wyscout metrics.

No calculations are performed at this stage.

---

# Layer 2 — KPI Standardization

Every KPI is standardized only against players from:

• the same competition
• the same position group

The output is a standardized KPI score (0–100).

This prevents unfair comparisons across positions or competitions.

---

# Layer 3 — Competency Scores

Each competency is calculated from standardized KPIs.

Examples:

Distribution

Progression

Creativity

Ball Carrying

Defending

Offensive Duels

Goal Threat

Chance Creation

Each competency is expressed on a 0–100 scale.

---

# Layer 4 — Position Model

Each position is evaluated only through its predefined competency model.

Irrelevant competencies are ignored.

Examples:

CB

Distribution
Progression
Defending
Ball Winning

AM

Creativity
Progression
Ball Carrying
Goal Threat

---

# Layer 5 — Player DNA

Player DNA is determined using weighted competency profiles.

The profile with the highest score is selected.

DNA is generated only from competencies.

Never directly from KPIs.

---

# Layer 6 — Development Engine

Development priorities are identified from the weakest relevant competencies.

Only competencies defined inside the Position Model are evaluated.

---

# Layer 7 — Intelligence Layer

ScoutVision Intelligence modules include:

• Executive Summary

• Recruitment Verdict

• Club Fit

• Similar Player

These modules consume competencies and DNA only.

They never read raw KPIs.

---

# Validation Principles

Every ScoutVision score must be:

✓ Deterministic

✓ Explainable

✓ Traceable

✓ Position-specific

✓ Competition-specific

