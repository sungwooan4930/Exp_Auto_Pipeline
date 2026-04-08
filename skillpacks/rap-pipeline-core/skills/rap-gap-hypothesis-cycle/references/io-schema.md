# RAP Gap Hypothesis Cycle JSON 스키마

## gap_hypothesis_input.json

```json
{
  "iteration": 1,
  "approved_search_output_ref": "search_cycle_output.json",
  "approved_papers": [
    {
      "paper_id": "string",
      "title": "string",
      "abstract": "string"
    }
  ],
  "previous_feedback": [],
  "previous_output_ref": null
}
```

## gap_hypothesis_feedback.json

```json
{
  "iteration": 1,
  "feedback_items": [
    {
      "target": "gap|hypothesis|evidence",
      "target_id": "string",
      "comment": "string"
    }
  ],
  "approval_status": "pending|approved|revise"
}
```

## gap_hypothesis_output.json

```json
{
  "iteration": 1,
  "gaps": [
    {
      "gap_id": "gap_001",
      "gap": "string",
      "evidence_papers": ["paper_id"]
    }
  ],
  "hypotheses": [
    {
      "hypothesis_id": "h_001",
      "linked_gap_id": "gap_001",
      "hypothesis": "string",
      "independent_var": "string",
      "dependent_var": "string",
      "expected_relation": "string"
    }
  ],
  "researcher_feedback": [],
  "approval_status": "pending|approved|revise"
}
```
