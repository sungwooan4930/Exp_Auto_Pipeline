import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

logger = logging.getLogger(__name__)

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s5_hypothesis")


def generate_hypotheses(
    gaps: list[dict],
    screened: list[dict],
    llm: LLMClient,
    config: Config
) -> list[dict]:
    gaps_text = "\n".join(
        f"[{g['gap_id']}] {g['gap']}" for g in gaps
    )
    included = [p for p in screened if p.get("decision") == "include"]
    papers_text = "\n\n".join(
        f"[{p['paper_id']}] {p['title']}: {p['abstract'][:300]}"
        for p in included[:10]  # token saving
    )
    prompt = _PROMPT_TEMPLATE.format(
        gaps_text=gaps_text,
        papers_text=papers_text,
        min_hypotheses=config.min_hypotheses
    )
    raw = llm.complete(prompt, system=_SYSTEM)
    
    # 가장 마지막에 나오는 JSON 배열 [ ... ] 을 찾음
    matches = list(re.finditer(r'\[.*\]', raw, re.DOTALL))
    hypotheses = []
    if matches:
        try:
            hypotheses = json.loads(matches[-1].group())
        except json.JSONDecodeError:
            pass
    
    if not hypotheses:
        try:
            hypotheses = json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse hypothesis generation response: {raw}")
            hypotheses = []

    # clip novelty_score to [0, 1]
    for h in hypotheses:
        if isinstance(h, dict):
            try:
                h["novelty_score"] = max(0.0, min(1.0, float(h.get("novelty_score", 0.5))))
            except (ValueError, TypeError):
                h["novelty_score"] = 0.5

    if len(hypotheses) < config.min_hypotheses:
        logger.warning(f"Only {len(hypotheses)} hypotheses generated, minimum is {config.min_hypotheses}")

    return hypotheses
