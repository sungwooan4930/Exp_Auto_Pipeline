# Prompt Skill Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract hardcoded SYSTEM + PROMPT_TEMPLATE constants from 5 pipeline stages into `.md` files under `pipeline/prompts/`, enabling prompt fine-tuning without touching Python code.

**Architecture:** A `load_prompt(name)` utility in `pipeline/prompts/__init__.py` reads `{name}.md`, parses `## System` and `## Prompt` sections, and returns `(system, prompt_template)`. Each stage imports this at module level (load-once on import). The function accepts an optional `_base` path parameter for test isolation using `tmp_path`.

**Tech Stack:** Python 3.11+, pytest, pathlib (stdlib only — no new dependencies)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `pipeline/prompts/__init__.py` | `load_prompt()` parser utility |
| Create | `pipeline/prompts/s1_query_gen.md` | S1 system + prompt template |
| Create | `pipeline/prompts/s3_screen.md` | S3 system + prompt template |
| Create | `pipeline/prompts/s4_gap.md` | S4 system + prompt template |
| Create | `pipeline/prompts/s5_hypothesis.md` | S5 system + prompt template |
| Create | `pipeline/prompts/s6_experiment.md` | S6 system + prompt template |
| Create | `tests/test_prompts_loader.py` | Unit tests for `load_prompt()` |
| Modify | `pipeline/stages/s1_query_gen.py` | Replace constants with `load_prompt()` |
| Modify | `pipeline/stages/s3_screen.py` | Replace constants with `load_prompt()` |
| Modify | `pipeline/stages/s4_gap.py` | Replace constants with `load_prompt()` |
| Modify | `pipeline/stages/s5_hypothesis.py` | Replace constants with `load_prompt()` |
| Modify | `pipeline/stages/s6_experiment.py` | Replace constants with `load_prompt()` |

---

## Task 1: `load_prompt()` 유틸 함수 (TDD)

**Files:**
- Create: `pipeline/prompts/__init__.py`
- Create: `tests/test_prompts_loader.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_prompts_loader.py` 파일을 생성:

```python
import pytest
from pathlib import Path
from pipeline.prompts import load_prompt


def _write_md(tmp_path: Path, name: str, content: str) -> Path:
    """tmp_path에 {name}.md 파일 생성 후 경로 반환."""
    p = tmp_path / f"{name}.md"
    p.write_text(content, encoding="utf-8")
    return tmp_path


def test_load_prompt_returns_system_and_template(tmp_path):
    """정상 .md 파싱 시 (system, template) 튜플 반환."""
    base = _write_md(tmp_path, "test_stage", """\
## System
You are a test assistant.

## Prompt
Hello {name}, you are in {domain}.
""")
    system, template = load_prompt("test_stage", _base=base)
    assert system == "You are a test assistant."
    assert template == "Hello {name}, you are in {domain}."


def test_load_prompt_file_not_found(tmp_path):
    """존재하지 않는 파일명 → FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent", _base=tmp_path)


def test_load_prompt_missing_system_section(tmp_path):
    """## System 없는 파일 → ValueError."""
    base = _write_md(tmp_path, "no_system", """\
## Prompt
Hello {domain}.
""")
    with pytest.raises(ValueError, match="## System"):
        load_prompt("no_system", _base=base)


def test_load_prompt_missing_prompt_section(tmp_path):
    """## Prompt 없는 파일 → ValueError."""
    base = _write_md(tmp_path, "no_prompt", """\
## System
You are a test assistant.
""")
    with pytest.raises(ValueError, match="## Prompt"):
        load_prompt("no_prompt", _base=base)


def test_load_prompt_preserves_placeholders(tmp_path):
    """{domain}, {n_queries} 등 플레이스홀더 문자 그대로 유지."""
    base = _write_md(tmp_path, "placeholders", """\
## System
System text.

## Prompt
Generate {n_queries} queries for {domain}.
""")
    _, template = load_prompt("placeholders", _base=base)
    assert "{n_queries}" in template
    assert "{domain}" in template
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd /c/Exp_Auto_Pipeline && python -m pytest tests/test_prompts_loader.py -v
```

Expected: `ModuleNotFoundError: No module named 'pipeline.prompts'` (또는 `ImportError`)

- [ ] **Step 3: `pipeline/prompts/__init__.py` 구현**

```python
from pathlib import Path


def load_prompt(name: str, _base: Path | None = None) -> tuple[str, str]:
    """pipeline/prompts/{name}.md 에서 System·Prompt 섹션을 파싱해 반환.

    Args:
        name: .md 파일 이름 (확장자 제외). 예: "s1_query_gen"
        _base: 테스트용 오버라이드 경로. None이면 이 파일과 같은 디렉터리 사용.

    Returns:
        (system, prompt_template) — 각각 strip() 처리된 str

    Raises:
        FileNotFoundError: .md 파일이 없을 때
        ValueError: ## System 또는 ## Prompt 섹션 누락 시
    """
    base = _base if _base is not None else Path(__file__).parent
    path = base / f"{name}.md"
    text = path.read_text(encoding="utf-8")  # FileNotFoundError는 자연 전파

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.strip() == "## System":
            current = "system"
            sections[current] = []
        elif line.strip() == "## Prompt":
            current = "prompt"
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    if "system" not in sections:
        raise ValueError(f"{name}.md: ## System 섹션 없음")
    if "prompt" not in sections:
        raise ValueError(f"{name}.md: ## Prompt 섹션 없음")

    return "\n".join(sections["system"]).strip(), "\n".join(sections["prompt"]).strip()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_prompts_loader.py -v
```

Expected: 5개 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/prompts/__init__.py tests/test_prompts_loader.py
git commit -m "feat: add load_prompt() utility for pipeline prompt files"
```

---

## Task 2: 프롬프트 `.md` 파일 5개 생성

**Files:**
- Create: `pipeline/prompts/s1_query_gen.md`
- Create: `pipeline/prompts/s3_screen.md`
- Create: `pipeline/prompts/s4_gap.md`
- Create: `pipeline/prompts/s5_hypothesis.md`
- Create: `pipeline/prompts/s6_experiment.md`

- [ ] **Step 1: `pipeline/prompts/s1_query_gen.md` 생성**

```markdown
## System
You are a research assistant. Output ONLY valid JSON arrays, no explanation.

## Prompt
Generate {n_queries} diverse academic search queries for the research domain: "{domain}"

Rules:
- Each query should target a different angle (methods, benchmarks, applications, limitations)
- Queries should be suitable for Semantic Scholar and arXiv search
- Output ONLY a JSON array of strings, e.g. ["query1", "query2", ...]

Domain: {domain}
```

- [ ] **Step 2: `pipeline/prompts/s3_screen.md` 생성**

```markdown
## System
You are a systematic review assistant. Output ONLY valid JSON, no explanation.

## Prompt
You are screening papers for a systematic literature review on the domain: "{domain}"

Paper to screen:
Title: {title}
Abstract: {abstract}

Decide whether to INCLUDE or EXCLUDE this paper.
- INCLUDE if: directly relevant to the domain, empirical/theoretical contribution
- EXCLUDE if: tangentially related, off-topic, no abstract

Output ONLY this JSON (no markdown):
{{"decision": "include" or "exclude", "reason": "one sentence explanation"}}
```

- [ ] **Step 3: `pipeline/prompts/s4_gap.md` 생성**

```markdown
## System
You are a research gap analyst. Output ONLY valid JSON arrays, no explanation.

## Prompt
Analyze the following screened papers and identify research gaps.

Papers:
{papers_text}

Identify at least {min_gaps} distinct research gaps — areas that existing papers do NOT adequately address.
For each gap, cite which paper IDs support the finding.

Output ONLY a JSON array (no markdown):
[
  {{"gap_id": "gap_001", "gap": "description of gap", "evidence_papers": ["paper_id1", "paper_id2"]}},
  ...
]
```

- [ ] **Step 4: `pipeline/prompts/s5_hypothesis.md` 생성**

```markdown
## System
You are a research hypothesis generator. Output ONLY valid JSON arrays, no explanation.

## Prompt
Based on the following research gaps and supporting papers, generate structured research hypotheses.

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
]
```

- [ ] **Step 5: `pipeline/prompts/s6_experiment.md` 생성**

```markdown
## System
You are a research experiment designer. Write clear, reproducible experiment plans in Markdown.

## Prompt
Design a complete experiment plan to test the following research hypotheses.

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

A third party should be able to replicate the experiment from this document alone.
```

- [ ] **Step 6: `.md` 파일이 `load_prompt()`로 파싱되는지 빠른 검증**

```bash
python -c "
from pipeline.prompts import load_prompt
for name in ['s1_query_gen', 's3_screen', 's4_gap', 's5_hypothesis', 's6_experiment']:
    s, p = load_prompt(name)
    assert s, f'{name}: system empty'
    assert p, f'{name}: prompt empty'
    print(f'{name}: OK (system={len(s)}chars, prompt={len(p)}chars)')
"
```

Expected:
```
s1_query_gen: OK (system=..., prompt=...)
s3_screen: OK (...)
s4_gap: OK (...)
s5_hypothesis: OK (...)
s6_experiment: OK (...)
```

- [ ] **Step 7: 커밋**

```bash
git add pipeline/prompts/s1_query_gen.md pipeline/prompts/s3_screen.md pipeline/prompts/s4_gap.md pipeline/prompts/s5_hypothesis.md pipeline/prompts/s6_experiment.md
git commit -m "feat: add prompt .md files for pipeline stages s1/s3/s4/s5/s6"
```

---

## Task 3: s1_query_gen.py 리팩토링

**Files:**
- Modify: `pipeline/stages/s1_query_gen.py`

- [ ] **Step 1: 기존 테스트 통과 확인 (baseline)**

```bash
python -m pytest tests/test_s1_query_gen.py -v
```

Expected: 모두 PASS

- [ ] **Step 2: `s1_query_gen.py` 상단 수정**

현재:
```python
import json
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

SYSTEM = "You are a research assistant. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Generate {n_queries} diverse academic search queries for the research domain: "{domain}"
...
Domain: {domain}"""
```

변경 후:
```python
import json
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s1_query_gen")
```

- [ ] **Step 3: 함수 내부 참조 교체**

현재 `generate_queries()` 함수:
```python
def generate_queries(domain: str, llm: LLMClient, config: Config) -> dict:
    prompt = PROMPT_TEMPLATE.format(domain=domain, n_queries=7)
    raw = llm.complete(prompt, system=SYSTEM)
```

변경 후:
```python
def generate_queries(domain: str, llm: LLMClient, config: Config) -> dict:
    prompt = _PROMPT_TEMPLATE.format(domain=domain, n_queries=7)
    raw = llm.complete(prompt, system=_SYSTEM)
```

- [ ] **Step 4: 테스트 재실행**

```bash
python -m pytest tests/test_s1_query_gen.py -v
```

Expected: 모두 PASS (LLM mock이 실제 프롬프트 내용에 의존하지 않으므로 변경 없이 통과)

- [ ] **Step 5: 커밋**

```bash
git add pipeline/stages/s1_query_gen.py
git commit -m "refactor: load s1 prompts from s1_query_gen.md"
```

---

## Task 4: s3_screen.py 리팩토링

**Files:**
- Modify: `pipeline/stages/s3_screen.py`

- [ ] **Step 1: 기존 테스트 통과 확인**

```bash
python -m pytest tests/test_s3_screen.py -v
```

Expected: 모두 PASS

- [ ] **Step 2: `s3_screen.py` 상단 수정**

현재:
```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a systematic review assistant. Output ONLY valid JSON, no explanation."

PROMPT_TEMPLATE = """You are screening papers for a systematic literature review on the domain: "{domain}"
...
Output ONLY this JSON (no markdown):
{{"decision": "include" or "exclude", "reason": "one sentence explanation"}}"""
```

변경 후:
```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s3_screen")
```

- [ ] **Step 3: 함수 내부 참조 교체**

현재 `screen_papers()` 내:
```python
        prompt = PROMPT_TEMPLATE.format(
            domain=domain,
            title=paper.get("title", ""),
            abstract=paper.get("abstract", "")
        )
        raw = llm.complete(prompt, system=SYSTEM)
```

변경 후:
```python
        prompt = _PROMPT_TEMPLATE.format(
            domain=domain,
            title=paper.get("title", ""),
            abstract=paper.get("abstract", "")
        )
        raw = llm.complete(prompt, system=_SYSTEM)
```

- [ ] **Step 4: 테스트 재실행**

```bash
python -m pytest tests/test_s3_screen.py -v
```

Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/stages/s3_screen.py
git commit -m "refactor: load s3 prompts from s3_screen.md"
```

---

## Task 5: s4_gap.py 리팩토링

**Files:**
- Modify: `pipeline/stages/s4_gap.py`

- [ ] **Step 1: 기존 테스트 통과 확인**

```bash
python -m pytest tests/test_s4_gap.py -v
```

Expected: 모두 PASS

- [ ] **Step 2: `s4_gap.py` 상단 수정**

현재:
```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a research gap analyst. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Analyze the following screened papers and identify research gaps.
...
]"""
```

변경 후:
```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s4_gap")
```

- [ ] **Step 3: 함수 내부 참조 교체**

현재 `analyze_gaps()` 내:
```python
    prompt = PROMPT_TEMPLATE.format(papers_text=papers_text, min_gaps=config.min_gaps)
    raw = llm.complete(prompt, system=SYSTEM)
```

변경 후:
```python
    prompt = _PROMPT_TEMPLATE.format(papers_text=papers_text, min_gaps=config.min_gaps)
    raw = llm.complete(prompt, system=_SYSTEM)
```

- [ ] **Step 4: 테스트 재실행**

```bash
python -m pytest tests/test_s4_gap.py -v
```

Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/stages/s4_gap.py
git commit -m "refactor: load s4 prompts from s4_gap.md"
```

---

## Task 6: s5_hypothesis.py 리팩토링

**Files:**
- Modify: `pipeline/stages/s5_hypothesis.py`

- [ ] **Step 1: 기존 테스트 통과 확인**

```bash
python -m pytest tests/test_s5_hypothesis.py -v
```

Expected: 모두 PASS

- [ ] **Step 2: `s5_hypothesis.py` 상단 수정**

현재:
```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a research hypothesis generator. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Based on the following research gaps and supporting papers, generate structured research hypotheses.
...
]"""
```

변경 후:
```python
import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s5_hypothesis")
```

- [ ] **Step 3: 함수 내부 참조 교체**

현재 `generate_hypotheses()` 내:
```python
    prompt = PROMPT_TEMPLATE.format(
        gaps_text=gaps_text,
        papers_text=papers_text,
        min_hypotheses=config.min_hypotheses
    )
    raw = llm.complete(prompt, system=SYSTEM)
```

변경 후:
```python
    prompt = _PROMPT_TEMPLATE.format(
        gaps_text=gaps_text,
        papers_text=papers_text,
        min_hypotheses=config.min_hypotheses
    )
    raw = llm.complete(prompt, system=_SYSTEM)
```

- [ ] **Step 4: 테스트 재실행**

```bash
python -m pytest tests/test_s5_hypothesis.py -v
```

Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/stages/s5_hypothesis.py
git commit -m "refactor: load s5 prompts from s5_hypothesis.md"
```

---

## Task 7: s6_experiment.py 리팩토링

**Files:**
- Modify: `pipeline/stages/s6_experiment.py`

- [ ] **Step 1: 기존 테스트 통과 확인**

```bash
python -m pytest tests/test_s6_experiment.py -v
```

Expected: 모두 PASS

- [ ] **Step 2: `s6_experiment.py` 상단 수정**

현재:
```python
from pipeline.config import Config
from pipeline.llm import LLMClient

SYSTEM = "You are a research experiment designer. Write clear, reproducible experiment plans in Markdown."

PROMPT_TEMPLATE = """Design a complete experiment plan to test the following research hypotheses.
...
A third party should be able to replicate the experiment from this document alone."""
```

변경 후:
```python
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s6_experiment")
```

- [ ] **Step 3: 함수 내부 참조 교체**

현재 `design_experiment()` 내:
```python
    prompt = PROMPT_TEMPLATE.format(hypotheses_text=hypotheses_text)
    return llm.complete(prompt, system=SYSTEM)
```

변경 후:
```python
    prompt = _PROMPT_TEMPLATE.format(hypotheses_text=hypotheses_text)
    return llm.complete(prompt, system=_SYSTEM)
```

- [ ] **Step 4: 테스트 재실행**

```bash
python -m pytest tests/test_s6_experiment.py -v
```

Expected: 모두 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/stages/s6_experiment.py
git commit -m "refactor: load s6 prompts from s6_experiment.md"
```

---

## Task 8: 전체 테스트 실행 및 최종 확인

**Files:** (없음 — 검증만)

- [ ] **Step 1: 전체 테스트 스위트 실행**

```bash
python -m pytest --tb=short -q
```

Expected: 기존 37개 + 새 5개 = **42개 PASS**, 0 FAIL

- [ ] **Step 2: 프롬프트 fine-tuning 가능 여부 smoke test**

```bash
python -c "
from pipeline.prompts import load_prompt
s, p = load_prompt('s1_query_gen')
print('System:', s[:60])
print('Prompt preview:', p[:80])
# 플레이스홀더 포맷 동작 확인
filled = p.format(n_queries=7, domain='LLM planning')
print('Formatted OK, length:', len(filled))
"
```

Expected: 오류 없이 출력

- [ ] **Step 3: 최종 커밋**

```bash
git add docs/superpowers/plans/2026-03-31-prompt-skill-refactor.md
git commit -m "docs: add prompt-skill-refactor implementation plan"
```
