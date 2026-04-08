# RAP Experiment Design JSON 스키마

## experiment_design_input.json

```json
{
  "gap_hypothesis_output_ref": "gap_hypothesis_output.json",
  "selected_hypotheses": [
    {
      "hypothesis_id": "h_001",
      "hypothesis": "string"
    }
  ]
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
  "procedure": ["string"],
  "evaluation_metrics": ["string"],
  "statistical_tests": ["string"],
  "expected_outcomes": ["string"],
  "risks_and_limitations": ["string"]
}
```
