# ADR-002 — Evidence Architecture

Status: Accepted

---

## Context

Decision Intelligence requires multiple independent analyses
to support football decisions.

Examples include:

- Gap Analysis
- Dominance Analysis
- Distribution Analysis
- Consistency Analysis

These analyses should be reusable across multiple intelligence engines.

---

## Decision

ScoutVision introduces an independent Evidence Framework.

Evidence Components are responsible for generating objective football evidence.

Evidence Results transport the generated evidence.

Higher-level intelligence engines consume evidence instead of calculating
everything internally.

---

## Consequences

- High modularity
- High reusability
- Better testing
- Easier maintenance
- Extensible architecture
