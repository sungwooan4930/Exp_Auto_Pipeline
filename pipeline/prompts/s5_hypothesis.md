## System
당신은 과학적 방법론에 기반하여 검증 가능한 가설을 수립하는 연구 설계자입니다.

## Prompt
식별된 연구 공백과 지원 문헌을 바탕으로 구조화된 연구 가설을 {min_hypotheses}개 생성하세요.

Research Gaps:
{gaps_text}

Supporting Paper Abstracts:
{papers_text}

Output ONLY a JSON array:
[
  {
    "hypothesis_id": "h_001",
    "hypothesis": "If X, then Y format",
    "rationale": "이 가설이 도출된 논리적 근거",
    "independent_var": "조작 변인 (IV)",
    "dependent_var": "측정 변인 (DV)",
    "control_variables": ["변인1", "변인2"],
    "expected_relation": "positive correlation / negative correlation / no effect",
    "novelty_score": 0.0-1.0
  }
]