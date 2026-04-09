import json
import logging
import re
from typing import Any
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s1_query_gen")


def _format_list_block(value: list[str] | None, fallback: str = "- not specified") -> str:
    if not value:
        return fallback
    return "\n".join(f"- {item}" for item in value if isinstance(item, str) and item.strip()) or fallback


def _normalize_request(domain_or_request: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(domain_or_request, dict):
        request = domain_or_request.get("request", domain_or_request)
        quality = domain_or_request.get("quality_criteria", {})
        year_range = request.get("year_range", {})
        return {
            "domain": request.get("domain", ""),
            "keywords": request.get("keywords", []),
            "experiment_type": request.get("experiment_type", "not specified"),
            "research_goals": request.get("research_goals", []),
            "constraints": request.get("constraints", []),
            "preferred_sources": request.get("preferred_sources", []),
            "exclusion_rules": request.get("exclusion_rules", []),
            "must_cover": quality.get("must_cover", []),
            "must_avoid": quality.get("must_avoid", []),
            "selection_principles": quality.get("selection_principles", []),
            "year_range": year_range,
            "raw_request": domain_or_request,
        }

    return {
        "domain": domain_or_request,
        "keywords": [],
        "experiment_type": "not specified",
        "research_goals": [],
        "constraints": [],
        "preferred_sources": [],
        "exclusion_rules": [],
        "must_cover": [],
        "must_avoid": [],
        "selection_principles": [],
        "year_range": {},
        "raw_request": None,
    }


def generate_queries(domain_or_request: str | dict[str, Any], llm: LLMClient, config: Config) -> dict:
    normalized = _normalize_request(domain_or_request)
    year_range = normalized["year_range"]
    year_constraint = ""
    if year_range.get("start") and year_range.get("end"):
        year_constraint = f"- Prefer work published between {year_range['start']} and {year_range['end']}."

    prompt = _PROMPT_TEMPLATE.format(
        domain=normalized["domain"],
        n_queries=7,
        keywords=_format_list_block(normalized["keywords"]),
        experiment_type=normalized["experiment_type"],
        research_goals=_format_list_block(normalized["research_goals"]),
        constraints=_format_list_block(normalized["constraints"] + ([year_constraint] if year_constraint else [])),
        preferred_sources=_format_list_block(normalized["preferred_sources"]),
        exclusion_rules=_format_list_block(normalized["exclusion_rules"]),
        must_cover=_format_list_block(normalized["must_cover"]),
        must_avoid=_format_list_block(normalized["must_avoid"]),
        selection_principles=_format_list_block(normalized["selection_principles"]),
    )
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

    result = {"domain": normalized["domain"], "queries": queries}
    if normalized["raw_request"] is not None:
        result["request"] = normalized["raw_request"].get("request", normalized["raw_request"])
        if "quality_criteria" in normalized["raw_request"]:
            result["quality_criteria"] = normalized["raw_request"]["quality_criteria"]
    return result
