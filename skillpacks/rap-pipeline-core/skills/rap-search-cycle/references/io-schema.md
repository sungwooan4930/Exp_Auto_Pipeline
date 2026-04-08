# RAP Search Cycle JSON 스키마

## search_cycle_input.json

```json
{
  "iteration": 1,
  "request": {
    "domain": "string",
    "keywords": ["string"],
    "experiment_type": "string",
    "research_goals": ["string"],
    "constraints": ["string"]
  },
  "previous_feedback": [],
  "previous_output_ref": null
}
```

## search_feedback.json

```json
{
  "iteration": 1,
  "feedback_items": [
    {
      "type": "expand|narrow|replace|prioritize",
      "target": "queries|papers|topic",
      "comment": "string"
    }
  ],
  "approval_status": "pending|approved|revise"
}
```

## search_cycle_output.json

```json
{
  "iteration": 1,
  "search_strategy": {
    "facets": ["string"],
    "notes": "string"
  },
  "queries": ["string"],
  "candidate_papers": [
    {
      "paper_id": "string",
      "title": "string",
      "abstract": "string",
      "authors": ["string"],
      "year": 2026,
      "source": "string",
      "reason_for_inclusion": "string"
    }
  ],
  "researcher_feedback": [],
  "approval_status": "pending|approved|revise"
}
```
