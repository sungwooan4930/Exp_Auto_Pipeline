#!/usr/bin/env python3
"""전체 파이프라인 실행: python run_pipeline.py --domain "LLM-based autonomous agents" """
import argparse
import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from pipeline.config import Config
from pipeline.llm import get_client
from pipeline.stages.s1_query_gen import generate_queries
from pipeline.stages.s2_collect import collect_papers, papers_to_bibtex
from pipeline.stages.s3_screen import screen_papers
from pipeline.stages.s4_gap import analyze_gaps
from pipeline.stages.s5_hypothesis import generate_hypotheses
from pipeline.stages.s6_experiment import design_experiment
from pipeline.stages.s7_metrics import compute_metrics


def make_run_dir(config: Config) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = config.output_base / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


async def run(domain: str, config: Config, from_stage: int = 1, input_dir: Path | None = None):
    run_dir = input_dir if input_dir else make_run_dir(config)
    llm = get_client(config)
    logger.info(f"Run dir: {run_dir}, domain: {domain}, provider: {config.provider}, model: {config.gemini_model if config.provider == 'gemini' else config.claude_model}")

    # S1
    if from_stage <= 1:
        logger.info("Stage 1: Generating queries...")
        queries_data = generate_queries(domain, llm, config)
        (run_dir / "search_queries.json").write_text(json.dumps(queries_data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"  → {len(queries_data['queries'])} queries saved")
    else:
        queries_data = json.loads((run_dir / "search_queries.json").read_text(encoding="utf-8"))

    # S2
    if from_stage <= 2:
        logger.info("Stage 2: Collecting papers...")
        papers = await collect_papers(queries_data["queries"], config)
        (run_dir / "collected_papers.bib").write_text(papers_to_bibtex(papers), encoding="utf-8")
        (run_dir / "collected_papers.json").write_text(json.dumps(papers, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"  → {len(papers)} papers collected")
    else:
        papers = json.loads((run_dir / "collected_papers.json").read_text(encoding="utf-8"))

    # S3
    if from_stage <= 3:
        logger.info("Stage 3: Screening papers...")
        screened = screen_papers(papers, domain, llm, config)
        (run_dir / "screening_results.json").write_text(json.dumps(screened, ensure_ascii=False, indent=2), encoding="utf-8")
        included = sum(1 for p in screened if p["decision"] == "include")
        logger.info(f"  → {included} papers included")
    else:
        screened = json.loads((run_dir / "screening_results.json").read_text(encoding="utf-8"))

    # S4
    if from_stage <= 4:
        logger.info("Stage 4: Analyzing gaps...")
        gaps = analyze_gaps(screened, llm, config)
        (run_dir / "gap_analysis.json").write_text(json.dumps(gaps, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"  → {len(gaps)} gaps identified")
    else:
        gaps = json.loads((run_dir / "gap_analysis.json").read_text(encoding="utf-8"))

    # S5
    if from_stage <= 5:
        logger.info("Stage 5: Generating hypotheses...")
        hypotheses = generate_hypotheses(gaps, screened, llm, config)
        (run_dir / "hypotheses.json").write_text(json.dumps(hypotheses, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"  → {len(hypotheses)} hypotheses generated")
    else:
        hypotheses = json.loads((run_dir / "hypotheses.json").read_text(encoding="utf-8"))

    # S6
    if from_stage <= 6:
        logger.info("Stage 6: Designing experiment...")
        experiment_md = design_experiment(hypotheses, llm, config)
        (run_dir / "experiment_design.md").write_text(experiment_md, encoding="utf-8")
        logger.info("  → experiment_design.md written")

    # S7
    logger.info("Stage 7: Computing metrics...")
    metrics = compute_metrics(run_dir, domain)
    (run_dir / "weekly_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"  → Metrics: {metrics}")
    logger.info(f"Pipeline complete. Results in: {run_dir}")
    return run_dir


def main():
    parser = argparse.ArgumentParser(description="RAP Pipeline")
    parser.add_argument("--domain", required=True, help="Research domain")
    parser.add_argument("--from-stage", type=int, default=1, help="Start from stage (1-7)")
    parser.add_argument("--input", help="Existing run directory to resume")
    parser.add_argument("--provider", help="LLM Provider (claude, gemini, openai)")
    parser.add_argument("--model", help="Specific model name")
    args = parser.parse_args()

    config = Config()
    if args.provider:
        config.provider = args.provider.lower()
    
    if args.model:
        if config.provider == "claude":
            config.claude_model = args.model
        elif config.provider == "gemini":
            config.gemini_model = args.model
        elif config.provider == "openai":
            config.openai_model = args.model

    input_dir = Path(args.input) if args.input else None
    asyncio.run(run(args.domain, config, from_stage=args.from_stage, input_dir=input_dir))


if __name__ == "__main__":
    main()
