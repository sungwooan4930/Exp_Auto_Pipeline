import json
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from pipeline.stages.s4_gap import analyze_gaps
from pipeline.config import Config

FIXTURES = Path("tests/fixtures")


@pytest.fixture
def screened_papers():
    return json.loads((FIXTURES / "sample_screening.json").read_text())


@pytest.fixture
def mock_llm_gaps():
    llm = MagicMock()
    llm.complete.return_value = json.dumps([
        {"gap_id": "gap_001", "gap": "Gap one description.", "evidence_papers": ["ss_001"]},
        {"gap_id": "gap_002", "gap": "Gap two description.", "evidence_papers": ["ss_002"]},
        {"gap_id": "gap_003", "gap": "Gap three description.", "evidence_papers": ["ss_001", "ss_002"]},
    ])
    return llm


def test_analyze_gaps_returns_list(screened_papers, mock_llm_gaps):
    config = Config(min_gaps=3)
    result = analyze_gaps(screened_papers, mock_llm_gaps, config)
    assert isinstance(result, list)


def test_analyze_gaps_returns_min_3(screened_papers, mock_llm_gaps):
    config = Config(min_gaps=3)
    result = analyze_gaps(screened_papers, mock_llm_gaps, config)
    assert len(result) >= 3


def test_analyze_gaps_each_has_required_fields(screened_papers, mock_llm_gaps):
    config = Config(min_gaps=3)
    result = analyze_gaps(screened_papers, mock_llm_gaps, config)
    for gap in result:
        assert "gap_id" in gap
        assert "gap" in gap
        assert isinstance(gap["gap"], str) and len(gap["gap"]) > 0
        assert "evidence_papers" in gap
        assert isinstance(gap["evidence_papers"], list)
        assert len(gap["evidence_papers"]) > 0


def test_analyze_gaps_warns_when_below_minimum(caplog):
    import logging
    screened = [{"paper_id": "p1", "title": "T", "abstract": "A", "decision": "include", "reason": "R"}]
    llm = MagicMock()
    llm.complete.return_value = json.dumps([
        {"gap_id": "gap_001", "gap": "Only one gap.", "evidence_papers": ["p1"]}
    ])
    config = Config(min_gaps=3)
    with caplog.at_level(logging.WARNING):
        result = analyze_gaps(screened, llm, config)
    assert any("gap" in r.message.lower() for r in caplog.records)
