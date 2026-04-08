# NotebookLM Prompt

아래 프롬프트를 NotebookLM에 그대로 넣어 RAP 워크플로우 다이어그램 생성을 요청하면 된다.

```text
RAP 프로젝트의 최신 워크플로우를 한 장의 깔끔한 프로세스 다이어그램으로 시각화해줘.

반드시 다음 구조를 반영해줘.

1. 워크플로우는 크게 2개의 루프로 나뉜다.
- Loop A: 연구 서치 루프
- Loop B: 연구 아이디어 구체화 및 검증 루프

2. Loop A의 흐름
- 연구자 요구 입력
- 논문 탐색
- 탐색 결과 제시
- 연구자 피드백 수집
- 피드백 반영 후 재탐색
- 연구자 최종 승인까지 반복

3. Loop B의 흐름
- Gap 제시 및 가설 제시
- 연구자 피드백 반영
- 연구자 최종 승인까지 반복
- 실험 디자인 제시
- 실제 데이터 또는 가상 데이터 기반 시뮬레이션
- 결과 예측 및 검증

4. 복귀 규칙
- 시뮬레이션 또는 검증 실패 시 필요에 따라 아래 두 경로 중 하나로 되돌아갈 수 있어야 한다.
  - Gap/Hypothesis 단계로 복귀
  - Experiment Design 단계로 복귀

5. 다이어그램에서 꼭 표현할 요소
- Loop A와 Loop B를 큰 영역 또는 swimlane처럼 구분
- 연구자 승인 전까지 반복되는 피드백 루프
- Gap과 Hypothesis가 하나의 묶음 단계라는 점
- 모든 단계가 정규화된 JSON input/output를 가진다는 점

6. 함께 표기하면 좋은 JSON 파일 예시
- search_cycle_input.json
- search_cycle_output.json
- search_feedback.json
- gap_hypothesis_input.json
- gap_hypothesis_output.json
- gap_hypothesis_feedback.json
- experiment_design_input.json
- experiment_design_output.json
- simulation_input.json
- simulation_output.json

7. 원하는 시각 스타일
- 발표 자료용으로 깔끔하고 구조가 한눈에 보이게
- 노션 스타일처럼 미니멀한 톤
- Loop A는 옅은 노란색 강조
- Loop B는 중립적인 화이트/그레이 톤
- 복귀 화살표는 눈에 띄게 강조

최종 결과는 한국어 라벨을 사용한 다이어그램 설명 또는 그림 생성용 구조로 정리해줘.
```
