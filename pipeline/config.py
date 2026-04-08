import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    provider: str = field(default_factory=lambda: os.getenv("PROVIDER", "claude"))
    claude_model: str = "claude-3-5-sonnet-20241022"
    openai_model: str = "gpt-4o"
    gemini_model: str = "gemini-2.0-flash"
    target_papers: int = 50
    min_screened: int = 15
    max_screened: int = 20
    min_gaps: int = 3
    min_hypotheses: int = 3
    output_base: Path = Path("outputs")
    api_retry_count: int = 3
    api_retry_backoff: float = 2.0
    use_snowball: bool = True
    year_range: str = "2022-2026"
