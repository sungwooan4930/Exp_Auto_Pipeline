# RAP (Research Automation Pipeline) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 연구 도메인 문자열을 입력받아 문헌 검색 → 선별 → 갭 분석 → 가설 도출 → 실험 설계까지 자동화하는 CLI 파이프라인을 구축한다.

**Architecture:** 7개의 독립 Stage 모듈(`pipeline/stages/s1_*.py` ~ `s7_*.py`)이 순차 실행되며, 각 단계 결과물은 `outputs/YYYY-MM-DD_HHMMSS/`에 저장된다. LLM 호출은 `pipeline/llm.py`의 `LLMClient` 추상화를 통해 Claude(기본) / OpenAI 교체 가능.

**Tech Stack:** Python 3.11+, anthropic SDK, openai SDK, httpx (async), bibtexparser, pytest, python-dotenv

---

## File Map

| 파일 | 역할 |
|------|------|
| `requirements.txt` | 의존성 목록 |
| `.env.example` | 환경변수 예시 |
| `pipeline/__init__.py` | 패키지 초기화 |
| `pipeline/config.py` | Config 데이터클래스 + 환경변수 로드 |
| `pipeline/llm.py` | LLMClient 추상 기반 클래스, ClaudeClient, OpenAIClient, get_client() |
| `pipeline/stages/__init__.py` | stages 패키지 초기화 |
| `pipeline/stages/s1_query_gen.py` | generate_queries(domain, llm, config) → dict |
| `pipeline/stages/s2_collect.py` | collect_papers(queries, config) → list[dict] + save_bib() |
| `pipeline/stages/s3_screen.py` | screen_papers(papers, domain, llm, config) → list[dict] |
| `pipeline/stages/s4_gap.py` | analyze_gaps(screened, llm, config) → list[dict] |
| `pipeline/stages/s5_hypothesis.py` | generate_hypotheses(gaps, screened, llm, config) → list[dict] |
| `pipeline/stages/s6_experiment.py` | design_experiment(hypotheses, llm, config) → str (markdown) |
| `pipeline/stages/s7_metrics.py` | compute_metrics(output_dir, domain) → dict |
| `run_pipeline.py` | CLI 진입점 (전체 실행) |
| `run_stage.py` | CLI 진입점 (단일 단계 실행) |
| `tests/fixtures/sample_queries.json` | S1 테스트 픽스처 |
| `tests/fixtures/sample_papers.json` | S2/S3 테스트 픽스처 (5건 샘플) |
| `tests/fixtures/sample_screening.json` | S4 테스트 픽스처 |
| `tests/fixtures/sample_gaps.json` | S5 테스트 픽스처 |
| `tests/fixtures/sample_hypotheses.json` | S6 테스트 픽스처 |
| `tests/test_s1_query_gen.py` | S1 단위 테스트 |
| `tests/test_s2_collect.py` | S2 단위 테스트 |
| `tests/test_s3_screen.py` | S3 단위 테스트 |
| `tests/test_s4_gap.py` | S4 단위 테스트 |
| `tests/test_s5_hypothesis.py` | S5 단위 테스트 |
| `tests/test_s6_experiment.py` | S6 단위 테스트 |
| `tests/test_s7_metrics.py` | S7 단위 테스트 |
| `tests/test_pipeline_integration.py` | end-to-end 통합 테스트 |

---

## Task 1: 프로젝트 기반 설정

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `pipeline/__init__.py`
- Create: `pipeline/stages/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/fixtures/` (directory)

- [ ] **Step 1: requirements.txt 작성**

```
anthropic>=0.40.0
openai>=1.50.0
httpx>=0.27.0
bibtexparser>=2.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
python-dotenv>=1.0.0
```

파일 경로: `requirements.txt`

- [ ] **Step 2: .env.example 작성**

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PROVIDER=claude
```

파일 경로: `.env.example`

- [ ] **Step 3: 디렉토리 및 빈 __init__.py 생성**

```bash
mkdir -p pipeline/stages tests/fixtures
touch pipeline/__init__.py pipeline/stages/__init__.py tests/__init__.py
```

- [ ] **Step 4: 의존성 설치**

```bash
pip install -r requirements.txt
```

Expected: 모든 패키지 설치 완료, 에러 없음

- [ ] **Step 5: 설치 확인**

```bash
python -c "import anthropic, openai, httpx, bibtexparser; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git init
git add requirements.txt .env.example pipeline/ tests/
git commit -m "chore: project scaffold and dependencies"
```

---

## Task 2: Config + LLM 클라이언트

**Files:**
- Create: `pipeline/config.py`
- Create: `pipeline/llm.py`

- [ ] **Step 1: pipeline/config.py 작성**

```python
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    provider: str = field(default_factory=lambda: os.getenv("PROVIDER", "claude"))
    claude_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    target_papers: int = 50
    min_screened: int = 15
    max_screened: int = 20
    min_gaps: int = 3
    min_hypotheses: int = 3
    output_base: Path = Path("outputs")
    api_retry_count: int = 3
    api_retry_backoff: float = 2.0
```

- [ ] **Step 2: pipeline/llm.py 작성**

```python
import os
import time
from abc import ABC, abstractmethod
from pipeline.config import Config


class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str = "") -> str:
        ...


class ClaudeClient(LLMClient):
    def __init__(self, config: Config):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self._model = config.claude_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        messages = [{"role": "user", "content": prompt}]
        kwargs = {"model": self._model, "max_tokens": 4096, "messages": messages}
        if system:
            kwargs["system"] = system
        for attempt in range(self._retry_count):
            try:
                response = self._client.messages.create(**kwargs)
                return response.content[0].text
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                time.sleep(self._backoff * (2 ** attempt))


class OpenAIClient(LLMClient):
    def __init__(self, config: Config):
        import openai
        self._client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._model = config.openai_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        for attempt in range(self._retry_count):
            try:
                response = self._client.chat.completions.create(
                    model=self._model, messages=messages, max_tokens=4096
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                time.sleep(self._backoff * (2 ** attempt))


def get_client(config: Config | None = None) -> LLMClient:
    if config is None:
        config = Config()
    if config.provider == "openai":
        return OpenAIClient(config)
    return ClaudeClient(config)
```

- [ ] **Step 3: LLMClient 테스트 작성 — `tests/test_llm.py`**

```python
from unittest.mock import MagicMock, patch
from pipeline.config import Config
from pipeline.llm import get_client, ClaudeClient, OpenAIClient


def test_get_client_returns_claude_by_default():
    config = Config(provider="claude")
    with patch("anthropic.Anthropic"):
        client = get_client(config)
    assert isinstance(client, ClaudeClient)


def test_get_client_returns_openai_when_set():
    config = Config(provider="openai")
    with patch("openai.OpenAI"):
        client = get_client(config)
    assert isinstance(client, OpenAIClient)


def test_claude_complete_returns_text():
    config = Config(provider="claude")
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="test response")]
        mock_anthropic.return_value.messages.create.return_value = mock_msg
        client = ClaudeClient(config)
        result = client.complete("hello")
    assert result == "test response"


def test_claude_complete_retries_on_failure():
    config = Config(provider="claude", api_retry_count=2, api_retry_backoff=0.0)
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="ok")]
        mock_anthropic.return_value.messages.create.side_effect = [
            Exception("rate limit"), mock_msg
        ]
        client = ClaudeClient(config)
        result = client.complete("hello")
    assert result == "ok"
```

- [ ] **Step 4: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_llm.py -v
```

Expected: `ModuleNotFoundError` 또는 `ImportError` (아직 파일 없음)

- [ ] **Step 5: 테스트 재실행 — 통과 확인**

```bash
pytest tests/test_llm.py -v
```

Expected: 4개 PASSED

- [ ] **Step 6: Commit**

```bash
git add pipeline/config.py pipeline/llm.py tests/test_llm.py
git commit -m "feat: config dataclass and LLM client abstraction (Claude/OpenAI)"
```

---

## Task 3: S1 — 검색 쿼리 생성

**Files:**
- Create: `pipeline/stages/s1_query_gen.py`
- Create: `tests/fixtures/sample_queries.json`
- Create: `tests/test_s1_query_gen.py`

- [ ] **Step 1: 테스트 픽스처 작성 — `tests/fixtures/sample_queries.json`**

```json
{
  "domain": "LLM-based autonomous agents",
  "queries": [
    "LLM autonomous agent planning",
    "large language model task decomposition",
    "LLM tool use agent benchmark",
    "autonomous agent reasoning evaluation",
    "chain-of-thought planning LLM"
  ]
}
```

- [ ] **Step 2: 테스트 먼저 작성 — `tests/test_s1_query_gen.py`**

```python
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
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s1_query_gen.py -v
```

Expected: `ImportError: cannot import name 'generate_queries'`

- [ ] **Step 4: s1_query_gen.py 구현**

```python
import json
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

SYSTEM = "You are a research assistant. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Generate {n_queries} diverse academic search queries for the research domain: "{domain}"

Rules:
- Each query should target a different angle (methods, benchmarks, applications, limitations)
- Queries should be suitable for Semantic Scholar and arXiv search
- Output ONLY a JSON array of strings, e.g. ["query1", "query2", ...]

Domain: {domain}"""


def generate_queries(domain: str, llm: LLMClient, config: Config) -> dict:
    prompt = PROMPT_TEMPLATE.format(domain=domain, n_queries=7)
    raw = llm.complete(prompt, system=SYSTEM)
    # JSON 배열 추출 (LLM이 마크다운 코드블록으로 감쌀 수 있음)
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        queries = json.loads(match.group())
    else:
        queries = json.loads(raw)
    # 5~10개 범위로 클리핑
    queries = [q for q in queries if isinstance(q, str) and q.strip()][:10]
    if len(queries) < 5:
        raise ValueError(f"LLM returned only {len(queries)} queries, expected 5+")
    return {"domain": domain, "queries": queries}
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s1_query_gen.py -v
```

Expected: 4개 PASSED

- [ ] **Step 6: Commit**

```bash
git add pipeline/stages/s1_query_gen.py tests/test_s1_query_gen.py tests/fixtures/sample_queries.json
git commit -m "feat: S1 query generation with TDD"
```

---

## Task 4: S2 — 논문 수집

**Files:**
- Create: `pipeline/stages/s2_collect.py`
- Create: `tests/fixtures/sample_papers.json`
- Create: `tests/test_s2_collect.py`

- [ ] **Step 1: 테스트 픽스처 작성 — `tests/fixtures/sample_papers.json`**

```json
[
  {
    "paper_id": "ss_001",
    "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
    "abstract": "We explore the use of LLMs to generate reasoning traces and task-specific actions in an interleaved manner.",
    "authors": ["Yao, Shunyu", "Zhao, Jeffrey"],
    "year": 2023,
    "doi": "10.48550/arXiv.2210.03629",
    "source": "semantic_scholar"
  },
  {
    "paper_id": "ax_001",
    "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
    "abstract": "We explore the use of LLMs to generate reasoning traces and task-specific actions in an interleaved manner.",
    "authors": ["Yao, Shunyu"],
    "year": 2023,
    "doi": "10.48550/arXiv.2210.03629",
    "source": "arxiv"
  },
  {
    "paper_id": "ss_002",
    "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
    "abstract": "We introduce a framework for LLM inference that allows deliberate decision making.",
    "authors": ["Yao, Shunyu"],
    "year": 2023,
    "doi": "10.48550/arXiv.2305.10601",
    "source": "semantic_scholar"
  }
]
```

- [ ] **Step 2: 테스트 작성 — `tests/test_s2_collect.py`**

```python
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
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s2_collect.py -v
```

Expected: `ImportError`

- [ ] **Step 4: s2_collect.py 구현**

```python
import asyncio
import hashlib
import json
import logging
import re
import httpx
from pipeline.config import Config

logger = logging.getLogger(__name__)

SS_API = "https://api.semanticscholar.org/graph/v1/paper/search"
ARXIV_API = "https://export.arxiv.org/api/query"


async def fetch_semantic_scholar(query: str, limit: int = 25) -> list[dict]:
    params = {
        "query": query,
        "limit": limit,
        "fields": "paperId,title,abstract,authors,year,externalIds"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SS_API, params=params)
        resp.raise_for_status()
        data = resp.json()
    papers = []
    for p in data.get("data", []):
        doi = (p.get("externalIds") or {}).get("DOI", "")
        papers.append({
            "paper_id": f"ss_{p.get('paperId', '')[:8]}",
            "title": p.get("title", ""),
            "abstract": p.get("abstract", ""),
            "authors": [a["name"] for a in (p.get("authors") or [])],
            "year": p.get("year", 0),
            "doi": doi,
            "source": "semantic_scholar"
        })
    return papers


async def fetch_arxiv(query: str, limit: int = 25) -> list[dict]:
    params = {"search_query": f"all:{query}", "start": 0, "max_results": limit}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()
        text = resp.text
    papers = []
    entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
    for entry in entries:
        title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
        abstract = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
        doi_match = re.search(r'<arxiv:doi>(.*?)</arxiv:doi>', entry)
        id_match = re.search(r'<id>(.*?)</id>', entry)
        authors = re.findall(r'<name>(.*?)</name>', entry)
        year_match = re.search(r'<published>(\d{4})', entry)
        arxiv_id = (id_match.group(1) if id_match else "").split("/")[-1]
        doi = doi_match.group(1).strip() if doi_match else f"arxiv:{arxiv_id}"
        papers.append({
            "paper_id": f"ax_{arxiv_id[:8]}",
            "title": (title.group(1) if title else "").strip(),
            "abstract": (abstract.group(1) if abstract else "").strip(),
            "authors": authors,
            "year": int(year_match.group(1)) if year_match else 0,
            "doi": doi,
            "source": "arxiv"
        })
    return papers


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen = {}
    for p in papers:
        doi = p.get("doi", "").strip().lower()
        if doi:
            key = doi
        else:
            # DOI 없으면 제목 정규화로 중복 판단
            key = re.sub(r'\s+', ' ', p.get("title", "").lower().strip())
        if key and key not in seen:
            seen[key] = p
    return list(seen.values())


def papers_to_bibtex(papers: list[dict]) -> str:
    lines = []
    for p in papers:
        key = re.sub(r'\W+', '', p.get("paper_id", "p"))
        authors = " and ".join(p.get("authors", ["Unknown"]))
        lines.append(f'@article{{{key},')
        lines.append(f'  title = {{{p.get("title", "")}}},')
        lines.append(f'  author = {{{authors}}},')
        lines.append(f'  year = {{{p.get("year", "")}}},')
        lines.append(f'  doi = {{{p.get("doi", "")}}},')
        lines.append(f'  abstract = {{{p.get("abstract", "")}}},')
        lines.append('}')
        lines.append('')
    return "\n".join(lines)


async def collect_papers(queries: list[str], config: Config) -> list[dict]:
    tasks = []
    per_query = max(5, config.target_papers // len(queries))
    for q in queries:
        tasks.append(fetch_semantic_scholar(q, per_query))
        tasks.append(fetch_arxiv(q, per_query))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_papers = []
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"API fetch failed: {r}")
        else:
            all_papers.extend(r)
    deduped = deduplicate_papers(all_papers)
    if len(deduped) < config.target_papers:
        logger.warning(f"Collected {len(deduped)} papers, target was {config.target_papers}")
    return deduped[:config.target_papers]
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s2_collect.py -v
```

Expected: 4개 PASSED

- [ ] **Step 6: Commit**

```bash
git add pipeline/stages/s2_collect.py tests/test_s2_collect.py tests/fixtures/sample_papers.json
git commit -m "feat: S2 paper collection with SS+arXiv parallel fetch and deduplication"
```

---

## Task 5: S3 — 문헌 선별

**Files:**
- Create: `pipeline/stages/s3_screen.py`
- Create: `tests/fixtures/sample_screening.json`
- Create: `tests/test_s3_screen.py`

- [ ] **Step 1: 픽스처 작성 — `tests/fixtures/sample_screening.json`**

```json
[
  {
    "paper_id": "ss_001",
    "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
    "abstract": "We explore the use of LLMs to generate reasoning traces and task-specific actions in an interleaved manner.",
    "decision": "include",
    "reason": "Directly addresses LLM-based agent planning and action generation."
  },
  {
    "paper_id": "ss_002",
    "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
    "abstract": "We introduce a framework for LLM inference that allows deliberate decision making.",
    "decision": "include",
    "reason": "Core paper on structured LLM reasoning, directly relevant."
  }
]
```

- [ ] **Step 2: 테스트 작성 — `tests/test_s3_screen.py`**

```python
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
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s3_screen.py -v
```

Expected: `ImportError`

- [ ] **Step 4: s3_screen.py 구현**

```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a systematic review assistant. Output ONLY valid JSON, no explanation."

PROMPT_TEMPLATE = """You are screening papers for a systematic literature review on the domain: "{domain}"

Paper to screen:
Title: {title}
Abstract: {abstract}

Decide whether to INCLUDE or EXCLUDE this paper.
- INCLUDE if: directly relevant to the domain, empirical/theoretical contribution
- EXCLUDE if: tangentially related, off-topic, no abstract

Output ONLY this JSON (no markdown):
{{"decision": "include" or "exclude", "reason": "one sentence explanation"}}"""


def _parse_screening_response(raw: str) -> dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)


def screen_papers(papers: list[dict], domain: str, llm: LLMClient, config: Config) -> list[dict]:
    results = []
    for paper in papers:
        prompt = PROMPT_TEMPLATE.format(
            domain=domain,
            title=paper.get("title", ""),
            abstract=paper.get("abstract", "")
        )
        raw = llm.complete(prompt, system=SYSTEM)
        parsed = _parse_screening_response(raw)
        results.append({
            "paper_id": paper["paper_id"],
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "decision": parsed.get("decision", "exclude"),
            "reason": parsed.get("reason", "")
        })

    included = [r for r in results if r["decision"] == "include"]

    if len(included) < config.min_screened:
        logger.warning(
            f"Screened papers ({len(included)}) below minimum ({config.min_screened}). "
            f"Relaxing threshold — returning all screened results."
        )

    return results
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s3_screen.py -v
```

Expected: 4개 PASSED

- [ ] **Step 6: Commit**

```bash
git add pipeline/stages/s3_screen.py tests/test_s3_screen.py tests/fixtures/sample_screening.json
git commit -m "feat: S3 literature screening with LLM include/exclude judgment"
```

---

## Task 6: S4 — 갭 분석

**Files:**
- Create: `pipeline/stages/s4_gap.py`
- Create: `tests/fixtures/sample_gaps.json`
- Create: `tests/test_s4_gap.py`

- [ ] **Step 1: 픽스처 작성 — `tests/fixtures/sample_gaps.json`**

```json
[
  {
    "gap_id": "gap_001",
    "gap": "Multimodal context in LLM planning has not been systematically studied.",
    "evidence_papers": ["ss_001", "ss_002"]
  },
  {
    "gap_id": "gap_002",
    "gap": "Long-horizon task planning with memory retrieval lacks benchmark evaluation.",
    "evidence_papers": ["ss_002"]
  },
  {
    "gap_id": "gap_003",
    "gap": "Robustness of LLM agents under adversarial instruction injection is underexplored.",
    "evidence_papers": ["ss_001"]
  }
]
```

- [ ] **Step 2: 테스트 작성 — `tests/test_s4_gap.py`**

```python
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
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s4_gap.py -v
```

Expected: `ImportError`

- [ ] **Step 4: s4_gap.py 구현**

```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a research gap analyst. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Analyze the following screened papers and identify research gaps.

Papers:
{papers_text}

Identify at least {min_gaps} distinct research gaps — areas that existing papers do NOT adequately address.
For each gap, cite which paper IDs support the finding.

Output ONLY a JSON array (no markdown):
[
  {{"gap_id": "gap_001", "gap": "description of gap", "evidence_papers": ["paper_id1", "paper_id2"]}},
  ...
]"""


def analyze_gaps(screened: list[dict], llm: LLMClient, config: Config) -> list[dict]:
    included = [p for p in screened if p.get("decision") == "include"]
    if not included:
        included = screened  # fallback

    papers_text = "\n\n".join(
        f"[{p['paper_id']}] {p['title']}\n{p['abstract']}"
        for p in included
    )
    prompt = PROMPT_TEMPLATE.format(papers_text=papers_text, min_gaps=config.min_gaps)
    raw = llm.complete(prompt, system=SYSTEM)

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    gaps = json.loads(match.group() if match else raw)

    if len(gaps) < config.min_gaps:
        logger.warning(f"Only {len(gaps)} gaps identified, minimum is {config.min_gaps}")

    return gaps
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s4_gap.py -v
```

Expected: 4개 PASSED

- [ ] **Step 6: Commit**

```bash
git add pipeline/stages/s4_gap.py tests/test_s4_gap.py tests/fixtures/sample_gaps.json
git commit -m "feat: S4 research gap analysis"
```

---

## Task 7: S5 — 가설 도출

**Files:**
- Create: `pipeline/stages/s5_hypothesis.py`
- Create: `tests/fixtures/sample_hypotheses.json`
- Create: `tests/test_s5_hypothesis.py`

- [ ] **Step 1: 픽스처 작성 — `tests/fixtures/sample_hypotheses.json`**

```json
[
  {
    "hypothesis_id": "h_001",
    "hypothesis": "Providing multimodal context improves LLM planning accuracy.",
    "independent_var": "Multimodal context (text + image)",
    "dependent_var": "LLM planning accuracy (task completion rate)",
    "expected_relation": "positive correlation",
    "novelty_score": 0.82
  },
  {
    "hypothesis_id": "h_002",
    "hypothesis": "External memory retrieval increases long-horizon task success in LLM agents.",
    "independent_var": "External memory retrieval module",
    "dependent_var": "Long-horizon task success rate",
    "expected_relation": "positive correlation",
    "novelty_score": 0.75
  },
  {
    "hypothesis_id": "h_003",
    "hypothesis": "Adversarial instruction injection reduces LLM agent task completion.",
    "independent_var": "Adversarial instruction injection",
    "dependent_var": "Task completion rate",
    "expected_relation": "negative correlation",
    "novelty_score": 0.88
  }
]
```

- [ ] **Step 2: 테스트 작성 — `tests/test_s5_hypothesis.py`**

```python
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
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s5_hypothesis.py -v
```

Expected: `ImportError`

- [ ] **Step 4: s5_hypothesis.py 구현**

```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a research hypothesis generator. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Based on the following research gaps and supporting papers, generate structured research hypotheses.

Research Gaps:
{gaps_text}

Supporting Paper Abstracts:
{papers_text}

Generate at least {min_hypotheses} hypotheses. For each:
- State the hypothesis clearly (if X then Y format)
- Identify the independent variable (what you manipulate)
- Identify the dependent variable (what you measure)
- State expected relationship direction
- Estimate novelty score (0.0–1.0) vs existing literature

Output ONLY a JSON array (no markdown):
[
  {{
    "hypothesis_id": "h_001",
    "hypothesis": "...",
    "independent_var": "...",
    "dependent_var": "...",
    "expected_relation": "positive correlation" or "negative correlation" or "no effect",
    "novelty_score": 0.0
  }},
  ...
]"""


def generate_hypotheses(
    gaps: list[dict],
    screened: list[dict],
    llm: LLMClient,
    config: Config
) -> list[dict]:
    gaps_text = "\n".join(
        f"[{g['gap_id']}] {g['gap']}" for g in gaps
    )
    included = [p for p in screened if p.get("decision") == "include"]
    papers_text = "\n\n".join(
        f"[{p['paper_id']}] {p['title']}: {p['abstract'][:300]}"
        for p in included[:10]  # 토큰 절약
    )
    prompt = PROMPT_TEMPLATE.format(
        gaps_text=gaps_text,
        papers_text=papers_text,
        min_hypotheses=config.min_hypotheses
    )
    raw = llm.complete(prompt, system=SYSTEM)
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    hypotheses = json.loads(match.group() if match else raw)

    # novelty_score 범위 클리핑
    for h in hypotheses:
        h["novelty_score"] = max(0.0, min(1.0, float(h.get("novelty_score", 0.5))))

    if len(hypotheses) < config.min_hypotheses:
        logger.warning(f"Only {len(hypotheses)} hypotheses generated, minimum is {config.min_hypotheses}")

    return hypotheses
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s5_hypothesis.py -v
```

Expected: 4개 PASSED

- [ ] **Step 6: Commit**

```bash
git add pipeline/stages/s5_hypothesis.py tests/test_s5_hypothesis.py tests/fixtures/sample_hypotheses.json
git commit -m "feat: S5 hypothesis generation with novelty scoring"
```

---

## Task 8: S6 — 실험 설계

**Files:**
- Create: `pipeline/stages/s6_experiment.py`
- Create: `tests/test_s6_experiment.py`

- [ ] **Step 1: 테스트 작성 — `tests/test_s6_experiment.py`**

```python
import json
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from pipeline.stages.s6_experiment import design_experiment
from pipeline.config import Config

FIXTURES = Path("tests/fixtures")

REQUIRED_SECTIONS = [
    "## 1.",   # Overview or Research Questions
    "## 2.",   # Variables
    "## 3.",   # Methodology
    "## 4.",   # Evaluation
    "## 5.",   # Expected Results
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
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s6_experiment.py -v
```

Expected: `ImportError`

- [ ] **Step 3: s6_experiment.py 구현**

```python
from pipeline.config import Config
from pipeline.llm import LLMClient

SYSTEM = "You are a research experiment designer. Write clear, reproducible experiment plans in Markdown."

PROMPT_TEMPLATE = """Design a complete experiment plan to test the following research hypotheses.

Hypotheses:
{hypotheses_text}

Write a Markdown document with EXACTLY these 5 sections (use these exact headings):
## 1. Research Overview
## 2. Variables
## 3. Methodology
## 4. Evaluation Metrics
## 5. Expected Results

Requirements:
- Section 2: List all independent and dependent variables with operational definitions
- Section 3: Describe dataset selection, baseline models, experimental conditions, and procedure step-by-step
- Section 4: Define each metric with formula or measurement method
- Section 5: State predicted outcomes for each hypothesis

A third party should be able to replicate the experiment from this document alone."""


def design_experiment(hypotheses: list[dict], llm: LLMClient, config: Config) -> str:
    hypotheses_text = "\n\n".join(
        f"[{h['hypothesis_id']}] {h['hypothesis']}\n"
        f"  Independent: {h['independent_var']}\n"
        f"  Dependent: {h['dependent_var']}\n"
        f"  Expected: {h['expected_relation']}"
        for h in hypotheses
    )
    prompt = PROMPT_TEMPLATE.format(hypotheses_text=hypotheses_text)
    return llm.complete(prompt, system=SYSTEM)
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s6_experiment.py -v
```

Expected: 3개 PASSED

- [ ] **Step 5: Commit**

```bash
git add pipeline/stages/s6_experiment.py tests/test_s6_experiment.py
git commit -m "feat: S6 experiment design generation"
```

---

## Task 9: S7 — 메트릭 집계

**Files:**
- Create: `pipeline/stages/s7_metrics.py`
- Create: `tests/test_s7_metrics.py`

- [ ] **Step 1: 테스트 작성 — `tests/test_s7_metrics.py`**

```python
import json
import pytest
from pathlib import Path
from pipeline.stages.s7_metrics import compute_metrics


def _write_fixtures(tmp_path: Path):
    (tmp_path / "search_queries.json").write_text(json.dumps({
        "domain": "LLM agents", "queries": ["q1", "q2"]
    }))
    papers = [{"paper_id": f"p{i}"} for i in range(42)]
    # BibTeX 파일 — 논문 수는 @article 태그 수로 카운트
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
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_s7_metrics.py -v
```

Expected: `ImportError`

- [ ] **Step 3: s7_metrics.py 구현**

```python
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def compute_metrics(output_dir: Path, domain: str) -> dict:
    output_dir = Path(output_dir)

    # 수집 건수: BibTeX @article 태그 수
    bib_path = output_dir / "collected_papers.bib"
    collected = 0
    if bib_path.exists():
        collected = len(re.findall(r'@\w+\{', bib_path.read_text()))

    # 선별 건수
    screening_path = output_dir / "screening_results.json"
    screened = 0
    if screening_path.exists():
        screening = json.loads(screening_path.read_text())
        screened = sum(1 for p in screening if p.get("decision") == "include")

    screen_rate = round(screened / collected, 4) if collected > 0 else 0.0

    # 갭 수
    gap_path = output_dir / "gap_analysis.json"
    gaps = 0
    if gap_path.exists():
        gaps = len(json.loads(gap_path.read_text()))

    # 가설 수
    hyp_path = output_dir / "hypotheses.json"
    hypotheses = 0
    if hyp_path.exists():
        hypotheses = len(json.loads(hyp_path.read_text()))

    run_id = output_dir.name

    return {
        "run_id": run_id,
        "domain": domain,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "collected": collected,
        "screened": screened,
        "screen_rate": screen_rate,
        "gaps": gaps,
        "hypotheses": hypotheses,
    }
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_s7_metrics.py -v
```

Expected: 6개 PASSED

- [ ] **Step 5: Commit**

```bash
git add pipeline/stages/s7_metrics.py tests/test_s7_metrics.py
git commit -m "feat: S7 metrics aggregation"
```

---

## Task 10: CLI 진입점 — run_pipeline.py + run_stage.py

**Files:**
- Create: `run_pipeline.py`
- Create: `run_stage.py`

- [ ] **Step 1: run_pipeline.py 작성**

```python
#!/usr/bin/env python3
"""전체 파이프라인 실행: python run_pipeline.py --domain "LLM-based autonomous agents" """
import argparse
import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from pipeline.config import Config
from pipeline.llm import get_client
from pipeline.stages.s1_query_gen import generate_queries
from pipeline.stages.s2_collect import collect_papers, papers_to_bibtex
from pipeline.stages.s3_screen import screen_papers
from pipeline.stages.s4_gap import analyze_gaps
from pipeline.stages.s5_hypothesis import generate_hypotheses
from pipeline.stages.s6_experiment import design_experiment
from pipeline.stages.s7_metrics import compute_metrics


def make_run_dir(config: Config) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = config.output_base / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


async def run(domain: str, config: Config, from_stage: int = 1, input_dir: Path | None = None):
    run_dir = input_dir if input_dir else make_run_dir(config)
    llm = get_client(config)
    logger.info(f"Run dir: {run_dir}, domain: {domain}, provider: {config.provider}")

    # S1
    if from_stage <= 1:
        logger.info("Stage 1: Generating queries...")
        queries_data = generate_queries(domain, llm, config)
        (run_dir / "search_queries.json").write_text(json.dumps(queries_data, ensure_ascii=False, indent=2))
        logger.info(f"  → {len(queries_data['queries'])} queries saved")
    else:
        queries_data = json.loads((run_dir / "search_queries.json").read_text())

    # S2
    if from_stage <= 2:
        logger.info("Stage 2: Collecting papers...")
        papers = await collect_papers(queries_data["queries"], config)
        (run_dir / "collected_papers.bib").write_text(papers_to_bibtex(papers))
        # JSON도 저장 (S3에서 사용)
        (run_dir / "collected_papers.json").write_text(json.dumps(papers, ensure_ascii=False, indent=2))
        logger.info(f"  → {len(papers)} papers collected")
    else:
        papers = json.loads((run_dir / "collected_papers.json").read_text())

    # S3
    if from_stage <= 3:
        logger.info("Stage 3: Screening papers...")
        screened = screen_papers(papers, domain, llm, config)
        (run_dir / "screening_results.json").write_text(json.dumps(screened, ensure_ascii=False, indent=2))
        included = sum(1 for p in screened if p["decision"] == "include")
        logger.info(f"  → {included} papers included")
    else:
        screened = json.loads((run_dir / "screening_results.json").read_text())

    # S4
    if from_stage <= 4:
        logger.info("Stage 4: Analyzing gaps...")
        gaps = analyze_gaps(screened, llm, config)
        (run_dir / "gap_analysis.json").write_text(json.dumps(gaps, ensure_ascii=False, indent=2))
        logger.info(f"  → {len(gaps)} gaps identified")
    else:
        gaps = json.loads((run_dir / "gap_analysis.json").read_text())

    # S5
    if from_stage <= 5:
        logger.info("Stage 5: Generating hypotheses...")
        hypotheses = generate_hypotheses(gaps, screened, llm, config)
        (run_dir / "hypotheses.json").write_text(json.dumps(hypotheses, ensure_ascii=False, indent=2))
        logger.info(f"  → {len(hypotheses)} hypotheses generated")
    else:
        hypotheses = json.loads((run_dir / "hypotheses.json").read_text())

    # S6
    if from_stage <= 6:
        logger.info("Stage 6: Designing experiment...")
        experiment_md = design_experiment(hypotheses, llm, config)
        (run_dir / "experiment_design.md").write_text(experiment_md)
        logger.info("  → experiment_design.md written")

    # S7
    logger.info("Stage 7: Computing metrics...")
    metrics = compute_metrics(run_dir, domain)
    (run_dir / "weekly_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    logger.info(f"  → Metrics: {metrics}")
    logger.info(f"Pipeline complete. Results in: {run_dir}")
    return run_dir


def main():
    parser = argparse.ArgumentParser(description="RAP: Research Automation Pipeline")
    parser.add_argument("--domain", required=True, help="Research domain string")
    parser.add_argument("--provider", default=None, help="LLM provider: claude (default) or openai")
    parser.add_argument("--from-stage", type=int, default=1, help="Resume from stage N (1-6)")
    parser.add_argument("--input", default=None, help="Existing output dir to resume from")
    args = parser.parse_args()

    config = Config()
    if args.provider:
        config.provider = args.provider
    if args.input:
        os.environ.setdefault("PROVIDER", config.provider)

    input_dir = Path(args.input) if args.input else None
    asyncio.run(run(args.domain, config, from_stage=args.from_stage, input_dir=input_dir))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: run_stage.py 작성**

```python
#!/usr/bin/env python3
"""단일 단계 실행: python run_stage.py --stage 3 --input outputs/2026-03-31_143022/"""
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from run_pipeline import run


def main():
    parser = argparse.ArgumentParser(description="RAP: Run a single stage")
    parser.add_argument("--stage", type=int, required=True, choices=range(1, 8), help="Stage number (1-7)")
    parser.add_argument("--input", required=True, help="Existing output dir")
    parser.add_argument("--domain", default="", help="Domain (required for stage 1)")
    args = parser.parse_args()

    from pipeline.config import Config
    config = Config()
    input_dir = Path(args.input)

    # 도메인: stage 1은 필수, 이후 단계는 search_queries.json에서 읽음
    domain = args.domain
    if not domain and (input_dir / "search_queries.json").exists():
        import json
        domain = json.loads((input_dir / "search_queries.json").read_text()).get("domain", "")

    asyncio.run(run(domain, config, from_stage=args.stage, input_dir=input_dir))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: import 확인**

```bash
python -c "from run_pipeline import run; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add run_pipeline.py run_stage.py
git commit -m "feat: CLI entry points run_pipeline.py and run_stage.py"
```

---

## Task 11: 통합 테스트

**Files:**
- Create: `tests/test_pipeline_integration.py`

- [ ] **Step 1: 통합 테스트 작성**

```python
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
    # S1
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
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
pytest tests/test_pipeline_integration.py -v
```

Expected: `ImportError` 또는 fixture 관련 에러

- [ ] **Step 3: 테스트 실행 — 통과 확인**

```bash
pytest tests/test_pipeline_integration.py -v
```

Expected: 2개 PASSED

- [ ] **Step 4: 전체 테스트 스위트 실행**

```bash
pytest tests/ -v --tb=short
```

Expected: 모든 테스트 PASSED (최소 27개)

- [ ] **Step 5: Commit**

```bash
git add tests/test_pipeline_integration.py
git commit -m "test: end-to-end integration test for full pipeline"
```

---

## Task 12: pytest 설정 및 최종 확인

**Files:**
- Create: `pytest.ini`

- [ ] **Step 1: pytest.ini 작성**

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
log_cli = true
log_cli_level = WARNING
```

- [ ] **Step 2: 전체 테스트 최종 실행**

```bash
pytest tests/ -v
```

Expected: 모든 테스트 PASSED, 에러 없음

- [ ] **Step 3: 도움말 확인**

```bash
python run_pipeline.py --help
python run_stage.py --help
```

Expected: 사용법 출력됨

- [ ] **Step 4: 최종 Commit**

```bash
git add pytest.ini
git commit -m "chore: add pytest config and finalize project"
```

---

## 셀프 리뷰

**Spec 커버리지 확인:**
- [x] S1 검색 쿼리 생성 → Task 3
- [x] S2 논문 수집 (SS + arXiv 병렬, 중복 제거) → Task 4
- [x] S3 문헌 선별 (include/exclude + 근거) → Task 5
- [x] S4 갭 분석 (3개+, 근거 논문 매핑) → Task 6
- [x] S5 가설 도출 (독립/종속변수, novelty_score) → Task 7
- [x] S6 실험 설계 (재현 가능 Markdown) → Task 8
- [x] S7 메트릭 집계 → Task 9
- [x] LLM provider 교체 (Claude/OpenAI) → Task 2
- [x] 타임스탬프 폴더 저장 → Task 10
- [x] --from-stage 재실행 → Task 10
- [x] 에러 처리 (retry, 임계값 경고) → Task 2, 5
- [x] TDD (테스트 먼저) → 전 Task
- [x] 통합 테스트 → Task 11

**타입 일관성:** `generate_queries`, `collect_papers`, `screen_papers`, `analyze_gaps`, `generate_hypotheses`, `design_experiment`, `compute_metrics` 시그니처 전 Task 통일 확인됨.
