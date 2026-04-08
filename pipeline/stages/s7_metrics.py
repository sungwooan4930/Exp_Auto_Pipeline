import json
import re
from datetime import datetime, timezone
from pathlib import Path


def compute_metrics(output_dir: Path, domain: str) -> dict:
    output_dir = Path(output_dir)

    bib_path = output_dir / "collected_papers.bib"
    collected = 0
    if bib_path.exists():
        collected = len(re.findall(r'@\w+\{', bib_path.read_text()))

    screening_path = output_dir / "screening_results.json"
    screened = 0
    if screening_path.exists():
        screening = json.loads(screening_path.read_text())
        screened = sum(1 for p in screening if p.get("decision") == "include")

    json_path = output_dir / "collected_papers.json"
    snowball_count = 0
    if json_path.exists():
        papers_data = json.loads(json_path.read_text())
        snowball_count = sum(1 for p in papers_data if p.get("source", "").startswith("snowball_"))

    screen_rate = round(screened / collected, 4) if collected > 0 else 0.0

    gap_path = output_dir / "gap_analysis.json"
    gaps = 0
    if gap_path.exists():
        gaps = len(json.loads(gap_path.read_text()))

    hyp_path = output_dir / "hypotheses.json"
    hypotheses = 0
    if hyp_path.exists():
        hypotheses = len(json.loads(hyp_path.read_text()))

    run_id = output_dir.name

    return {
        "run_id": run_id,
        "domain": domain,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "collected": collected,
        "screened": screened,
        "screen_rate": screen_rate,
        "snowball_count": snowball_count,
        "gaps": gaps,
        "hypotheses": hypotheses,
    }
