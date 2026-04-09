# RAP Simulation Prediction JSON Schema

## simulation_input.json

```json
{
  "project_profile_ref": "RAP_PROJECT_PROFILE.json",
  "experiment_design_output_ref": "experiment_design_output.json",
  "simulation_goal": "string",
  "data_mode": "real|synthetic",
  "data_sources": [
    {
      "name": "string",
      "type": "dataset|user_input|mock",
      "description": "string",
      "availability": "available|to_be_created"
    }
  ],
  "simulation_constraints": ["string"],
  "success_criteria": ["string"],
  "status": "draft|ready",
  "notes": "string"
}
```

## simulation_output.json

```json
{
  "simulation_id": "sim_001",
  "experiment_design_output_ref": "experiment_design_output.json",
  "data_mode": "real|synthetic",
  "simulation_setup": {
    "steps": ["string"],
    "assumptions": ["string"]
  },
  "predicted_results": [
    {
      "metric": "string",
      "expected_value": "string",
      "interpretation": "string"
    }
  ],
  "validation_result": "pass|fail|uncertain",
  "failure_analysis": ["string"],
  "recommended_backtrack_stage": "gap_hypothesis|experiment_design|none",
  "next_actions": ["string"]
}
```
