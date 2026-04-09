# RAP Experiment Design JSON Schema

## experiment_design_input.json

```json
{
  "project_profile_ref": "RAP_PROJECT_PROFILE.json",
  "gap_hypothesis_output_ref": "gap_hypothesis_output.json",
  "selected_hypotheses": [
    {
      "hypothesis_id": "h_001",
      "hypothesis": "string",
      "independent_var": "string",
      "dependent_var": "string"
    }
  ],
  "design_goals": ["string"],
  "constraints": ["string"],
  "status": "draft|ready",
  "notes": "string"
}
```

## experiment_design_output.json

```json
{
  "design_id": "exp_design_001",
  "selected_hypotheses": ["h_001"],
  "variables": {
    "independent": ["string"],
    "dependent": ["string"],
    "control": ["string"]
  },
  "dataset_plan": {
    "sources": ["string"],
    "sampling_strategy": "string"
  },
  "procedure": ["string"],
  "evaluation_metrics": [
    {
      "name": "string",
      "definition": "string"
    }
  ],
  "statistical_tests": [
    {
      "name": "string",
      "purpose": "string"
    }
  ],
  "expected_outcomes": ["string"],
  "risks_and_limitations": ["string"],
  "artifact_plan": ["string"],
  "status": "draft|completed"
}
```
