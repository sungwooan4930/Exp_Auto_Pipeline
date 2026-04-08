---
name: rap-experiment-design
description: 승인된 연구 가설을 검증하기 위한 실험 계획을 구조화하는 skill. experiment design을 정규화된 JSON으로 만들고, 필요하면 Markdown 설명으로 확장해야 할 때 사용한다.
---

# RAP Experiment Design

## 입력

- 승인된 `gap_hypothesis_output.json`

## 해야 할 일

1. 연구 개요와 목적을 정리한다.
2. 독립변수, 종속변수, 통제변수를 정의한다.
3. 실험 절차를 단계별로 적는다.
4. 평가 지표와 통계 검정을 명시한다.
5. 예상 결과와 한계를 적는다.

## 정규화 JSON 파일

- 입력: `experiment_design_input.json`
- 출력: `experiment_design_output.json`
- 선택적 설명 문서: `experiment_design.md`

세부 스키마는 `references/io-schema.md`를 읽는다.

## 출력에 포함할 핵심 필드

- `selected_hypotheses`
- `variables`
- `controls`
- `procedure`
- `evaluation_metrics`
- `statistical_tests`
- `expected_outcomes`
- `risks_and_limitations`

## 완료 기준

- 제3자가 읽고 실험 재현 흐름을 이해할 수 있다.
- 변수, 절차, 평가 지표가 빠지지 않는다.
- 가설과 실험 설계의 연결이 분명하다.
