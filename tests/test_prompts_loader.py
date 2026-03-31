import pytest
from pathlib import Path
from pipeline.prompts import load_prompt


def _write_md(tmp_path: Path, name: str, content: str) -> Path:
    """tmp_path에 {name}.md 파일 생성 후 경로 반환."""
    p = tmp_path / f"{name}.md"
    p.write_text(content, encoding="utf-8")
    return tmp_path


def test_load_prompt_returns_system_and_template(tmp_path):
    """정상 .md 파싱 시 (system, template) 튜플 반환."""
    base = _write_md(tmp_path, "test_stage", """\
## System
You are a test assistant.

## Prompt
Hello {name}, you are in {domain}.
""")
    system, template = load_prompt("test_stage", _base=base)
    assert system == "You are a test assistant."
    assert template == "Hello {name}, you are in {domain}."


def test_load_prompt_file_not_found(tmp_path):
    """존재하지 않는 파일명 → FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent", _base=tmp_path)


def test_load_prompt_missing_system_section(tmp_path):
    """## System 없는 파일 → ValueError."""
    base = _write_md(tmp_path, "no_system", """\
## Prompt
Hello {domain}.
""")
    with pytest.raises(ValueError, match="## System"):
        load_prompt("no_system", _base=base)


def test_load_prompt_missing_prompt_section(tmp_path):
    """## Prompt 없는 파일 → ValueError."""
    base = _write_md(tmp_path, "no_prompt", """\
## System
You are a test assistant.
""")
    with pytest.raises(ValueError, match="## Prompt"):
        load_prompt("no_prompt", _base=base)


def test_load_prompt_preserves_placeholders(tmp_path):
    """{domain}, {n_queries} 등 플레이스홀더 문자 그대로 유지."""
    base = _write_md(tmp_path, "placeholders", """\
## System
System text.

## Prompt
Generate {n_queries} queries for {domain}.
""")
    _, template = load_prompt("placeholders", _base=base)
    assert "{n_queries}" in template
    assert "{domain}" in template
