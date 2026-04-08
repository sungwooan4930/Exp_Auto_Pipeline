# RAP 프로젝트 작업 지침

이 저장소는 RAP(Research Automation Pipeline)를 적용하는 프로젝트 작업 공간이다.

## 핵심 방향

이 프로젝트는 하이브리드 구조를 따른다.

- 전역 또는 마켓플레이스 코어 스킬팩:
  - `rap-pipeline`
- 프로젝트 로컬 설정:
  - `RAP_PROJECT_PROFILE.json`
  - `search_cycle_input.json`
  - `run_logging.md`
  - `outputs/`

기본 원칙:

- 공통 workflow, 단계 로직, JSON 규약은 코어 스킬팩 `rap-pipeline`이 담당한다.
- 현재 저장소는 프로젝트별 주제, 경로, 연구 선호 조건을 `RAP_PROJECT_PROFILE.json`에 둔다.
- 로컬의 `skillpacks/rap-pipeline-core/`는 현재 코어 스킬팩 초안을 개발하고 참조하는 소스로 취급한다.
- 로컬의 `claude/` 디렉터리는 전환 기간 동안 작업 복사본으로 유지한다.
- 실제 범용 사용 시에는 설치된 `rap-pipeline` 코어가 이 저장소의 `RAP_PROJECT_PROFILE.json`을 읽고 동작한다고 가정한다.

## 기준 문서

- `RAP_PROJECT_PROFILE.json`
- `run_logging.md`
- `search_cycle_input.json`
- `claude/project/PROJECT_GUIDE.md`
- `claude/project/PROJECT_PROFILE_SCHEMA.md`
- `claude/project/PIPELINE_START.md`
- `claude/project/EXECUTION_PROMPT_TEMPLATE.md`
- `claude/workflows/rap-workflow.md`

## 빠른 시작 규칙

이 프로젝트의 명시적 호출 이름은 `rap-pipeline`이다.
이 파이프라인을 시작하거나 특정 단계로 진입할 때는 반드시 `rap-pipeline`을 포함한 호출을 사용한다.

지원 호출:

- `rap-pipeline 시작`
- `rap-pipeline 연구 서치 시작`
- `rap-pipeline gap 가설 단계 시작`
- `rap-pipeline 실험 설계 시작`
- `rap-pipeline 시뮬레이션 시작`
- `rap-pipeline 상태 업데이트`

`rap-pipeline 시작`이 들어오면 바로 작업을 시작하지 말고 먼저 아래 선택지를 제시한다.

1. 연구 서치 시작
2. gap 가설 단계 시작
3. 실험 설계 시작
4. 시뮬레이션 시작
5. 상태 업데이트

위처럼 `rap-pipeline`이 명시된 호출이 들어오면 반드시 다음을 자동 수행한다.

1. `RAP_PROJECT_PROFILE.json` 확인
2. `run_logging.md` 확인
3. 현재 루프와 단계 판단
4. 관련 코어 skill 확인
5. 필요한 JSON 입출력 파일 생성 또는 갱신
6. 작업 후 `run_logging.md` 업데이트

## 작업 원칙

- 새 작업을 시작할 때 먼저 `RAP_PROJECT_PROFILE.json`을 읽고 프로젝트별 설정을 확인한다.
- 다음으로 `run_logging.md`를 읽고 현재 상태와 blocker를 확인한다.
- 전체 흐름은 `claude/project/PROJECT_GUIDE.md`와 `claude/workflows/rap-workflow.md`를 기준으로 판단한다.
- 단계별 작업은 대응되는 코어 skill 규칙을 따른다.
- 각 단계의 입력과 출력은 정규화된 JSON 파일로 저장한다.
- 기존 Python 코드는 참고 구현 또는 검증 자산으로 취급한다.

## 현재 코어 스킬 초안 위치

현재 저장소에서 코어 스킬팩 초안을 개발할 때 참고하는 로컬 경로:

- `skillpacks/rap-pipeline-core/manifest.json`
- `skillpacks/rap-pipeline-core/references/`
- `skillpacks/rap-pipeline-core/skills/`
- `skillpacks/rap-pipeline-core/templates/`

전환 기간 작업 복사본:

- `claude/skills/rap-orchestrator`
- `claude/skills/rap-search-cycle`
- `claude/skills/rap-gap-hypothesis-cycle`
- `claude/skills/rap-experiment-design`
- `claude/skills/rap-simulation-prediction`
- `claude/skills/rap-metrics-tracking`

## 문서 갱신 규칙

- 구조나 workflow에 major 변경이 있으면 `CLAUDE.md`, `RAP_PROJECT_PROFILE.json`, `claude/project/PROJECT_GUIDE.md`를 함께 갱신한다.
- 중요한 상태 변화가 있으면 `run_logging.md`에 기록한다.
- 프로젝트 로컬 설정과 코어 workflow 규칙이 어긋나지 않도록 유지한다.
## Hard Gate For `rap-pipeline 시작`

When the invocation is exactly `rap-pipeline 시작`, do not begin any stage automatically.

- Always ask which stage to start from first.
- Do not infer the stage from `search_cycle_input.json`.
- Do not infer the stage from the topic in `RAP_PROJECT_PROFILE.json`.
- Do not infer the stage from prior run state or existing draft files.
- Do not begin literature search until the user explicitly chooses `연구 서치 시작`.
