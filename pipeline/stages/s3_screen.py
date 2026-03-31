import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a systematic review assistant. Output ONLY valid JSON, no explanation."

PROMPT_TEMPLATE = """You are screening papers for a systematic literature review on the domain: "{domain}"

Paper to screen:
Title: {title}
Abstract: {abstract}

Decide whether to INCLUDE or EXCLUDE this paper.
- INCLUDE if: directly relevant to the domain, empirical/theoretical contribution
- EXCLUDE if: tangentially related, off-topic, no abstract

Output ONLY this JSON (no markdown):
{{"decision": "include" or "exclude", "reason": "one sentence explanation"}}"""


def _parse_screening_response(raw: str) -> dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)


def screen_papers(papers: list[dict], domain: str, llm: LLMClient, config: Config) -> list[dict]:
    results = []
    for paper in papers:
        prompt = PROMPT_TEMPLATE.format(
            domain=domain,
            title=paper.get("title", ""),
            abstract=paper.get("abstract", "")
        )
        raw = llm.complete(prompt, system=SYSTEM)
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
