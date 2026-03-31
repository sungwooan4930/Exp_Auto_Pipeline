import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s3_screen")


def _parse_screening_response(raw: str) -> dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)


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
        results.append({
            "paper_id": paper["paper_id"],
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "decision": parsed.get("decision", "exclude"),
            "reason": parsed.get("reason", "")
        })

    included = [r for r in results if r["decision"] == "include"]

    if len(included) < config.min_screened:
        logger.warning(
            f"Screened papers ({len(included)}) below minimum ({config.min_screened}). "
            f"Relaxing threshold — returning all screened results."
        )

    return results
