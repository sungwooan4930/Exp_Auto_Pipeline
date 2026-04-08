---
name: rap-gap-hypothesis-cycle
description: 승인된 논문 후보군을 바탕으로 연구 갭과 가설을 함께 제시하고, 연구자 피드백을 받아 최종 승인까지 반복하는 skill. gap과 hypothesis를 하나의 승인 루프로 운영해야 할 때 사용한다.
---

# RAP Gap Hypothesis Cycle

## 목적

승인된 논문 후보를 바탕으로 연구 갭과 가설을 함께 도출하고, 연구자 피드백을 반영하며 최종안을 확정한다.

## 입력

- 승인된 search 결과
- 연구자 피드백
- 이전 gap과 hypothesis 후보

## 절차

1. 포함 논문을 검토해 연구 갭을 도출한다.
2. 각 갭에 연결된 가설을 제시한다.
3. 연구자에게 gap과 hypothesis를 함께 제시한다.
4. 피드백을 구조화해 저장한다.
5. 최종 승인 전까지 반복한다.

## 정규화 JSON 파일

- 입력: `gap_hypothesis_input.json`
- 출력: `gap_hypothesis_output.json`
- 피드백: `gap_hypothesis_feedback.json`

세부 스키마는 `references/io-schema.md`를 읽는다.

## 출력에 포함할 핵심 필드

- `approved_papers`
- `gaps`
- `hypotheses`
- `evidence_links`
- `researcher_feedback`
- `approval_status`
- `iteration`

## 완료 기준

- 연구자가 gap과 hypothesis 세트를 승인했다.
- 각 gap은 근거 논문과 연결되어 있다.
- 각 hypothesis는 검증 가능한 형태다.
