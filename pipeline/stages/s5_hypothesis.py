import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a research hypothesis generator. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Based on the following research gaps and supporting papers, generate structured research hypotheses.

Research Gaps:
{gaps_text}

Supporting Paper Abstracts:
{papers_text}

Generate at least {min_hypotheses} hypotheses. For each:
- State the hypothesis clearly (if X then Y format)
- Identify the independent variable (what you manipulate)
- Identify the dependent variable (what you measure)
- State expected relationship direction
- Estimate novelty score (0.0–1.0) vs existing literature

Output ONLY a JSON array (no markdown):
[
  {{
    "hypothesis_id": "h_001",
    "hypothesis": "...",
    "independent_var": "...",
    "dependent_var": "...",
    "expected_relation": "positive correlation" or "negative correlation" or "no effect",
    "novelty_score": 0.0
  }},
  ...
]"""


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
    prompt = PROMPT_TEMPLATE.format(
        gaps_text=gaps_text,
        papers_text=papers_text,
        min_hypotheses=config.min_hypotheses
    )
    raw = llm.complete(prompt, system=SYSTEM)
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    hypotheses = json.loads(match.group() if match else raw)

    # clip novelty_score to [0, 1]
    for h in hypotheses:
        h["novelty_score"] = max(0.0, min(1.0, float(h.get("novelty_score", 0.5))))

    if len(hypotheses) < config.min_hypotheses:
        logger.warning(f"Only {len(hypotheses)} hypotheses generated, minimum is {config.min_hypotheses}")

    return hypotheses
