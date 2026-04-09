# RAP Metrics Tracking JSON Schema

## weekly_metrics.json

```json
{
  "run_id": "rap_2026_04_08_001",
  "timestamp": "2026-04-08T10:00:00+09:00",
  "overall_status": "in_progress|completed|blocked",
  "active_stage": "search_cycle|gap_hypothesis_cycle|experiment_design|simulation_prediction|metrics",
  "search_cycle": {
    "iterations": 2,
    "approval_status": "approved",
    "candidate_paper_count": 24
  },
  "gap_hypothesis_cycle": {
    "iterations": 2,
    "approval_status": "approved",
    "gap_count": 3,
    "hypothesis_count": 3
  },
  "experiment_design": {
    "design_count": 1,
    "status": "completed"
  },
  "simulation_prediction": {
    "simulation_count": 1,
    "validation_result": "pass",
    "recommended_backtrack_stage": "none"
  },
  "blockers": ["string"],
  "notes": ["string"]
}
```
