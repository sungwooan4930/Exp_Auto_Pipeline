## System
You are a research gap analyst. Output ONLY valid JSON arrays, no explanation.

## Prompt
Analyze the following screened papers and identify research gaps.

Papers:
{papers_text}

Identify at least {min_gaps} distinct research gaps — areas that existing papers do NOT adequately address.
For each gap, cite which paper IDs support the finding.

Output ONLY a JSON array (no markdown):
[
  {{"gap_id": "gap_001", "gap": "description of gap", "evidence_papers": ["paper_id1", "paper_id2"]}},
  ...
]
