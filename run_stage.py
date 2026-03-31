#!/usr/bin/env python3
"""단일 단계 실행: python run_stage.py --stage 3 --input outputs/2026-03-31_143022/"""
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from run_pipeline import run


def main():
    parser = argparse.ArgumentParser(description="RAP: Run a single stage")
    parser.add_argument("--stage", type=int, required=True, choices=range(1, 8), help="Stage number (1-7)")
    parser.add_argument("--input", required=True, help="Existing output dir")
    parser.add_argument("--domain", default="", help="Domain (required for stage 1)")
    args = parser.parse_args()

    from pipeline.config import Config
    config = Config()
    input_dir = Path(args.input)

    domain = args.domain
    if not domain and (input_dir / "search_queries.json").exists():
        import json
        domain = json.loads((input_dir / "search_queries.json").read_text()).get("domain", "")

    asyncio.run(run(domain, config, from_stage=args.stage, input_dir=input_dir))


if __name__ == "__main__":
    main()
