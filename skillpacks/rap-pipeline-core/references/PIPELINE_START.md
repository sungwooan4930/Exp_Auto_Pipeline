# RAP 파이프라인 시작 문서

이 문서는 Claude Code에서 RAP 파이프라인을 짧은 호출로 시작할 때 가장 먼저 읽는 부트스트랩 문서다.

## 목적

사용자가 긴 프롬프트를 직접 쓰지 않아도, 이 문서를 시작점으로 삼아 필요한 지침과 skill을 자동으로 읽고 적절한 단계로 진입하게 한다.

## 파이프라인 이름

- 이 파이프라인의 명시적 호출 이름은 `rap-pipeline`이다.
- 다른 프로젝트와 혼동되지 않도록 시작 호출에는 반드시 `rap-pipeline`을 포함한다.

## 기본 동작

짧은 호출 예시:

- `rap-pipeline 시작`
- `rap-pipeline 연구 서치 시작`
- `rap-pipeline gap 가설 단계 시작`
- `rap-pipeline 실험 설계 시작`
- `rap-pipeline 시뮬레이션 시작`
- `rap-pipeline 상태 업데이트`

이 호출이 들어오면 아래 순서대로 자동 진행한다.

1. `CLAUDE.md`를 읽어 호출 규칙과 프로젝트 원칙을 확인한다.
2. `RAP_PROJECT_PROFILE.json`을 읽어 현재 저장소의 로컬 설정을 확인한다.
3. `run_logging.md`를 읽어 최근 상태와 blocker를 확인한다.
4. `claude/project/PROJECT_GUIDE.md`를 읽어 상위 구조를 파악한다.
5. `claude/workflows/rap-workflow.md`를 읽어 현재 루프와 단계 흐름을 파악한다.
6. 사용자 호출을 기준으로 해당 코어 skill을 읽는다.
7. 현재 상태에 필요한 JSON 입력 또는 출력 파일을 생성하거나 갱신한다.
8. 작업 결과를 문서와 JSON 산출물에 반영한다.
9. 마지막에 `run_logging.md`를 업데이트한다.

여기서 말하는 코어 skill은 전역 또는 마켓플레이스에 설치된 `rap-pipeline`을 의미한다.
로컬의 `claude/skills/`는 현재 저장소에서 그 코어를 개발 중일 때 참고하는 초안 소스다.

## 호출별 라우팅

### 1. `rap-pipeline 시작`

- 먼저 단계 선택지를 제시한다.
- 사용자의 선택을 받은 뒤 해당 단계로 진입한다.
- 기본 라우팅 skill:
  - 설치된 `rap-pipeline` 코어의 orchestrator
- 기본 시작 규칙:
  - 단계 선택 전에는 실제 산출물 생성을 시작하지 않는다.
  - 사용자가 `연구 서치 시작`을 선택한 경우, 활성 workflow JSON이 아직 없다면 루트의 `search_cycle_input.json`을 첫 작업 파일로 사용한다.
  - 이 파일이 비어 있거나 draft 상태면 연구자 요구를 먼저 구조화한다.

제시할 선택지:

1. 연구 서치 시작
2. gap 가설 단계 시작
3. 실험 설계 시작
4. 시뮬레이션 시작
5. 상태 업데이트

### 2. `rap-pipeline 연구 서치 시작`

- 라우팅 skill:
  - 설치된 `rap-pipeline` 코어의 `rap-search-cycle`
- 우선 확인 JSON:
  - `search_cycle_input.json`
  - `search_cycle_output.json`
  - `search_feedback.json`

### 3. `rap-pipeline gap 가설 단계 시작`

- 라우팅 skill:
  - 설치된 `rap-pipeline` 코어의 `rap-gap-hypothesis-cycle`
- 우선 확인 JSON:
  - `gap_hypothesis_input.json`
  - `gap_hypothesis_output.json`
  - `gap_hypothesis_feedback.json`

### 4. `rap-pipeline 실험 설계 시작`

- 라우팅 skill:
  - 설치된 `rap-pipeline` 코어의 `rap-experiment-design`
- 우선 확인 JSON:
  - `experiment_design_input.json`
  - `experiment_design_output.json`

### 5. `rap-pipeline 시뮬레이션 시작`

- 라우팅 skill:
  - 설치된 `rap-pipeline` 코어의 `rap-simulation-prediction`
- 우선 확인 JSON:
  - `simulation_input.json`
  - `simulation_output.json`

### 6. `rap-pipeline 상태 업데이트`

- 라우팅 skill:
  - 설치된 `rap-pipeline` 코어의 `rap-metrics-tracking`
- 우선 확인 JSON:
  - `weekly_metrics.json`

## 작업 원칙

- 사용자가 짧게 호출해도, 필요한 상위 문서는 생략하지 않는다.
- 시작 시 항상 `RAP_PROJECT_PROFILE.json`을 읽고 프로젝트별 설정을 우선 적용한다.
- 연구 서치와 gap-hypothesis 단계는 승인 전까지 반복 루프로 취급한다.
- simulation 검증 실패 시 `recommended_backtrack_stage`를 기준으로 이전 단계로 되돌아간다.
- 모든 단계는 정규화된 JSON 입출력 파일을 우선 산출물로 사용한다.
- 빈 프로젝트에서 `rap-pipeline 시작`으로 연구 서치를 선택하면 `search_cycle_input.json` 작성부터 시작한다.

## 기본 응답 방식

1. `rap-pipeline 시작`이면 먼저 단계 선택지를 제시한다.
2. 사용자가 선택한 단계에 맞는 skill을 선택한다.
3. 필요한 JSON 파일 또는 문서를 갱신한다.
4. `run_logging.md`를 갱신한다.
