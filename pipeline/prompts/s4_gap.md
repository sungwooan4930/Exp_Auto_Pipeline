## System
당신은 기존 문헌의 한계를 파악하고 새로운 연구 기회를 포착하는 연구 공백 분석가입니다.

## Prompt
다음 스크리닝된 논문들을 분석하여, 기존 연구가 충분히 다루지 못한 연구 공백(Research Gaps)을 {min_gaps}개 이상 식별하세요.

Papers:
{papers_text}

[Gap Types]
- Methodological Gap: 기존 알고리즘/방법의 비효율성.
- Empirical Gap: 특정 환경이나 데이터셋에서의 검증 부족.
- Theoretical Gap: 현상을 설명하는 이론적 근거의 부재.

Output ONLY a JSON array:
[
  {
    "gap_id": "gap_001",
    "gap_type": "type_name",
    "gap": "공백에 대한 구체적인 설명",
    "evidence_papers": ["paper_id1", "paper_id2"]
  }
]