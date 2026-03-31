import json
import asyncio
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from pipeline.config import Config
from run_pipeline import run


FIXTURES = Path("tests/fixtures")


def _make_llm_mock():
    llm = MagicMock()
    llm.complete.side_effect = [
        # S1: query generation
        json.dumps(["query1", "query2", "query3", "query4", "query5"]),
        # S3: screening (called per paper, 3 papers)
        json.dumps({"decision": "include", "reason": "relevant"}),
        json.dumps({"decision": "include", "reason": "relevant"}),
        json.dumps({"decision": "exclude", "reason": "not relevant"}),
        # S4: gap analysis
        json.dumps([
            {"gap_id": "gap_001", "gap": "Gap 1", "evidence_papers": ["p0"]},
            {"gap_id": "gap_002", "gap": "Gap 2", "evidence_papers": ["p1"]},
            {"gap_id": "gap_003", "gap": "Gap 3", "evidence_papers": ["p0", "p1"]},
        ]),
        # S5: hypothesis generation
        json.dumps([
            {"hypothesis_id": "h_001", "hypothesis": "H1", "independent_var": "IV1",
             "dependent_var": "DV1", "expected_relation": "positive correlation", "novelty_score": 0.8},
            {"hypothesis_id": "h_002", "hypothesis": "H2", "independent_var": "IV2",
             "dependent_var": "DV2", "expected_relation": "positive correlation", "novelty_score": 0.7},
            {"hypothesis_id": "h_003", "hypothesis": "H3", "independent_var": "IV3",
             "dependent_var": "DV3", "expected_relation": "negative correlation", "novelty_score": 0.9},
        ]),
        # S6: experiment design
        "# Experiment Design\n## 1. Research Overview\nTest.\n## 2. Variables\nIV/DV.\n## 3. Methodology\nMethod.\n## 4. Evaluation Metrics\nMetrics.\n## 5. Expected Results\nResults.",
    ]
    return llm


@pytest.fixture
def sample_papers():
    return [
        {"paper_id": f"p{i}", "title": f"Paper {i}", "abstract": f"Abstract {i}",
         "authors": ["Author"], "year": 2023, "doi": f"10.1234/{i}", "source": "semantic_scholar"}
        for i in range(3)
    ]


@pytest.mark.asyncio
async def test_full_pipeline_creates_all_artifacts(tmp_path, sample_papers):
    config = Config(output_base=tmp_path, target_papers=3, min_screened=1, min_gaps=3, min_hypotheses=3)
    llm_mock = _make_llm_mock()

    with patch("run_pipeline.get_client", return_value=llm_mock), \
         patch("pipeline.stages.s2_collect.fetch_semantic_scholar", new_callable=AsyncMock) as mock_ss, \
         patch("pipeline.stages.s2_collect.fetch_arxiv", new_callable=AsyncMock) as mock_ax:
        mock_ss.return_value = sample_papers
        mock_ax.return_value = []
        run_dir = await run("LLM agents", config)

    expected_files = [
        "search_queries.json",
        "collected_papers.bib",
        "collected_papers.json",
        "screening_results.json",
        "gap_analysis.json",
        "hypotheses.json",
        "experiment_design.md",
        "weekly_metrics.json",
    ]
    for fname in expected_files:
        assert (run_dir / fname).exists(), f"Missing: {fname}"


@pytest.mark.asyncio
async def test_full_pipeline_metrics_are_correct(tmp_path, sample_papers):
    config = Config(output_base=tmp_path, target_papers=3, min_screened=1, min_gaps=3, min_hypotheses=3)
    llm_mock = _make_llm_mock()

    with patch("run_pipeline.get_client", return_value=llm_mock), \
         patch("pipeline.stages.s2_collect.fetch_semantic_scholar", new_callable=AsyncMock) as mock_ss, \
         patch("pipeline.stages.s2_collect.fetch_arxiv", new_callable=AsyncMock) as mock_ax:
        mock_ss.return_value = sample_papers
        mock_ax.return_value = []
        run_dir = await run("LLM agents", config)

    metrics = json.loads((run_dir / "weekly_metrics.json").read_text())
    assert metrics["collected"] == 3
    assert metrics["screened"] == 2  # 3개 중 include 2개
    assert metrics["gaps"] == 3
    assert metrics["hypotheses"] == 3
    assert metrics["domain"] == "LLM agents"
