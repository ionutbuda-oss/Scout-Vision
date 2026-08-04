# ScoutVision Scoring Methodology v1.0

**Status:** Locked model  
**Data source:** Wyscout  
**Scope:** Outfield players, position-specific comparison pools

## 1. Purpose

ScoutVision converts real Wyscout event indicators into transparent position-specific competency scores, a balanced Season Performance score and a weighted Scout Score used for ranking and recruitment support.

Every displayed score is traceable through this chain:

`Raw KPI → League Percentile → Competency Score → Season Performance / Scout Score`

## 2. Comparison pool

League Percentiles are calculated only among eligible players who:

- belong to the same ScoutVision position group;
- play in the same analysed competition and season;
- satisfy the configured age and minimum-sample filters;
- are outfield players.

A League Percentile of 83 means that the player's value is at or above approximately 83% of the eligible players in that position group. Percentiles describe relative standing, not the magnitude of the raw difference between players.

### Percentile calculation

For each KPI, ScoutVision applies an average-rank percentile:

`League Percentile = percentile rank of the raw KPI within the position group × 100`

Tied values receive the average rank. When a comparison pool contains one or fewer valid values, the neutral value 50 is assigned.

## 3. Competency Score

Each competency combines the League Percentiles of the KPIs defined in `ROLE_MODELS`.

`Competency Score = Σ(League Percentile_i × KPI Weight_i)`

The KPI weights inside every competency total 100%. The resulting score ranges from 0 to 100.

### Example: AM Progression

- Progressive passes per 90: 35%
- Accurate progressive passes: 30%
- Passes to final third per 90: 20%
- Accurate final-third passes: 15%

If the respective League Percentiles are 83, 100, 83 and 83:

`Progression = 83×0.35 + 100×0.30 + 83×0.20 + 83×0.15 = 88.1`

After display rounding, the competency is shown as 88.

## 4. Season Performance

Season Performance is the unweighted arithmetic mean of all competency scores in the player's position model.

`Season Performance = Σ(Competency Scores) / Number of Competencies`

It answers:

> How balanced was the player's statistical performance across all position-specific competencies?

Example for an attacking midfielder:

`(Creativity 72.5 + Ball Carrying 74.2 + Progression 88.3 + Goal Threat 59.6) / 4 = 73.65`

Displayed Season Performance: 73.7 (subject to the full-precision values used by the engine).

## 5. Scout Score

Scout Score is the weighted mean of the competency scores using the competency weights of the position model.

`Scout Score = Σ(Competency Score_j × Competency Weight_j)`

It answers:

> How strongly does the player's statistical profile fit the ScoutVision model for this position?

Example AM model:

- Creativity: 35%
- Ball Carrying: 25%
- Progression: 20%
- Goal Threat: 20%

`Scout Score = Creativity×0.35 + Ball Carrying×0.25 + Progression×0.20 + Goal Threat×0.20`

Scout Score is the principal ranking score.

## 6. Recruitment Score compatibility alias

For backward compatibility with existing files and visualisation modules:

`Recruitment Score = Scout Score`

The two columns must always be numerically identical in v1.0. Future code should prefer the name **Scout Score**.

## 7. Contextual indicators

### Age Potential Score

Age Potential remains a separate descriptive indicator. It does not alter Scout Score.

### Sample Confidence

Sample Confidence remains a separate indicator based on the available match sample. It does not alter Scout Score.

Current match-based calculation:

`Sample Confidence = min(100, Matches played / 25 × 100)`

Interpretation:

- High: 75–100
- Medium: 50–74.9
- Low: below 50

This indicator reflects sample quantity, not certainty about future performance.

## 8. Recommendation labels

Recommendations are derived exclusively from Scout Score:

- 85–100: A+ | Priority Target
- 78–84.9: A | Strong Target
- 70–77.9: B+ | Shortlist
- 62–69.9: B | Monitor
- Below 62: C | Secondary Option

## 9. Position models

The definitive competency names, competency weights, KPI names and KPI weights are stored in:

`engine/scoring/profile_models.py`

That file is the single source of truth for calculations, cards, reports and methodology exports.

## 10. Model transparency

Any Scout Score can be reproduced by:

1. reading the player's raw Wyscout KPI values;
2. calculating each KPI's League Percentile in the eligible position group;
3. applying the KPI weights to obtain competency scores;
4. taking the simple mean for Season Performance;
5. applying competency weights for Scout Score.

## 11. Limitations

- Results are relative to the analysed competition, season and eligible comparison pool.
- Percentiles do not measure the absolute size of differences between players.
- Team style, tactical role and possession context can influence event volumes.
- Small samples can make per-90 values unstable.
- Event data does not fully capture positioning, decision quality or tactical discipline.
- Scout Score is a decision-support indicator, not a prediction of transfer success or future performance.
- Video scouting, tactical analysis, medical information and contextual judgement remain necessary.

## 12. Version governance

ScoutVision Scoring Methodology v1.0 is locked. Formula or weight changes require a new documented version (v1.1, v2.0, etc.). Design changes and new competition databases do not change the methodology version unless they alter calculations.
