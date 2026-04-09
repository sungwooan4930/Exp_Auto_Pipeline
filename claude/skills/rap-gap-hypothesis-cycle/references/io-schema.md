# RAP Gap Hypothesis Cycle JSON Schema

## gap_hypothesis_input.json

```json
{
  "iteration": 1,
  "project_profile_ref": "RAP_PROJECT_PROFILE.json",
  "approved_search_output_ref": "search_cycle_output.json",
  "approved_papers": [
    {
      "paper_id": "string",
      "title": "string",
      "abstract": "string",
      "source": "string",
      "year": 2026,
      "reason_for_inclusion": "string"
    }
  ],
  "analysis_focus": ["string"],
  "previous_feedback": [],
  "previous_output_ref": null,
  "status": "draft|ready",
  "notes": "string"
}
```

## gap_hypothesis_feedback.json

```json
{
  "iteration": 1,
  "feedback_items": [
    {
      "type": "refine|remove|expand|merge|prioritize",
      "target": "gap|hypothesis|evidence|set",
      "target_id": "string",
      "comment": "string",
      "priority": "high|medium|low"
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
      "gap_type": "methodological|empirical|theoretical",
      "gap": "string",
      "significance": "string",
      "evidence_papers": ["paper_id"],
      "open_questions": ["string"]
    }
  ],
  "hypotheses": [
    {
      "hypothesis_id": "h_001",
      "linked_gap_id": "gap_001",
      "hypothesis": "string",
      "rationale": "string",
      "independent_var": "string",
      "dependent_var": "string",
      "control_variables": ["string"],
      "expected_relation": "string",
      "novelty_score": 0.0,
      "testability_notes": ["string"]
    }
  ],
  "researcher_feedback": [],
  "approval_status": "pending|approved|revise"
}
```
