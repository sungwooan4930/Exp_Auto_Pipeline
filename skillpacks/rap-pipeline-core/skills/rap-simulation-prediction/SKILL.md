---
name: rap-simulation-prediction
description: 승인된 실험 설계를 바탕으로 실제 데이터 또는 가상 데이터로 시뮬레이션을 구성하고 결과를 예측하는 skill. 검증 실패 시 gap/hypothesis 또는 experiment design 단계로 되돌아갈 판단이 필요할 때 사용한다.
---

# RAP Simulation Prediction

## 목적

실험 설계가 실제로 검증 가능한지 확인하고, 실제 데이터 또는 가상 데이터를 사용해 예상 결과를 구조화한다.

## 입력

- `experiment_design_output.json`
- 실제 데이터 또는 가상 데이터 설정

## 절차

1. 사용할 데이터 소스를 명확히 한다.
2. 실제 데이터가 없으면 가상 데이터 생성 규칙을 정한다.
3. 실험 절차를 시뮬레이션 가능 형태로 바꾼다.
4. 예상 결과와 실패 조건을 정리한다.
5. 검증 실패 시 원인을 분석한다.
6. 필요하면 gap/hypothesis 단계 또는 experiment design 단계로 복귀를 제안한다.

## 정규화 JSON 파일

- 입력: `simulation_input.json`
- 출력: `simulation_output.json`

세부 스키마는 `references/io-schema.md`를 읽는다.

## 출력에 포함할 핵심 필드

- `data_mode`
- `data_sources`
- `simulation_setup`
- `predicted_results`
- `validation_result`
- `failure_analysis`
- `recommended_backtrack_stage`

## 완료 기준

- 실제 데이터 또는 가상 데이터 기반 검증 흐름이 명시되어 있다.
- 결과 예측이 구조화되어 있다.
- 실패 시 되돌아갈 단계가 분명히 제시된다.
