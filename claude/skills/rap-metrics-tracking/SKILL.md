---
name: rap-metrics-tracking
description: RAP 각 단계의 정규화 JSON 산출물을 바탕으로 진행 상태와 핵심 지표를 요약하는 skill. weekly_metrics.json 또는 진행 로그를 갱신해야 할 때 사용한다.
---

# RAP Metrics Tracking

## 입력

- 단계별 JSON 산출물 전체

## 해야 할 일

1. search iteration 수와 승인 상태를 집계한다.
2. 승인된 논문 후보 수를 집계한다.
3. gap 수와 hypothesis 수를 집계한다.
4. 실험 설계 및 시뮬레이션 결과 상태를 요약한다.
5. 필요하면 run id와 timestamp를 기록한다.

## 산출물

- `weekly_metrics.json`
- 필요시 `run_logging.md` 상태 갱신

세부 스키마와 예시는 `references/` 아래 문서를 읽는다.

## 완료 기준

- 핵심 수치가 빠지지 않는다.
- 단계별 산출물과 숫자가 일치한다.
- 후속 회고나 비교에 사용할 수 있다.
