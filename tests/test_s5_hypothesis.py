import json
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from pipeline.stages.s5_hypothesis import generate_hypotheses
from pipeline.config import Config

FIXTURES = Path("tests/fixtures")


@pytest.fixture
def sample_gaps():
    return json.loads((FIXTURES / "sample_gaps.json").read_text())


@pytest.fixture
def sample_screened():
    return json.loads((FIXTURES / "sample_screening.json").read_text())


@pytest.fixture
def mock_llm_hypotheses():
    llm = MagicMock()
    llm.complete.return_value = json.dumps([
        {
            "hypothesis_id": "h_001",
            "hypothesis": "Multimodal context improves planning accuracy.",
            "independent_var": "Multimodal context",
            "dependent_var": "Planning accuracy",
            "expected_relation": "positive correlation",
            "novelty_score": 0.8
        },
        {
            "hypothesis_id": "h_002",
            "hypothesis": "Memory retrieval increases long-horizon task success.",
            "independent_var": "Memory retrieval",
            "dependent_var": "Task success rate",
            "expected_relation": "positive correlation",
            "novelty_score": 0.75
        },
        {
            "hypothesis_id": "h_003",
            "hypothesis": "Adversarial injection reduces task completion.",
            "independent_var": "Adversarial injection",
            "dependent_var": "Task completion rate",
            "expected_relation": "negative correlation",
            "novelty_score": 0.9
        }
    ])
    return llm


def test_generate_hypotheses_returns_list(sample_gaps, sample_screened, mock_llm_hypotheses):
    config = Config(min_hypotheses=3)
    result = generate_hypotheses(sample_gaps, sample_screened, mock_llm_hypotheses, config)
    assert isinstance(result, list)


def test_generate_hypotheses_returns_min_3(sample_gaps, sample_screened, mock_llm_hypotheses):
    config = Config(min_hypotheses=3)
    result = generate_hypotheses(sample_gaps, sample_screened, mock_llm_hypotheses, config)
    assert len(result) >= 3


def test_hypothesis_has_required_fields(sample_gaps, sample_screened, mock_llm_hypotheses):
    config = Config(min_hypotheses=3)
    result = generate_hypotheses(sample_gaps, sample_screened, mock_llm_hypotheses, config)
    for h in result:
        assert "hypothesis_id" in h
        assert "hypothesis" in h
        assert "independent_var" in h
        assert "dependent_var" in h
        assert "expected_relation" in h
        assert "novelty_score" in h


def test_novelty_score_is_between_0_and_1(sample_gaps, sample_screened, mock_llm_hypotheses):
    config = Config(min_hypotheses=3)
    result = generate_hypotheses(sample_gaps, sample_screened, mock_llm_hypotheses, config)
    for h in result:
        assert 0.0 <= h["novelty_score"] <= 1.0
