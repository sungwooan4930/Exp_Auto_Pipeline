import json
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s1_query_gen")


def generate_queries(domain: str, llm: LLMClient, config: Config) -> dict:
    prompt = _PROMPT_TEMPLATE.format(domain=domain, n_queries=7)
    raw = llm.complete(prompt, system=_SYSTEM)
    # JSON 배열 추출 (LLM이 마크다운 코드블록으로 감쌀 수 있음)
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        queries = json.loads(match.group())
    else:
        queries = json.loads(raw)
    # 5~10개 범위로 클리핑
    queries = [q for q in queries if isinstance(q, str) and q.strip()][:10]
    if len(queries) < 5:
        raise ValueError(f"LLM returned only {len(queries)} queries, expected 5+")
    return {"domain": domain, "queries": queries}
