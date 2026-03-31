## System
You are a research hypothesis generator. Output ONLY valid JSON arrays, no explanation.

## Prompt
Based on the following research gaps and supporting papers, generate structured research hypotheses.

Research Gaps:
{gaps_text}

Supporting Paper Abstracts:
{papers_text}

Generate at least {min_hypotheses} hypotheses. For each:
- State the hypothesis clearly (if X then Y format)
- Identify the independent variable (what you manipulate)
- Identify the dependent variable (what you measure)
- State expected relationship direction
- Estimate novelty score (0.0–1.0) vs existing literature

Output ONLY a JSON array (no markdown):
[
  {{
    "hypothesis_id": "h_001",
    "hypothesis": "...",
    "independent_var": "...",
    "dependent_var": "...",
    "expected_relation": "positive correlation" or "negative correlation" or "no effect",
    "novelty_score": 0.0
  }},
  ...
]
