import json
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from pipeline.stages.s6_experiment import design_experiment
from pipeline.config import Config

FIXTURES = Path("tests/fixtures")

REQUIRED_SECTIONS = [
    "## 1.",
    "## 2.",
    "## 3.",
    "## 4.",
    "## 5.",
]


@pytest.fixture
def sample_hypotheses():
    return json.loads((FIXTURES / "sample_hypotheses.json").read_text())


@pytest.fixture
def mock_llm_experiment():
    llm = MagicMock()
    llm.complete.return_value = """# Experiment Design

## 1. Research Overview
Testing LLM planning with multimodal context.

## 2. Variables
- Independent: Multimodal context
- Dependent: Planning accuracy

## 3. Methodology
Controlled experiment with GPT-4 baseline.

## 4. Evaluation Metrics
Task completion rate, planning depth.

## 5. Expected Results
Multimodal context improves planning by 15%.
"""
    return llm


def test_design_experiment_returns_string(sample_hypotheses, mock_llm_experiment):
    config = Config()
    result = design_experiment(sample_hypotheses, mock_llm_experiment, config)
    assert isinstance(result, str)
    assert len(result) > 100


def test_design_experiment_contains_required_sections(sample_hypotheses, mock_llm_experiment):
    config = Config()
    result = design_experiment(sample_hypotheses, mock_llm_experiment, config)
    for section in REQUIRED_SECTIONS:
        assert section in result, f"Missing section: {section}"


def test_design_experiment_calls_llm_with_hypotheses(sample_hypotheses, mock_llm_experiment):
    config = Config()
    design_experiment(sample_hypotheses, mock_llm_experiment, config)
    call_args = mock_llm_experiment.complete.call_args[0][0]
    assert "independent_var" in call_args or "hypothesis" in call_args.lower()
