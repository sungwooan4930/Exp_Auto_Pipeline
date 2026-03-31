import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    provider: str = field(default_factory=lambda: os.getenv("PROVIDER", "claude"))
    claude_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    target_papers: int = 50
    min_screened: int = 15
    max_screened: int = 20
    min_gaps: int = 3
    min_hypotheses: int = 3
    output_base: Path = Path("outputs")
    api_retry_count: int = 3
    api_retry_backoff: float = 2.0
