import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s4_gap")


def analyze_gaps(screened: list[dict], llm: LLMClient, config: Config) -> list[dict]:
    included = [p for p in screened if p.get("decision") == "include"]
    if not included:
        included = screened  # fallback

    papers_text = "\n\n".join(
        f"[{p['paper_id']}] {p['title']}\n{p['abstract']}"
        for p in included
    )
    prompt = _PROMPT_TEMPLATE.format(papers_text=papers_text, min_gaps=config.min_gaps)
    raw = llm.complete(prompt, system=_SYSTEM)

    # 가장 마지막에 나오는 JSON 배열 [ ... ] 을 찾음
    matches = list(re.finditer(r'\[.*\]', raw, re.DOTALL))
    gaps = []
    if matches:
        try:
            gaps = json.loads(matches[-1].group())
        except json.JSONDecodeError:
            pass
    
    if not gaps:
        try:
            gaps = json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse gap analysis response: {raw}")
            gaps = []

    if len(gaps) < config.min_gaps:
        logger.warning(f"Only {len(gaps)} gaps identified, minimum is {config.min_gaps}")

    return gaps
