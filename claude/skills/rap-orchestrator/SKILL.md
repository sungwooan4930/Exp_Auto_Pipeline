---
name: rap-orchestrator
description: RAP 프로젝트 전체 흐름을 Claude Code 기준으로 운영할 때 사용하는 오케스트레이션 skill. 연구 서치 루프와 gap-가설-실험-시뮬레이션 루프 사이에서 현재 단계 선택, input/output 확인, run_logging.md 갱신이 필요할 때 사용한다.
---

# RAP Orchestrator

## 언제 사용하나

- RAP 작업을 처음 시작할 때
- 현재 어떤 루프와 단계부터 진행해야 할지 판단해야 할 때
- 여러 단계 산출물을 이어서 정리해야 할 때
- `run_logging.md`를 갱신해야 할 때

## 시작 절차

1. `CLAUDE.md`를 읽는다.
2. `claude/project/PROJECT_GUIDE.md`를 읽는다.
3. `run_logging.md`를 읽는다.
4. `claude/workflows/rap-workflow.md`를 읽는다.
5. 지금 작업이 어느 단계인지 판단한다.
6. 해당 단계 skill의 `SKILL.md`를 읽는다.

## 단계 선택 기준

- 연구자 요구 기반 논문 탐색과 피드백 반복이 필요하면 `rap-search-cycle`
- gap과 hypothesis를 함께 제시하고 승인 루프를 돌려야 하면 `rap-gap-hypothesis-cycle`
- 승인된 가설을 바탕으로 실험 구조를 잡아야 하면 `rap-experiment-design`
- 실제 데이터 또는 가상 데이터 기반 검증과 결과 예측이 필요하면 `rap-simulation-prediction`
- 진행 수치와 상태를 집계해야 하면 `rap-metrics-tracking`

## 출력 원칙

- 각 단계마다 입력, 절차, 산출물, 완료 기준을 분리해서 정리한다.
- 모든 단계의 input/output는 정규화 JSON 파일로 저장한다.
- 중요 변경이나 blocker는 `run_logging.md`에 즉시 반영한다.
