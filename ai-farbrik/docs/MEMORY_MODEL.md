# AI Fabrik — Memory Model

## 5-Type Cognitive Taxonomy

| Type | Stores | Decay | Confidence |
|------|--------|-------|-----------|
| EPISODIC | Past events, delivery runs, incidents | Hours-Days | 0.2-0.7 |
| SEMANTIC | Abstracted facts, rules, policies | Weeks-Months | 0.5-1.0 |
| PROCEDURAL | Skills, workflows, decision patterns | Months | 0.7-1.0 |
| GRAPH | Entity relationships, causalities | Permanent | 1.0 |
| PARAMETRIC | Model weights, embeddings | Permanent | Model-dependent |

## Lifecycle

```
EPISODIC (raw events)
    │
    ▼ (3+ occurrences detected)
SEMANTIC (abstracted patterns)
    │
    ▼ (2+ related facts grouped)
PROCEDURAL (actionable workflows)
    │
    ▼ (entity relationships mapped)
GRAPH (knowledge representation)
```

## Confidence Scaling

| Level | Value | Condition |
|-------|-------|-----------|
| UNVERIFIED | 0.2 | New, not yet confirmed |
| OBSERVED_ONCE | 0.4 | Single observation |
| OBSERVED_MULTIPLE | 0.7 | Multiple confirmations |
| CORROBORATED | 0.9 | Cross-source verification |
| CANONICAL | 1.0 | Official documentation |

## Effective Confidence

```
effective = confidence × decay^(age_days) + corroboration_bonus - contradiction_penalty
```

## Retrieval Scoring

```
score = semantic(0.35) + causal(0.25) + confidence(0.15) + recency(0.15) + access_count(0.10)
```
