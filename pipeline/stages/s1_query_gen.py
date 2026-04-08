import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s1_query_gen")


def generate_queries(domain: str, llm: LLMClient, config: Config) -> dict:
    prompt = _PROMPT_TEMPLATE.format(domain=domain, n_queries=7)
    raw = llm.complete(prompt, system=_SYSTEM)
    
    # JSON 배열 추출 (가장 마지막에 나타나는 배열을 찾음)
    matches = list(re.finditer(r'\[\s*".*?"\s*(?:\s*,\s*".*?"\s*)*\]', raw, re.DOTALL))
    
    queries = []
    if matches:
        # 가장 마지막 매치를 선택
        last_match = matches[-1].group()
        try:
            queries = json.loads(last_match)
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse JSON from last match: {last_match}")
    else:
        # 일반적인 [.*] 패턴으로 재시도
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            try:
                queries = json.loads(match.group())
            except json.JSONDecodeError:
                pass

    # 만약 여전히 비어있다면 전체 파싱 시도
    if not queries:
        try:
            queries = json.loads(raw)
        except Exception:
            pass
    
    # 5~10개 범위로 클리핑
    queries = [q for q in queries if isinstance(q, str) and q.strip()][:10]
    if len(queries) < 5:
        logger.error(f"LLM returned only {len(queries)} queries. Raw output: {raw}")
        raise ValueError(f"LLM returned only {len(queries)} queries, expected 5+.")
    return {"domain": domain, "queries": queries}
