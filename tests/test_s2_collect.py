import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from pipeline.stages.s2_collect import deduplicate_papers, papers_to_bibtex, collect_papers
from pipeline.config import Config

FIXTURES = Path("tests/fixtures")


@pytest.fixture
def sample_papers():
    return json.loads((FIXTURES / "sample_papers.json").read_text())


def test_deduplicate_removes_same_doi(sample_papers):
    # sample_papers에 ss_001과 ax_001은 같은 DOI
    result = deduplicate_papers(sample_papers)
    dois = [p["doi"] for p in result]
    assert len(dois) == len(set(dois))


def test_deduplicate_keeps_unique_papers(sample_papers):
    result = deduplicate_papers(sample_papers)
    assert len(result) == 2  # 3개 중 중복 1개 제거


def test_papers_to_bibtex_produces_valid_format():
    papers = [
        {
            "paper_id": "p1",
            "title": "Test Paper",
            "authors": ["Smith, John"],
            "year": 2023,
            "doi": "10.1234/test",
            "abstract": "An abstract.",
            "source": "semantic_scholar"
        }
    ]
    bib = papers_to_bibtex(papers)
    assert "@article" in bib
    assert "Test Paper" in bib
    assert "Smith, John" in bib
    assert "2023" in bib


@pytest.mark.asyncio
async def test_collect_papers_deduplicates(sample_papers):
    config = Config(target_papers=50)
    with patch("pipeline.stages.s2_collect.fetch_semantic_scholar", new_callable=AsyncMock) as mock_ss, \
         patch("pipeline.stages.s2_collect.fetch_arxiv", new_callable=AsyncMock) as mock_ax:
        mock_ss.return_value = sample_papers[:2]
        mock_ax.return_value = [sample_papers[1]]  # 중복
        result = await collect_papers(["test query"], config)
    assert len(result) == 2
