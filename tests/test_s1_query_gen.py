import json
import pytest
from unittest.mock import MagicMock
from pipeline.stages.s1_query_gen import generate_queries
from pipeline.config import Config


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.complete.return_value = json.dumps([
        "LLM autonomous agent planning",
        "large language model task decomposition",
        "LLM tool use agent benchmark",
        "autonomous agent reasoning evaluation",
        "chain-of-thought planning LLM",
        "LLM agent memory retrieval"
    ])
    return llm


def test_generate_queries_returns_dict_with_domain_and_queries(mock_llm):
    config = Config()
    result = generate_queries("LLM-based autonomous agents", mock_llm, config)
    assert result["domain"] == "LLM-based autonomous agents"
    assert "queries" in result
    assert isinstance(result["queries"], list)


def test_generate_queries_returns_5_to_10_queries(mock_llm):
    config = Config()
    result = generate_queries("LLM-based autonomous agents", mock_llm, config)
    assert 5 <= len(result["queries"]) <= 10


def test_generate_queries_each_query_is_string(mock_llm):
    config = Config()
    result = generate_queries("LLM-based autonomous agents", mock_llm, config)
    for q in result["queries"]:
        assert isinstance(q, str)
        assert len(q) > 0


def test_generate_queries_calls_llm_with_domain(mock_llm):
    config = Config()
    generate_queries("test domain", mock_llm, config)
    call_args = mock_llm.complete.call_args[0][0]
    assert "test domain" in call_args


def test_generate_queries_accepts_structured_request(mock_llm):
    config = Config()
    request = {
        "request": {
            "domain": "rapid fNIRS decoding",
            "keywords": ["fNIRS decoding", "real-time fNIRS"],
            "experiment_type": "classification",
            "research_goals": ["find low-latency decoding studies"],
            "constraints": ["prefer papers after 2020"],
            "preferred_sources": ["semantic_scholar", "arxiv"],
            "year_range": {"start": 2020, "end": 2026},
            "exclusion_rules": ["exclude non-decoding studies"],
        },
        "quality_criteria": {
            "must_cover": ["rapid and real-time variants"],
            "must_avoid": ["title-only judgments"],
            "selection_principles": ["explicit inclusion reasons"],
        },
    }

    result = generate_queries(request, mock_llm, config)

    assert result["domain"] == "rapid fNIRS decoding"
    assert result["request"]["keywords"] == ["fNIRS decoding", "real-time fNIRS"]
    call_args = mock_llm.complete.call_args[0][0]
    assert "real-time fNIRS" in call_args
    assert "rapid and real-time variants" in call_args
