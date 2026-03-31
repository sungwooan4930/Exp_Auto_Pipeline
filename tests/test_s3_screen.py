import json
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from pipeline.stages.s3_screen import screen_papers
from pipeline.config import Config

FIXTURES = Path("tests/fixtures")


@pytest.fixture
def sample_papers():
    return json.loads((FIXTURES / "sample_papers.json").read_text())


def _make_llm(decision="include"):
    llm = MagicMock()
    llm.complete.return_value = json.dumps({
        "decision": decision,
        "reason": "Relevant to the domain."
    })
    return llm


def test_screen_papers_returns_list_of_dicts(sample_papers):
    llm = _make_llm("include")
    config = Config(min_screened=1, max_screened=20)
    result = screen_papers(sample_papers[:2], "LLM agents", llm, config)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_screen_result_has_required_fields(sample_papers):
    llm = _make_llm("include")
    config = Config(min_screened=1, max_screened=20)
    result = screen_papers(sample_papers[:1], "LLM agents", llm, config)
    for r in result:
        assert "paper_id" in r
        assert "title" in r
        assert "abstract" in r
        assert "decision" in r
        assert r["decision"] in ("include", "exclude")
        assert "reason" in r
        assert len(r["reason"]) > 0


def test_screen_papers_filters_excludes():
    papers = [
        {"paper_id": "p1", "title": "A", "abstract": "about NLP"},
        {"paper_id": "p2", "title": "B", "abstract": "about agents"},
    ]
    llm = MagicMock()
    llm.complete.side_effect = [
        json.dumps({"decision": "exclude", "reason": "not relevant"}),
        json.dumps({"decision": "include", "reason": "relevant"}),
    ]
    config = Config(min_screened=1, max_screened=20)
    result = screen_papers(papers, "LLM agents", llm, config)
    included = [r for r in result if r["decision"] == "include"]
    assert len(included) == 1
    assert included[0]["paper_id"] == "p2"


def test_screen_papers_warns_when_below_minimum(caplog):
    import logging
    papers = [{"paper_id": "p1", "title": "A", "abstract": "irrelevant"}]
    llm = MagicMock()
    llm.complete.return_value = json.dumps({"decision": "exclude", "reason": "not relevant"})
    config = Config(min_screened=15, max_screened=20)
    with caplog.at_level(logging.WARNING):
        result = screen_papers(papers, "LLM agents", llm, config)
    assert any("below minimum" in r.message.lower() for r in caplog.records)
