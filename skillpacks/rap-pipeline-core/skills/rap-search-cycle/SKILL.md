---
name: rap-search-cycle
description: 연구자의 요구를 바탕으로 논문을 탐색하고, 연구자 피드백을 반영해 재탐색을 반복하는 skill. 연구자가 최종 승인할 때까지 search 결과를 개선하는 workflow가 필요할 때 사용한다.
---

# RAP Search Cycle

## Search Quality Rules

Use the following criteria as real operating rules, not as optional advice.

### Do Not Do

- Do not search only for papers that support the expected hypothesis.
- Do not rely on a single database when multiple scholarly sources are available.
- Do not judge relevance from title alone when abstract-level evidence is available.
- Do not use only one narrow query variant.
- Do not keep irrelevant papers only because they look prestigious or recent.
- Do not silently change search scope without reflecting that change in the JSON artifacts.

### Good Search Means

- The search is aligned with the research question.
- The search strategy is explainable and reproducible.
- Queries cover both core concepts and close variants.
- Candidate papers are relevant enough for downstream gap analysis.
- Inclusion reasons are explicit.
- Feedback changes are visible across iterations.

### Required Evaluation Checklist

Before marking a search iteration as ready for approval, verify:

1. the domain, keywords, goals, and constraints are internally consistent
2. the search covers more than one query angle
3. the preferred sources are appropriate for the topic
4. the candidate set is not obviously biased toward only one expected conclusion
5. each candidate paper has a concrete inclusion reason
6. the result can be handed to the gap-hypothesis stage without major cleanup

## 목적

연구자 요구에 맞는 논문 후보군을 찾고, 피드백을 반영해 검색 결과를 반복 개선한다.

## 입력

- 연구자 요구
- 도메인
- 키워드
- 실험 유형 또는 관심 문제
- 이전 search 결과
- 이전 피드백

## 절차

1. 연구자 요구를 구조화한다.
2. 검색 전략과 쿼리를 만든다.
3. 관련 논문 후보를 제시한다.
4. 연구자 피드백을 구조화해 기록한다.
5. 피드백을 반영해 다시 탐색한다.
6. 연구자가 최종 승인할 때까지 반복한다.

## 정규화 JSON 파일

- 입력: `search_cycle_input.json`
- 출력: `search_cycle_output.json`
- 피드백: `search_feedback.json`

세부 스키마는 `references/io-schema.md`를 읽는다.

## 출력에 포함할 핵심 필드

- `request`
- `search_strategy`
- `queries`
- `candidate_papers`
- `researcher_feedback`
- `approval_status`
- `iteration`

## 완료 기준

- 연구자가 검색 결과를 승인했다.
- 승인된 논문 후보군이 다음 단계 입력으로 바로 사용 가능하다.
- 반복 기록과 피드백 반영 흔적이 JSON에 남아 있다.
