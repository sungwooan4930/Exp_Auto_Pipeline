# RAP (Research Automation Pipeline) — 설계 문서

**날짜:** 2026-03-31
**상태:** 승인됨
**참조:** `ref_papers/[RAP] 1주차 숙제.pdf`

---

## 1. 목표

연구 도메인 문자열 하나를 입력받아 문헌 검색 → 선별 → 갭 분석 → 가설 도출 → 실험 설계까지 전체 흐름을 자동화한다. 각 단계는 독립적으로 실행 및 테스트 가능하며, 산출물은 타임스탬프 폴더에 저장된다.

---

## 2. 디렉토리 구조

```
Exp_Auto_Pipeline/
├── pipeline/
│   ├── __init__.py
│   ├── config.py           # provider 설정, API 키, 경로, 임계값
│   ├── llm.py              # LLM 클라이언트 추상화 (Claude / OpenAI)
│   └── stages/
│       ├── __init__.py
│       ├── s1_query_gen.py     # ① 검색 쿼리 생성
│       ├── s2_collect.py       # ② 논문 수집 (Semantic Scholar + arXiv 병렬)
│       ├── s3_screen.py        # ③ 문헌 선별
│       ├── s4_gap.py           # ④ 갭 분석
│       ├── s5_hypothesis.py    # ⑤ 가설 도출
│       ├── s6_experiment.py    # ⑥ 실험 설계
│       └── s7_metrics.py       # 메트릭 집계
├── tests/
│   ├── fixtures/           # 테스트용 샘플 데이터 (JSON, bib)
│   ├── test_s1_query_gen.py
│   ├── test_s2_collect.py
│   ├── test_s3_screen.py
│   ├── test_s4_gap.py
│   ├── test_s5_hypothesis.py
│   ├── test_s6_experiment.py
│   ├── test_s7_metrics.py
│   └── test_pipeline_integration.py
├── outputs/
│   └── YYYY-MM-DD_HHMMSS/  # 실행 결과물 (타임스탬프 폴더)
│       ├── search_queries.json
│       ├── collected_papers.bib
│       ├── screening_results.json
│       ├── gap_analysis.json
│       ├── hypotheses.json
│       ├── experiment_design.md
│       └── weekly_metrics.json
├── run_pipeline.py         # 전체 파이프라인 진입점
├── run_stage.py            # 단일 단계 실행
├── requirements.txt
└── .env.example
```

---

## 3. 파이프라인 단계

### 단계별 입출력 및 완료 기준

| # | 단계 | 입력 | 출력 | 완료 기준 |
|---|------|------|------|-----------|
| 1 | 검색 쿼리 생성 | domain string | `search_queries.json` | 쿼리 실행 시 관련 논문 검색됨 |
| 2 | 논문 수집 | search_queries.json | `collected_papers.bib` | 50건 수집, 중복 제거됨 |
| 3 | 문헌 선별 | collected_papers.bib | `screening_results.json` | 15~20건, 판정 근거 명시 |
| 4 | 갭 분석 | screening_results.json | `gap_analysis.json` | 갭 3개+, 근거 논문 매핑 |
| 5 | 가설 도출 | gap_analysis.json | `hypotheses.json` | 가설 3개+, 독립/종속변수 명시 |
| 6 | 실험 설계 | hypotheses.json | `experiment_design.md` | 제3자가 읽고 재현 가능 |
| 7 | 메트릭 집계 | 모든 산출물 | `weekly_metrics.json` | 수집건수·선별율·갭수·가설수 집계 |

### 각 단계 상세

**S1 — 검색 쿼리 생성**
- LLM에 도메인을 입력해 5~10개의 다각도 검색 쿼리 생성
- 출력: `{"domain": "...", "queries": ["query1", "query2", ...]}`

**S2 — 논문 수집**
- Semantic Scholar API와 arXiv API를 병렬 호출
- 제목·저자·초록·연도·DOI 수집
- DOI 및 제목 유사도 기반 중복 제거
- 목표 50건; 미달 시 경고 로그 후 계속 진행
- 출력: BibTeX 형식 `.bib` 파일

**S3 — 문헌 선별**
- 각 논문 초록을 LLM에 제출, include/exclude 판정 + 근거 생성
- 목표 15~20건; 미달 시 임계값 완화 후 재시도 1회
- 출력: `[{"paper_id": "...", "decision": "include"|"exclude", "reason": "..."}]`

**S4 — 갭 분석**
- 선별된 논문 전체를 LLM에 제출, 연구 갭 3개 이상 도출
- 각 갭에 근거 논문 ID 매핑
- 출력: `[{"gap": "...", "evidence_papers": ["id1", "id2"]}]`

**S5 — 가설 도출**
- 각 갭으로부터 구조화된 가설 생성 (독립변수 → 종속변수 형태)
- 참신성 검증: 기존 논문 제목/초록과 유사도 비교
- 출력: `[{"hypothesis": "...", "independent_var": "...", "dependent_var": "...", "novelty_score": 0.0~1.0}]`

**S6 — 실험 설계**
- 가설별 실험 계획 작성: 변수 정의, 데이터셋, 방법론, 평가지표, 베이스라인, 예상 결과
- 출력: Markdown 문서 (`experiment_design.md`)

**S7 — 메트릭 집계**
- 모든 산출물 읽어 정량 지표 계산
- 출력: `{"collected": 50, "screened": 18, "screen_rate": 0.36, "gaps": 4, "hypotheses": 4}`

---

## 4. 컴포넌트 설계

### 4.1 LLM 클라이언트 (`pipeline/llm.py`)

```python
class LLMClient:
    def complete(self, prompt: str, system: str = "") -> str: ...

class ClaudeClient(LLMClient): ...   # anthropic SDK
class OpenAIClient(LLMClient): ...   # openai SDK

def get_client() -> LLMClient:
    provider = os.getenv("PROVIDER", "claude")
    # "claude" → ClaudeClient, "openai" → OpenAIClient
```

- 각 Stage는 `get_client()`만 호출하며 provider를 모름
- 기본값: Claude (`claude-sonnet-4-6`)
- 교체: `PROVIDER=openai` 환경변수 설정

### 4.2 설정 (`pipeline/config.py`)

```python
@dataclass
class Config:
    provider: str = "claude"
    claude_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    target_papers: int = 50
    min_screened: int = 15
    max_screened: int = 20
    min_gaps: int = 3
    min_hypotheses: int = 3
    output_base: Path = Path("outputs")
    api_retry_count: int = 3
    api_retry_backoff: float = 2.0  # seconds, exponential
```

### 4.3 진입점

**전체 파이프라인:**
```bash
python run_pipeline.py --domain "LLM-based autonomous agents"
python run_pipeline.py --domain "..." --provider openai
```

**단일 단계:**
```bash
python run_stage.py --stage 3 --input outputs/2026-03-31_143022/
python run_pipeline.py --domain "..." --from-stage 4 --input outputs/2026-03-31_143022/
```

---

## 5. 에러 처리

- **API 실패:** 3회 exponential backoff 재시도 (2s, 4s, 8s). 실패 시 예외 발생 + 로그
- **수집 50건 미달:** 경고 로그 후 다음 단계 진행
- **선별 15건 미달:** 임계값을 10건으로 낮춰 재판정 1회 재시도. 그래도 미달 시 경고 후 진행
- **갭/가설 미달:** 경고 로그 후 진행 (완료 기준은 검증 단계에서 확인)
- **단계 실패:** 이전 단계 산출물 보존. 재실행 시 `--from-stage`로 해당 단계부터 재시작

---

## 6. 테스트 전략 (TDD)

### 원칙
- 각 Stage 구현 전 테스트 먼저 작성
- LLM 호출은 `unittest.mock.patch`로 격리
- 외부 API(Semantic Scholar, arXiv)는 `tests/fixtures/`의 샘플 JSON으로 대체
- 각 Stage 함수는 순수 함수에 가깝게 설계 (입력 → 출력, 부작용 최소화)

### 테스트 범위

| 파일 | 테스트 대상 |
|------|------------|
| `test_s1_query_gen.py` | 쿼리 수 (5~10개), JSON 스키마 유효성 |
| `test_s2_collect.py` | 중복 제거 로직, BibTeX 포맷, 병렬 수집 결과 병합 |
| `test_s3_screen.py` | include/exclude 판정 형식, reason 필드 존재, 임계값 재시도 |
| `test_s4_gap.py` | 갭 3개+ 검증, evidence_papers 매핑 존재 |
| `test_s5_hypothesis.py` | 독립/종속변수 필드, novelty_score 범위 (0~1) |
| `test_s6_experiment.py` | Markdown 출력 형식, 필수 섹션 존재 |
| `test_s7_metrics.py` | 정량 지표 계산 정확성 |
| `test_pipeline_integration.py` | 전체 파이프라인 end-to-end (모든 API mock) |

---

## 7. 산출물 스키마

### `search_queries.json`
```json
{"domain": "string", "queries": ["string"]}
```

### `screening_results.json`
```json
[{"paper_id": "string", "title": "string", "abstract": "string", "decision": "include|exclude", "reason": "string"}]
```

### `gap_analysis.json`
```json
[{"gap_id": "string", "gap": "string", "evidence_papers": ["paper_id"]}]
```

### `hypotheses.json`
```json
[{"hypothesis_id": "string", "hypothesis": "string", "independent_var": "string", "dependent_var": "string", "expected_relation": "string", "novelty_score": 0.0}]
```

### `weekly_metrics.json`
```json
{"run_id": "string", "domain": "string", "timestamp": "ISO8601", "collected": 0, "screened": 0, "screen_rate": 0.0, "gaps": 0, "hypotheses": 0}
```

---

## 8. 의존성

```
anthropic          # Claude API
openai             # OpenAI API (선택)
httpx              # 비동기 HTTP (arXiv, Semantic Scholar)
bibtexparser       # BibTeX 파싱/생성
pytest             # 테스트
pytest-asyncio     # 비동기 테스트
python-dotenv      # 환경변수 로드
```
