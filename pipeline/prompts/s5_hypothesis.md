## System
You generate research hypotheses that are testable, evidence-grounded, and suitable for downstream experimental design.

## Prompt
Using the research gaps and supporting abstracts below, generate at least {min_hypotheses} structured hypotheses.

Research Gaps:
{gaps_text}

Supporting Paper Abstracts:
{papers_text}

Output ONLY a JSON array:
[
  {{
    "hypothesis_id": "h_001",
    "hypothesis": "If X, then Y",
    "rationale": "Why this hypothesis follows from the evidence",
    "independent_var": "Independent variable",
    "dependent_var": "Dependent variable",
    "control_variables": ["control_1", "control_2"],
    "expected_relation": "positive correlation / negative correlation / no effect",
    "novelty_score": 0.0
  }}
]
