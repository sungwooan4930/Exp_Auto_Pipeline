import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s3_screen")


def _parse_screening_response(raw: str) -> dict:
    # 가장 마지막에 나오는 JSON 객체 { ... } 를 찾음
    matches = list(re.finditer(r'\{.*\}', raw, re.DOTALL))
    if matches:
        try:
            return json.loads(matches[-1].group())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse screening response: {raw}")
        return {"decision": "exclude", "reason": "Parsing error", "category": "Unknown", "confidence_score": 0.0}


def screen_papers(papers: list[dict], domain: str, llm: LLMClient, config: Config) -> list[dict]:
    results = []
    for paper in papers:
        prompt = _PROMPT_TEMPLATE.format(
            domain=domain,
            title=paper.get("title", ""),
            abstract=paper.get("abstract", "")
        )
        raw = llm.complete(prompt, system=_SYSTEM)
        parsed = _parse_screening_response(raw)
        
        # 새 필드들 포함 (category, confidence_score)
        results.append({
            "paper_id": paper["paper_id"],
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "decision": parsed.get("decision", "exclude"),
            "category": parsed.get("category", "Unknown"),
            "confidence_score": parsed.get("confidence_score", 0.0),
            "reason": parsed.get("reason", "")
        })

    included = [r for r in results if r["decision"] == "include"]

    if len(included) < config.min_screened:
        logger.warning(
            f"Screened papers ({len(included)}) below minimum ({config.min_screened}). "
            f"Relaxing threshold — returning all screened results."
        )

    return results
