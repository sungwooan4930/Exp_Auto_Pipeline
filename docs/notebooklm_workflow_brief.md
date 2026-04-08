# RAP Workflow Brief for NotebookLM

## 목적

이 문서는 NotebookLM이 RAP 프로젝트의 최신 워크플로우를 시각화할 때 참고할 수 있도록 만든 요약본이다.

## 프로젝트 한 줄 설명

연구자의 요구를 받아 논문 탐색을 반복하고, 승인된 논문 집합을 바탕으로 gap과 hypothesis를 구체화한 뒤, 실험 설계와 시뮬레이션으로 검증하는 human-in-the-loop 연구 자동화 워크플로우.

## 핵심 구조

워크플로우는 크게 2개의 루프로 구성된다.

### Loop A. 연구 서치 루프

목적:
- 연구자의 요구에 맞는 논문 후보군을 찾고, 연구자 피드백을 반영해 최종 승인된 논문 집합을 만든다.

흐름:
1. 연구자 요구 입력
2. 논문 탐색
3. 탐색 결과 제시
4. 연구자 피드백 수집
5. 피드백 반영 후 재탐색
6. 연구자 최종 승인까지 반복

핵심 특징:
- human-in-the-loop
- 승인 전까지 반복
- 각 반복은 JSON 파일로 저장

주요 JSON:
- `search_cycle_input.json`
- `search_cycle_output.json`
- `search_feedback.json`

### Loop B. 연구 아이디어 구체화 및 검증 루프

목적:
- 승인된 논문 집합을 기반으로 연구 갭과 가설을 정리하고, 실험 설계 및 시뮬레이션으로 검증한다.

흐름:
1. Gap 제시 및 가설 제시
2. 연구자 피드백 반영
3. 연구자 최종 승인까지 반복
4. 실험 디자인 제시
5. 실제 데이터 또는 가상 데이터 기반 시뮬레이션
6. 결과 예측 및 검증
7. 검증 실패 시 필요에 따라 Gap/Hypothesis 단계 또는 Experiment Design 단계로 복귀

핵심 특징:
- gap과 hypothesis는 함께 움직임
- 연구자 승인 루프 존재
- simulation 실패 시 역방향 복귀 화살표 필요

주요 JSON:
- `gap_hypothesis_input.json`
- `gap_hypothesis_output.json`
- `gap_hypothesis_feedback.json`
- `experiment_design_input.json`
- `experiment_design_output.json`
- `simulation_input.json`
- `simulation_output.json`

## 시각화할 때 꼭 드러나야 하는 점

1. Loop A와 Loop B를 구분된 큰 영역으로 보여줄 것
2. Loop A는 "연구자 승인 전까지 반복" 구조를 보여줄 것
3. Loop B의 첫 단계는 "Gap + Hypothesis"가 하나의 묶음임을 보여줄 것
4. Experiment Design은 승인된 Gap/Hypothesis 결과를 입력으로 받는다는 점을 보여줄 것
5. Simulation/Prediction 단계에서 실패 시 두 갈래 복귀가 있음을 보여줄 것
   - Gap/Hypothesis 단계로 복귀
   - Experiment Design 단계로 복귀
6. 모든 단계가 정규화된 JSON input/output를 가진다는 점을 보조 라벨이나 주석으로 넣을 것

## 추천 다이어그램 구조

- 좌우형 또는 상하형 프로세스 다이어그램
- Loop A와 Loop B를 각각 큰 박스로 감싸는 방식
- 연구자 피드백은 원형 또는 pill 모양 노드로 표현
- 단계 박스는 사각형
- 승인/실패에 따른 되돌아감은 점선 또는 강조 화살표로 표현

## 추천 단계 이름

- 연구자 요구 입력
- 논문 탐색
- 연구자 확인 및 피드백
- 승인된 논문 집합
- Gap 제시 및 가설 제시
- 연구자 승인 루프
- 실험 디자인
- 시뮬레이션 및 결과 예측
- 검증 실패 시 복귀

## 스타일 힌트

- 미니멀한 노션 스타일 또는 발표용 깔끔한 프로세스 다이어그램
- Loop A는 옅은 노란색 강조
- Loop B는 중립적인 회색/화이트 톤
- 복귀 화살표는 강조 색상 사용
