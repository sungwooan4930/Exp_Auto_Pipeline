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

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    gaps = json.loads(match.group() if match else raw)

    if len(gaps) < config.min_gaps:
        logger.warning(f"Only {len(gaps)} gaps identified, minimum is {config.min_gaps}")

    return gaps
