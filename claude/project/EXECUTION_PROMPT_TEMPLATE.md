# Claude Code 상위 실행 프롬프트 템플릿

이 문서는 Claude Code에서 RAP 프로젝트를 실행할 때 바로 붙여 넣을 수 있는 상위 프롬프트 템플릿 모음이다.

## 0. 가장 간단한 호출

앞으로는 아래처럼 짧게 호출해도 된다.

```text
rap-pipeline 시작
```

또는

```text
rap-pipeline 연구 서치 시작
```

이 경우 Claude Code는 `CLAUDE.md`의 빠른 시작 규칙과 `claude/project/PIPELINE_START.md`를 기준으로 자동으로 관련 문서를 읽고 적절한 단계로 진입해야 한다.

`rap-pipeline 시작`이 들어오면 첫 액션은 바로 실행이 아니라 단계 선택지를 제시하는 것이다.

선택지:
1. 연구 서치 시작
2. gap 가설 단계 시작
3. 실험 설계 시작
4. 시뮬레이션 시작
5. 상태 업데이트

이후 사용자가 `연구 서치 시작`을 선택하고 빈 상태라면 첫 액션은 루트의 `search_cycle_input.json`을 작성하거나 갱신하는 것이다.
또한 시작 시 항상 `RAP_PROJECT_PROFILE.json`을 먼저 읽어 현재 저장소의 주제와 파일 경로를 반영해야 한다.

## 1. 기본 오케스트레이션 템플릿

```text
RAP 프로젝트 작업을 시작해.

반드시 아래 순서대로 진행해.

1. `CLAUDE.md`를 읽고 현재 프로젝트 운영 원칙을 이해해.
2. `RAP_PROJECT_PROFILE.json`을 읽고 현재 프로젝트의 로컬 설정을 확인해.
3. `claude/project/PROJECT_GUIDE.md`를 읽고 상위 workflow를 파악해.
4. `claude/workflows/rap-workflow.md`를 읽고 현재 작업이 어느 루프와 단계에 속하는지 판단해.
5. `run_logging.md`를 읽고 최근 상태, blocker, 마지막 작업 내용을 확인해.
6. 필요한 코어 skill 문서를 선택해서 읽어.
7. 현재 상태에서 가장 적절한 다음 작업을 수행해.
8. 작업 결과를 정규화된 JSON 산출물 또는 관련 문서에 반영해.
9. 작업이 끝나면 `run_logging.md`를 업데이트해.

작업 원칙:
- 연구 서치 단계는 연구자 최종 승인 전까지 반복 루프로 운영해.
- gap과 hypothesis는 하나의 승인 루프로 다뤄.
- simulation 검증 실패 시 필요하면 gap-hypothesis 단계 또는 experiment design 단계로 되돌아가.
- 모든 단계는 정규화된 JSON input/output를 기준으로 다뤄.
- 기존 Python 코드는 참고 구현으로 활용하되, 문서와 skill 체계를 우선해.

이번 실행의 목표:
[여기에 이번 작업 목표를 한 줄로 적기]
```

## 2. 연구 서치 루프 실행 템플릿

```text
RAP 프로젝트에서 연구 서치 루프를 진행해.

다음 문서를 먼저 읽어:
- `CLAUDE.md`
- `RAP_PROJECT_PROFILE.json`
- `claude/project/PROJECT_GUIDE.md`
- `claude/workflows/rap-workflow.md`
- 설치된 `rap-pipeline` 코어의 `rap-search-cycle`
- `run_logging.md`

해야 할 일:
1. 현재 연구자 요구를 구조화해.
2. `search_cycle_input.json` 기준 입력을 정리해.
3. 논문 탐색 전략과 후보 논문 목록을 만들어.
4. `search_cycle_output.json` 형식으로 결과를 정리해.
5. 연구자 피드백이 있으면 `search_feedback.json`에 반영할 수 있게 구조화해.
6. 승인 상태가 확정되지 않았다면 다음 반복을 준비해.
7. 작업 후 `run_logging.md`를 업데이트해.

이번 연구자 요구:
[여기에 요구사항 입력]
```

## 3. Gap 및 Hypothesis 승인 루프 실행 템플릿

```text
RAP 프로젝트에서 gap-hypothesis 승인 루프를 진행해.

다음 문서를 먼저 읽어:
- `CLAUDE.md`
- `RAP_PROJECT_PROFILE.json`
- `claude/project/PROJECT_GUIDE.md`
- `claude/workflows/rap-workflow.md`
- 설치된 `rap-pipeline` 코어의 `rap-gap-hypothesis-cycle`
- `run_logging.md`

해야 할 일:
1. 승인된 search 결과를 확인해.
2. `gap_hypothesis_input.json` 기준으로 입력을 정리해.
3. 근거 논문과 연결된 gap을 제시해.
4. 각 gap에 연결된 hypothesis를 제시해.
5. `gap_hypothesis_output.json` 형식으로 정리해.
6. 연구자 피드백 반영이 필요하면 다음 iteration을 준비해.
7. 작업 후 `run_logging.md`를 업데이트해.

이번 단계의 추가 지시:
[여기에 현재 focus 입력]
```

## 4. 실험 디자인 실행 템플릿

```text
RAP 프로젝트에서 experiment design 단계를 진행해.

다음 문서를 먼저 읽어:
- `CLAUDE.md`
- `RAP_PROJECT_PROFILE.json`
- `claude/project/PROJECT_GUIDE.md`
- `claude/workflows/rap-workflow.md`
- 설치된 `rap-pipeline` 코어의 `rap-experiment-design`
- `run_logging.md`

해야 할 일:
1. 승인된 gap-hypothesis 결과를 확인해.
2. `experiment_design_input.json` 기준 입력을 정리해.
3. 변수, 절차, 평가 지표, 통계 검정을 구조화해.
4. `experiment_design_output.json` 형식으로 결과를 정리해.
5. 필요하면 `experiment_design.md` 설명 문서도 작성해.
6. 작업 후 `run_logging.md`를 업데이트해.

이번 설계 목표:
[여기에 설계 목표 입력]
```

## 5. 시뮬레이션 및 결과 예측 실행 템플릿

```text
RAP 프로젝트에서 simulation-prediction 단계를 진행해.

다음 문서를 먼저 읽어:
- `CLAUDE.md`
- `RAP_PROJECT_PROFILE.json`
- `claude/project/PROJECT_GUIDE.md`
- `claude/workflows/rap-workflow.md`
- 설치된 `rap-pipeline` 코어의 `rap-simulation-prediction`
- `run_logging.md`

해야 할 일:
1. 승인된 experiment design 결과를 확인해.
2. 실제 데이터 또는 가상 데이터 사용 여부를 명확히 해.
3. `simulation_input.json` 기준으로 입력을 정리해.
4. 시뮬레이션 절차와 예상 결과를 구성해.
5. `simulation_output.json` 형식으로 결과를 정리해.
6. 검증 실패 시 `recommended_backtrack_stage`를 반드시 채워.
7. 작업 후 `run_logging.md`를 업데이트해.

이번 검증 조건:
[여기에 데이터/검증 조건 입력]
```

## 6. 메트릭 및 상태 업데이트 템플릿

```text
RAP 프로젝트의 현재 진행 상태를 정리해.

다음 문서를 먼저 읽어:
- `CLAUDE.md`
- `RAP_PROJECT_PROFILE.json`
- `claude/project/PROJECT_GUIDE.md`
- 설치된 `rap-pipeline` 코어의 `rap-metrics-tracking`
- `run_logging.md`

해야 할 일:
1. 현재 존재하는 JSON 산출물을 확인해.
2. `weekly_metrics.json` 형식으로 핵심 수치를 집계해.
3. 진행 단계, 승인 상태, blocker를 요약해.
4. `run_logging.md`를 최신 상태로 업데이트해.

이번 요약 목적:
[여기에 목적 입력]
```

## 7. 빠른 사용법

- 가장 간단한 시작: `rap-pipeline 시작`
- `rap-pipeline 시작`의 기본 동작: 단계 선택지 먼저 제시
- 전체 작업 시작: `기본 오케스트레이션 템플릿`
- search 반복: `연구 서치 루프 실행 템플릿`
- gap/hypothesis 반복: `Gap 및 Hypothesis 승인 루프 실행 템플릿`
- 설계 단계: `실험 디자인 실행 템플릿`
- 검증 단계: `시뮬레이션 및 결과 예측 실행 템플릿`
- 정리 단계: `메트릭 및 상태 업데이트 템플릿`
