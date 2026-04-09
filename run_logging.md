# 실행 로그

최종 업데이트: 2026-04-08

## 프로젝트 개요

- 프로젝트명: RAP (Research Automation Pipeline)
- 기준 문서: `ref_papers/[RAP] 1주차 숙제.pdf`
- 현재 상태: 기존 코드 기반 파이프라인 위에 Claude Code용 하이브리드 구조를 적용하는 중
- 진행 기준 문서:
  - `CLAUDE.md`
  - `RAP_PROJECT_PROFILE.json`
  - `claude/project/PROJECT_GUIDE.md`
  - `claude/workflows/rap-workflow.md`

## 현재 진행 상태

### 방향 변경

- 프로젝트의 major 방향이 변경됨
- 기존 Python 파이프라인 중심 구조에서 Claude Code용 Markdown 지침 및 skill 중심 구조로 전환 중
- workflow도 크게 변경됨
- 명시적 시작 이름을 `rap-pipeline`으로 지정함
- `rap-pipeline 시작` 호출 시 바로 실행하지 않고 단계 선택지를 먼저 제시하도록 변경함
- 하이브리드 구조를 도입함
  - 코어: 전역 또는 마켓플레이스 스킬팩 `rap-pipeline`
  - 로컬: `RAP_PROJECT_PROFILE.json`, `search_cycle_input.json`, `run_logging.md`
- 코어 스킬팩 분리용 초안 경로를 `skillpacks/rap-pipeline-core/`로 생성함
- 연구 서치 단계는 연구자 승인까지 반복되는 search-feedback loop로 재정의
- 아이디어 구체화 단계는 gap-hypothesis 승인 루프, experiment design, simulation-prediction 순서로 재정의
- 모든 단계는 정규화된 JSON input/output 파일을 기준으로 연결하도록 변경

### 구현됨

- `run_pipeline.py`에 전체 Stage 실행 흐름이 존재함
- `s1`부터 `s7`까지 Stage 모듈이 존재함
- `app.py`에 Streamlit UI가 존재함
- Stage 단위 테스트 및 통합 테스트 코드가 존재함
- 회의 플로우차트 SVG 시안 추가 완료
  - `docs/meeting_flowchart.svg`
- workflow 시각화 SVG 추가 완료
  - `docs/rap_workflow.svg`
- Claude Code용 상위 지침 문서 추가
  - `CLAUDE.md`
  - `claude/project/PROJECT_GUIDE.md`
  - `claude/project/PIPELINE_START.md`
  - `claude/project/EXECUTION_PROMPT_TEMPLATE.md`
  - `claude/project/PROJECT_PROFILE_SCHEMA.md`
- 하이브리드 구조용 프로젝트 로컬 프로필 추가
  - `RAP_PROJECT_PROFILE.json`
- 코어 스킬팩 초안 패키지 추가
  - `skillpacks/rap-pipeline-core/`
- Claude Code용 skill 체계 재구성
  - `claude/skills/rap-orchestrator`
  - `claude/skills/rap-search-cycle`
  - `claude/skills/rap-gap-hypothesis-cycle`
  - `claude/skills/rap-experiment-design`
  - `claude/skills/rap-simulation-prediction`
  - `claude/skills/rap-metrics-tracking`
- 각 skill용 JSON 스키마 및 example JSON 초안 추가
- 시작용 루트 JSON 파일 추가
  - `search_cycle_input.json`

### 진행 중

- 하이브리드 구조 기준으로 코어 스킬팩과 로컬 프로젝트 파일의 경계를 더 명확히 정리
- 각 skill의 reference 문서와 example 보강
- JSON 스키마 세부화
- 기존 코드 구조와 새 문서 구조의 대응 관계 정리

### 막힌 이슈 / 확인된 문제

- 기존 Python 파이프라인은 새 workflow 구조와 완전히 일치하지 않음
- S3, S4, S5 프롬프트 템플릿은 JSON 예시 중괄호가 escape되지 않아 `str.format()` 오류 가능성이 있음
- `outputs/`에는 최근 성공 실행 결과가 명확히 남아 있지 않음
- 기본 LLM 클라이언트 선택 동작과 테스트 기대값이 일부 어긋남

## 현재 문서 기준 단계 구조

| 구간 | 단계 | 상태 | 비고 |
|---|---|---|---|
| Loop A | 연구 서치 | 문서화됨 | 연구자 승인까지 반복 |
| Loop B-1 | Gap 및 가설 제시 | 문서화됨 | 연구자 승인까지 반복 |
| Loop B-2 | 실험 디자인 | 문서화됨 | 승인된 가설 기준 |
| Loop B-3 | 시뮬레이션 및 결과 예측 | 문서화됨 | 실패 시 이전 단계 복귀 |
| Support | 메트릭 집계 | 문서화됨 | 정규화 JSON 기준 요약 |

## 최근 점검 내용

### 확인한 파일

- `CLAUDE.md`
- `RAP_PROJECT_PROFILE.json`
- `claude/project/PROJECT_GUIDE.md`
- `claude/project/PIPELINE_START.md`
- `claude/project/EXECUTION_PROMPT_TEMPLATE.md`
- `run_logging.md`
- `pipeline/config.py`
- `pipeline/llm.py`
- `run_pipeline.py`

### 테스트 결과

- 최근 확인 명령: `pytest -q`
- 최근 확인 결과: 28개 통과, 16개 실패

### 주요 실패 구간

- `tests/test_s3_screen.py`
- `tests/test_s4_gap.py`
- `tests/test_s5_hypothesis.py`
- `tests/test_pipeline_integration.py`
- `tests/test_llm.py`
- `tests/test_s6_experiment.py`

## 다음 권장 작업

1. 코어 skillpack을 독립 저장소 또는 배포 단위로 분리하는 디렉터리 구조 설계
2. 프로젝트 로컬 파일만 남기는 최소 구조 정의
3. 각 skill별 example JSON 샘플 보강
4. 실제 Claude Code 실행용 프롬프트와 로컬 프로필 사용 예시 추가
5. 의미 있는 코드 수정 또는 문서 구조 변경 이후 이 로그 문서를 계속 업데이트

## 작업 기록

### 2026-04-08

- 변경 내용:
  - 프로젝트를 Claude Code용 Markdown 지침 및 skill 중심 구조로 재정의
  - workflow 변경사항을 반영해 승인 루프 중심 구조로 재정리
  - search loop, gap-hypothesis loop, simulation 단계와 정규화 JSON 스키마 문서 추가
  - 각 skill별 example JSON 샘플 및 workflow SVG 시각화 추가
  - Claude Code에서 바로 사용할 수 있는 상위 실행 프롬프트 템플릿 추가
  - 짧은 호출을 지원하기 위한 `PIPELINE_START.md` 부트스트랩 문서 추가
  - 첫 진입용 `search_cycle_input.json` 초안 추가
  - 시작 호출 이름을 `rap-pipeline`으로 고정
  - `rap-pipeline 시작` 호출 시 단계 선택지를 먼저 제시하도록 수정
- 수정 파일:
  - `CLAUDE.md`
  - `claude/project/PROJECT_GUIDE.md`
  - `claude/project/PIPELINE_START.md`
  - `claude/project/EXECUTION_PROMPT_TEMPLATE.md`
  - `claude/workflows/rap-workflow.md`
  - `claude/skills/rap-orchestrator/SKILL.md`
  - `claude/skills/rap-search-cycle/SKILL.md`
  - `claude/skills/rap-gap-hypothesis-cycle/SKILL.md`
  - `claude/skills/rap-experiment-design/SKILL.md`
  - `claude/skills/rap-simulation-prediction/SKILL.md`
  - `claude/skills/rap-metrics-tracking/SKILL.md`
  - `search_cycle_input.json`
  - `run_logging.md`
- 검증:
  - 변경된 workflow가 상위 지침과 skill 구조에 반영되었는지 수동 검토
- 결과:
  - Claude Code가 읽을 수 있는 승인 루프 중심 문서 레이어가 생성됨
- 다음 단계:
  - 각 skill별 example JSON 샘플 추가 및 실제 운영 프롬프트 정리

### 2026-04-08 20:30

- 변경 내용:
  - 문서 기반 전체 파이프라인 스모크 테스트 수행
  - 샘플 입출력을 `outputs/2026-04-08_docflow_smoketest/`에 구성
  - metrics example의 candidate paper count를 실제 샘플과 일치하도록 수정
- 수정 파일:
  - `claude/skills/rap-metrics-tracking/references/example-weekly-metrics.json`
  - `run_logging.md`
- 검증:
  - 샘플 JSON 전체 파싱 확인
  - 단계 간 참조 일관성 확인
  - 검증 결과: `JSON_PARSE_OK`, `CONSISTENCY_OK`
- 결과:
  - search → gap/hypothesis → experiment design → simulation → metrics 흐름이 샘플 JSON 기준으로 끝까지 연결됨
- 다음 단계:
  - 실제 사용자 주제로 `search_cycle_input.json`을 채워 첫 실운영 run 시작

### 2026-04-08 20:40

- 변경 내용:
  - 루트 `search_cycle_input.json`을 실운영 첫 초안으로 갱신
  - 현재 프로젝트 방향에 맞춰 human-in-the-loop 연구 자동화 워크플로우 주제로 초기 입력 구성
- 수정 파일:
  - `search_cycle_input.json`
  - `run_logging.md`
- 검증:
  - JSON 형식 수동 확인
- 결과:
  - `rap-pipeline 연구 서치 시작`에 바로 사용할 수 있는 초기 입력 초안 준비 완료
- 다음 단계:
  - Claude Code에서 `rap-pipeline 시작` 또는 `rap-pipeline 연구 서치 시작` 호출 후 첫 search iteration 진행

### 2026-04-08 20:45

- 변경 내용:
  - 실운영 주제를 `Rapid fNIRS decoding`으로 변경
  - 검색 키워드, 목표, 제약조건을 fNIRS decoding 문맥에 맞게 갱신
- 수정 파일:
  - `search_cycle_input.json`
  - `run_logging.md`
- 검증:
  - JSON 형식 수동 확인
- 결과:
  - `rap-pipeline 연구 서치 시작`에 사용할 실제 주제 입력이 rapid fNIRS decoding으로 반영됨
- 다음 단계:
  - Claude Code에서 `rap-pipeline 연구 서치 시작` 호출 후 첫 search iteration 진행

### 2026-04-08 21:00

- 변경 내용:
  - 하이브리드 구조 구현 시작
  - 프로젝트 로컬 프로필 `RAP_PROJECT_PROFILE.json` 추가
  - 코어 skillpack과 로컬 프로젝트 설정의 역할 분리를 문서에 반영
- 수정 파일:
  - `CLAUDE.md`
  - `RAP_PROJECT_PROFILE.json`
  - `claude/project/PROJECT_GUIDE.md`
  - `claude/project/PROJECT_PROFILE_SCHEMA.md`
  - `claude/project/PIPELINE_START.md`
  - `claude/project/EXECUTION_PROMPT_TEMPLATE.md`
  - `search_cycle_input.json`
  - `run_logging.md`
- 검증:
  - 문서 간 참조 경로 수동 확인
- 결과:
  - 전역 `rap-pipeline` 코어와 로컬 프로젝트 프로필을 분리하는 첫 구현이 반영됨
- 다음 단계:
  - 코어 skillpack 독립 배포를 위한 디렉터리 분리 설계

### 2026-04-08 21:10

- 변경 내용:
  - 코어 skillpack 초안 디렉터리 `skillpacks/rap-pipeline-core/` 생성
  - 기존 로컬 코어 초안 문서와 skill을 배포용 구조로 복제
  - 프로젝트 로컬 프로필이 새 코어 경로를 바라보도록 갱신
- 수정 파일:
  - `skillpacks/rap-pipeline-core/manifest.json`
  - `skillpacks/rap-pipeline-core/skills/*`
  - `skillpacks/rap-pipeline-core/references/*`
  - `skillpacks/rap-pipeline-core/templates/*`
  - `RAP_PROJECT_PROFILE.json`
  - `CLAUDE.md`
  - `claude/project/PROJECT_GUIDE.md`
  - `claude/project/PROJECT_PROFILE_SCHEMA.md`
  - `run_logging.md`
- 검증:
  - 배포용 코어 디렉터리와 manifest 경로 수동 확인
- 결과:
  - 코어 skillpack을 별도 저장소 또는 배포 단위로 분리할 수 있는 첫 패키지 구조가 저장소 안에 마련됨
- 다음 단계:
  - 로컬 `claude/` 복사본을 점진적으로 배포용 코어 경로 기준으로 정리
### 2026-04-08 22:15

- 변경 내용:
  - Claude user-level local marketplace `rap-pipeline-local` created at `C:\Users\sungw\.claude\plugins\marketplaces\rap-pipeline-local`
  - Global plugin `rap-pipeline` installed into that marketplace with plugin manifest and 7 RAP skills
  - User-level Claude settings updated to register the marketplace and enable `rap-pipeline@rap-pipeline-local`
  - Added a bootstrap skill named `rap-pipeline` so `rap-pipeline 시작` is a direct global invocation phrase
- 수정 파일:
  - `C:\Users\sungw\.claude\settings.json`
  - `C:\Users\sungw\.claude\plugins\marketplaces\rap-pipeline-local\.claude-plugin\marketplace.json`
  - `C:\Users\sungw\.claude\plugins\marketplaces\rap-pipeline-local\plugins\rap-pipeline\.claude-plugin\plugin.json`
  - `C:\Users\sungw\.claude\plugins\marketplaces\rap-pipeline-local\plugins\rap-pipeline\skills\*`
- 검증:
  - JSON parse check passed for user settings, marketplace manifest, and plugin manifest
  - Required path existence check passed
  - Fresh `claude` process confirmed:
    - `Found 2 plugins (2 enabled, 0 disabled)`
    - `Loaded 7 skills from plugin rap-pipeline default directory`
    - `Skill prompt: showing "rap-pipeline:rap-pipeline"`
    - `SkillTool returning 2 newMessages for skill rap-pipeline:rap-pipeline`
- 참고:
  - The first verification run happened before the new marketplace finished reconciling, so `rap-pipeline` was missing on that first process only
  - The second fresh process loaded the plugin successfully from startup
  - Existing Gmail and Google Calendar MCP authentication warnings were unrelated to `rap-pipeline`
## 2026-04-08 - Fix `rap-pipeline 시작` auto-search

- Symptom: `rap-pipeline 시작` immediately moved into literature search for the current topic instead of asking for the start stage.
- Root cause: the bootstrap entry skill could read enough project context to infer the search stage before asking the stage-selection question.
- Fix:
  - patched the installed global bootstrap skill at `C:\Users\sungw\.claude\plugins\marketplaces\rap-pipeline-local\plugins\rap-pipeline\skills\rap-pipeline\SKILL.md`
  - patched the distributable bootstrap skill at `distribution/rap-pipeline-local/plugins/rap-pipeline/skills/rap-pipeline/SKILL.md`
  - added the same hard gate to `CLAUDE.md` and `claude/project/PIPELINE_START.md`
- New rule:
  - exact invocation `rap-pipeline 시작` must always present the stage choices first
  - it must not infer the stage from `search_cycle_input.json`, `RAP_PROJECT_PROFILE.json`, or prior run state
  - it must not begin search until the user explicitly chooses `연구 서치 시작`
- Verification:
  - reran `claude -p --max-turns 2 --debug-file C:\Users\sungw\Exp_Auto_Pipeline\tmp_claude_rap_debug_third.log "rap-pipeline 시작"`
  - confirmed bootstrap skill `rap-pipeline:rap-pipeline` loaded
  - found no `search_cycle_input.json` access and no `rapid fNIRS decoding` search kickoff in the debug log
## 2026-04-08 - Restore pipeline test suite

- Fixed prompt-template formatting failures in `pipeline/prompts/s3_screen.md`, `pipeline/prompts/s4_gap.md`, and `pipeline/prompts/s5_hypothesis.md` by escaping JSON examples for `str.format()`.
- Updated `pipeline/prompts/s6_experiment.md` and `pipeline/stages/s6_experiment.py` so the experiment-design prompt carries explicit hypothesis field names (`hypothesis`, `independent_var`, `dependent_var`, `expected_relation`).
- Simplified `pipeline.llm.get_client()` so `provider="claude"` returns `ClaudeClient`, while `provider="claude-cli"` explicitly selects `ClaudeCLIClient`.
- Verification: `pytest -q` now passes fully (`44 passed`).
## 2026-04-09 - Normalize JSON contracts across all RAP stages

- Refined the search-cycle, gap-hypothesis, experiment-design, simulation-prediction, and metrics-tracking JSON contracts to use a more consistent structure.
- Search-cycle updates:
  - added `project_profile_ref`, `preferred_sources`, `year_range`, `exclusion_rules`, `status`, and `notes` to input
  - added `sources`, `doi`, `url`, `matched_queries`, and `screening_note` to output
  - added `priority` and broader `target` values to feedback
- Gap-hypothesis updates:
  - added richer approved-paper metadata and `analysis_focus` to input
  - added `type` and `priority` to feedback
  - added `gap_type`, `significance`, `open_questions`, `rationale`, `control_variables`, `novelty_score`, and `testability_notes` to output
- Experiment-design updates:
  - added `project_profile_ref`, richer hypothesis metadata, `design_goals`, `constraints`, `status`, and `notes` to input
  - added `dataset_plan`, structured metric/test entries, `artifact_plan`, and `status` to output
- Simulation-prediction updates:
  - added `project_profile_ref`, `simulation_goal`, data-source availability, `success_criteria`, `status`, and `notes` to input
  - added `experiment_design_output_ref` and `next_actions` to output
- Metrics updates:
  - added `overall_status`, `active_stage`, `blockers`, and `notes`
- Synced both local `claude/` references and distributable `skillpacks/rap-pipeline-core/` references.
- Verification:
  - all updated example JSON files parsed successfully
  - `pytest -q` passed (`44 passed`)
