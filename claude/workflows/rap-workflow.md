# RAP 워크플로우

## 목적

Claude Code가 RAP 프로젝트를 문서 기반으로 수행할 때 따라야 하는 실행 순서를 정의한다.

## 전체 구조

이 workflow는 다음 2개의 큰 루프로 이루어진다.

### 1. 연구 서치 루프

흐름:

1. 연구자 요구 정리
2. 논문 탐색
3. 결과 제시
4. 연구자 피드백 수집
5. 피드백 반영 후 재탐색
6. 연구자 최종 승인까지 반복

사용 skill:

- `claude/skills/rap-search-cycle/SKILL.md`

### 2. 연구 아이디어 구체화 및 검증 루프

흐름:

1. Gap 제시 및 가설 제시
2. 연구자 피드백 반영
3. 연구자 최종 승인까지 반복
4. 실험 디자인 제시
5. 실제 데이터 또는 가상 데이터 기반 시뮬레이션
6. 결과 예측 및 검증
7. 실패 시 필요에 따라 1단계 또는 4단계로 복귀

사용 skill:

- `claude/skills/rap-gap-hypothesis-cycle/SKILL.md`
- `claude/skills/rap-experiment-design/SKILL.md`
- `claude/skills/rap-simulation-prediction/SKILL.md`

## 작업 시작 순서

1. `CLAUDE.md`를 읽는다.
2. `claude/project/PROJECT_GUIDE.md`를 읽는다.
3. `run_logging.md`를 읽는다.
4. 현재 작업이 어느 루프, 어느 단계인지 판단한다.
5. 해당 skill 문서를 읽고 실행한다.

## 공통 입출력 원칙

- 각 단계의 입력과 출력은 정규화된 JSON 파일로 저장한다.
- 각 반복은 별도의 iteration 정보를 포함한다.
- 연구자 피드백은 반드시 구조화해 다음 입력으로 넘긴다.

## 공통 산출물 예시

- `search_cycle_input.json`
- `search_cycle_output.json`
- `search_feedback.json`
- `gap_hypothesis_input.json`
- `gap_hypothesis_output.json`
- `gap_hypothesis_feedback.json`
- `experiment_design_input.json`
- `experiment_design_output.json`
- `simulation_input.json`
- `simulation_output.json`
- `weekly_metrics.json`

## 운영 원칙

- 한 단계가 끝나면 산출물 형식과 완료 기준을 확인한다.
- 다음 단계는 이전 단계 산출물을 입력으로 사용한다.
- 실패하거나 정보가 불충분하면 정의된 이전 단계로 되돌아간다.
- 단계별 결정 근거를 가능한 한 구조화된 형태로 남긴다.
