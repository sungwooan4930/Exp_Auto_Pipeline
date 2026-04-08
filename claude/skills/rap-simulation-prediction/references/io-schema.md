# RAP Simulation Prediction JSON 스키마

## simulation_input.json

```json
{
  "experiment_design_output_ref": "experiment_design_output.json",
  "data_mode": "real|synthetic",
  "data_sources": [
    {
      "name": "string",
      "type": "dataset|user_input|mock",
      "description": "string"
    }
  ],
  "simulation_constraints": ["string"]
}
```

## simulation_output.json

```json
{
  "simulation_id": "sim_001",
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
  "recommended_backtrack_stage": "gap_hypothesis|experiment_design|none"
}
```
