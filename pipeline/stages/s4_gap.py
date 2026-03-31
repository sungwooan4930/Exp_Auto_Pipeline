import json
import logging
import re
from pipeline.config import Config
from pipeline.llm import LLMClient

logger = logging.getLogger(__name__)

SYSTEM = "You are a research gap analyst. Output ONLY valid JSON arrays, no explanation."

PROMPT_TEMPLATE = """Analyze the following screened papers and identify research gaps.

Papers:
{papers_text}

Identify at least {min_gaps} distinct research gaps — areas that existing papers do NOT adequately address.
For each gap, cite which paper IDs support the finding.

Output ONLY a JSON array (no markdown):
[
  {{"gap_id": "gap_001", "gap": "description of gap", "evidence_papers": ["paper_id1", "paper_id2"]}},
  ...
]"""


def analyze_gaps(screened: list[dict], llm: LLMClient, config: Config) -> list[dict]:
    included = [p for p in screened if p.get("decision") == "include"]
    if not included:
        included = screened  # fallback

    papers_text = "\n\n".join(
        f"[{p['paper_id']}] {p['title']}\n{p['abstract']}"
        for p in included
    )
    prompt = PROMPT_TEMPLATE.format(papers_text=papers_text, min_gaps=config.min_gaps)
    raw = llm.complete(prompt, system=SYSTEM)

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    gaps = json.loads(match.group() if match else raw)

    if len(gaps) < config.min_gaps:
        logger.warning(f"Only {len(gaps)} gaps identified, minimum is {config.min_gaps}")

    return gaps
