import json
import pytest
from pathlib import Path
from pipeline.stages.s7_metrics import compute_metrics


def _write_fixtures(tmp_path: Path):
    (tmp_path / "search_queries.json").write_text(json.dumps({
        "domain": "LLM agents", "queries": ["q1", "q2"]
    }))
    bib_content = "\n".join(f"@article{{p{i}, title={{T}}}}" for i in range(42))
    (tmp_path / "collected_papers.bib").write_text(bib_content)
    screening = (
        [{"paper_id": f"p{i}", "decision": "include"} for i in range(18)] +
        [{"paper_id": f"p{i}", "decision": "exclude"} for i in range(18, 42)]
    )
    (tmp_path / "screening_results.json").write_text(json.dumps(screening))
    gaps = [{"gap_id": f"gap_{i}", "gap": "g"} for i in range(4)]
    (tmp_path / "gap_analysis.json").write_text(json.dumps(gaps))
    hypotheses = [{"hypothesis_id": f"h_{i}"} for i in range(4)]
    (tmp_path / "hypotheses.json").write_text(json.dumps(hypotheses))
    return tmp_path


def test_compute_metrics_returns_dict(tmp_path):
    _write_fixtures(tmp_path)
    result = compute_metrics(tmp_path, "LLM agents")
    assert isinstance(result, dict)


def test_compute_metrics_counts_collected(tmp_path):
    _write_fixtures(tmp_path)
    result = compute_metrics(tmp_path, "LLM agents")
    assert result["collected"] == 42


def test_compute_metrics_counts_screened(tmp_path):
    _write_fixtures(tmp_path)
    result = compute_metrics(tmp_path, "LLM agents")
    assert result["screened"] == 18


def test_compute_metrics_screen_rate(tmp_path):
    _write_fixtures(tmp_path)
    result = compute_metrics(tmp_path, "LLM agents")
    assert abs(result["screen_rate"] - 18/42) < 0.001


def test_compute_metrics_counts_gaps_and_hypotheses(tmp_path):
    _write_fixtures(tmp_path)
    result = compute_metrics(tmp_path, "LLM agents")
    assert result["gaps"] == 4
    assert result["hypotheses"] == 4


def test_compute_metrics_has_timestamp_and_domain(tmp_path):
    _write_fixtures(tmp_path)
    result = compute_metrics(tmp_path, "LLM agents")
    assert "timestamp" in result
    assert result["domain"] == "LLM agents"
    assert "run_id" in result
