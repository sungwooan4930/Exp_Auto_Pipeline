from pathlib import Path


def load_prompt(name: str, _base: Path | None = None) -> tuple[str, str]:
    """pipeline/prompts/{name}.md 에서 System·Prompt 섹션을 파싱해 반환.

    Args:
        name: .md 파일 이름 (확장자 제외). 예: "s1_query_gen"
        _base: 테스트용 오버라이드 경로. None이면 이 파일과 같은 디렉터리 사용.

    Returns:
        (system, prompt_template) — 각각 strip() 처리된 str

    Raises:
        FileNotFoundError: .md 파일이 없을 때
        ValueError: ## System 또는 ## Prompt 섹션 누락 시
    """
    base = _base if _base is not None else Path(__file__).parent
    path = base / f"{name}.md"
    text = path.read_text(encoding="utf-8")  # FileNotFoundError는 자연 전파

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.strip() == "## System":
            current = "system"
            sections[current] = []
        elif line.strip() == "## Prompt":
            current = "prompt"
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    if "system" not in sections:
        raise ValueError(f"{name}.md: ## System 섹션 없음")
    if "prompt" not in sections:
        raise ValueError(f"{name}.md: ## Prompt 섹션 없음")

    return "\n".join(sections["system"]).strip(), "\n".join(sections["prompt"]).strip()
