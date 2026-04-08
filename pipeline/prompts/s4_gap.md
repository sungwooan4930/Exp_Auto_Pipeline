## System
You analyze screened literature to identify concrete research gaps grounded in the evidence.

## Prompt
Analyze the following screened papers and identify at least {min_gaps} research gaps that remain insufficiently addressed.

Papers:
{papers_text}

[Gap Types]
- Methodological Gap: missing or weak methods, designs, or evaluation strategies
- Empirical Gap: insufficient validation on datasets, populations, settings, or conditions
- Theoretical Gap: weak explanatory framing, unclear mechanisms, or missing conceptual integration

Output ONLY a JSON array:
[
  {{
    "gap_id": "gap_001",
    "gap_type": "Methodological / Empirical / Theoretical",
    "gap": "Concrete description of the gap",
    "evidence_papers": ["paper_id1", "paper_id2"]
  }}
]
