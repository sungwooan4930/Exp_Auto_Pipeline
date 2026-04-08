# Prompt Skill Refactor — 설계 문서

**날짜:** 2026-03-31
**상태:** 승인됨
**참조:** `docs/superpowers/specs/2026-03-31-rap-pipeline-design.md`

---

## 1. 목표

각 Pipeline Stage에 하드코딩된 SYSTEM 프롬프트와 PROMPT_TEMPLATE을 `.md` 파일로 분리해, Python 코드를 수정하지 않고 프롬프트를 독립적으로 fine-tuning할 수 있도록 한다.

---

## 2. 파일 구조

```
pipeline/
├── prompts/
│   ├── __init__.py          # load_prompt() 유틸 함수
│   ├── s1_query_gen.md
│   ├── s3_screen.md
│   ├── s4_gap.md
│   ├── s5_hypothesis.md
│   └── s6_experiment.md
tests/
└── test_prompts_loader.py
```

---

## 3. 프롬프트 파일 형식

각 `.md` 파일은 `## System`과 `## Prompt` 섹션으로 구분된다.

```markdown
## System
You are a research assistant. Output ONLY valid JSON arrays, no explanation.

## Prompt
Generate {n_queries} diverse academic search queries for the research domain: "{domain}"

Requirements:
- ...
```

- `## System`: LLM `system` 파라미터로 전달되는 텍스트
- `## Prompt`: `str.format()` 플레이스홀더(`{변수명}`)를 포함하는 템플릿
- 섹션 순서는 System → Prompt 고정
- 두 섹션 모두 필수 (누락 시 `ValueError`)

---

## 4. `load_prompt()` 구현

**파일:** `pipeline/prompts/__init__.py`

```python
from pathlib import Path

def load_prompt(name: str) -> tuple[str, str]:
    """pipeline/prompts/{name}.md 에서 System·Prompt 섹션을 파싱해 반환.

    Returns:
        (system, prompt_template) — 둘 다 str, strip() 처리됨
    Raises:
        FileNotFoundError: .md 파일 없을 때
        ValueError: ## System 또는 ## Prompt 섹션 누락 시
    """
    path = Path(__file__).parent / f"{name}.md"
    text = path.read_text(encoding="utf-8")

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.strip() == "## System":
            current = "system"
            sections[current] = []
        elif line.strip() == "## Prompt":
            current = "prompt"
            sections[current] = []
        elif current:
            sections[current].append(line)

    if "system" not in sections:
        raise ValueError(f"{name}.md: ## System 섹션 없음")
    if "prompt" not in sections:
        raise ValueError(f"{name}.md: ## Prompt 섹션 없음")

    return "\n".join(sections["system"]).strip(), "\n".join(sections["prompt"]).strip()
```

**로딩 시점:** 모듈 임포트 시 1회 (`path.read_text()` 호출). Stage 실행마다 파일을 다시 읽지 않음.

---

## 5. Stage 파일 변경

### 변경 대상

| Stage | 파일 | 변경 내용 |
|-------|------|-----------|
| S1 | `pipeline/stages/s1_query_gen.py` | `SYSTEM`, `PROMPT_TEMPLATE` → `load_prompt("s1_query_gen")` |
| S3 | `pipeline/stages/s3_screen.py` | `SYSTEM`, `PROMPT_TEMPLATE` → `load_prompt("s3_screen")` |
| S4 | `pipeline/stages/s4_gap.py` | `SYSTEM`, `PROMPT_TEMPLATE` → `load_prompt("s4_gap")` |
| S5 | `pipeline/stages/s5_hypothesis.py` | `SYSTEM`, `PROMPT_TEMPLATE` → `load_prompt("s5_hypothesis")` |
| S6 | `pipeline/stages/s6_experiment.py` | `SYSTEM`, `PROMPT_TEMPLATE` → `load_prompt("s6_experiment")` |

S2(논문 수집), S7(메트릭)는 LLM 프롬프트 없음 → 변경 없음.

### 변경 패턴 (예: s1_query_gen.py)

```python
# 제거
SYSTEM = "You are a research assistant. ..."
PROMPT_TEMPLATE = """Generate ..."""

# 추가 (import 직후 모듈 레벨)
from pipeline.prompts import load_prompt
_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s1_query_gen")
```

함수 본문에서 `SYSTEM` → `_SYSTEM`, `PROMPT_TEMPLATE` → `_PROMPT_TEMPLATE`으로 참조 교체.

---

## 6. 테스트 전략

**새 파일:** `tests/test_prompts_loader.py`

테스트는 `tmp_path` pytest fixture로 임시 `.md` 파일을 생성해 `load_prompt()`에 주입. `pipeline/prompts/` 실제 파일에 의존하지 않아 격리됨.

`load_prompt(name)`은 `Path(__file__).parent / f"{name}.md"`를 사용하므로, 테스트에서는 `monkeypatch`로 `pipeline.prompts.Path` 또는 파일 내용을 주입하거나, `tmp_path`에 `.md` 파일을 만든 후 함수에 직접 경로를 전달하는 헬퍼를 사용한다.

| 테스트 케이스 | 검증 내용 |
|-------------|-----------|
| `test_load_prompt_returns_system_and_template` | 정상 `.md` 파싱 시 (system, template) 튜플 반환 |
| `test_load_prompt_file_not_found` | 존재하지 않는 파일명 → `FileNotFoundError` |
| `test_load_prompt_missing_system_section` | `## System` 없는 파일 → `ValueError` |
| `test_load_prompt_missing_prompt_section` | `## Prompt` 없는 파일 → `ValueError` |
| `test_load_prompt_preserves_placeholders` | `{domain}` 등 플레이스홀더 문자 그대로 유지 |

**기존 37개 테스트:** LLM mock을 그대로 사용하므로 변경 없음. 모두 통과 유지 필수.

---

## 7. 영향 범위

- **새 파일:** `pipeline/prompts/__init__.py`, `.md` 5개, `tests/test_prompts_loader.py`
- **수정 파일:** Stage 5개 (각 상단 3~5줄 변경, 내부 변수 참조 교체)
- **변경 없는 파일:** `s2_collect.py`, `s7_metrics.py`, `config.py`, `llm.py`, `run_pipeline.py`, `run_stage.py`
- **기존 테스트:** 변경 없음

---

## 8. 프롬프트 fine-tuning 방법

리팩토링 완료 후 프롬프트 수정 방법:

1. `pipeline/prompts/` 아래 해당 Stage `.md` 파일 열기
2. `## System` 또는 `## Prompt` 섹션 내용 수정
3. `run_pipeline.py` 또는 `run_stage.py` 재실행 — Python 코드 수정 불필요
