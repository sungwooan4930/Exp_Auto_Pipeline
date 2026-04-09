# RAP Search Cycle JSON Schema

## search_cycle_input.json

```json
{
  "iteration": 1,
  "project_profile_ref": "RAP_PROJECT_PROFILE.json",
  "request": {
    "domain": "string",
    "keywords": ["string"],
    "experiment_type": "string",
    "research_goals": ["string"],
    "constraints": ["string"],
    "preferred_sources": ["semantic_scholar", "arxiv"],
    "year_range": {
      "start": 2022,
      "end": 2026
    },
    "exclusion_rules": ["string"]
  },
  "previous_feedback": [],
  "previous_output_ref": null,
  "status": "draft|ready",
  "notes": "string"
}
```

## search_feedback.json

```json
{
  "iteration": 1,
  "feedback_items": [
    {
      "type": "expand|narrow|replace|prioritize",
      "target": "queries|papers|topic|strategy|constraints|sources",
      "comment": "string",
      "priority": "high|medium|low"
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
    "sources": ["semantic_scholar", "arxiv"],
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
      "doi": "string",
      "url": "string",
      "matched_queries": ["string"],
      "reason_for_inclusion": "string",
      "screening_note": "string"
    }
  ],
  "researcher_feedback": [],
  "approval_status": "pending|approved|revise"
}
```
