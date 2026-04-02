import json
import logging
import os
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from pipeline.config import Config

logger = logging.getLogger(__name__)


def _get_claude_cli_token() -> str | None:
    """~/.claude/.credentials.json 에서 Claude CLI OAuth 토큰을 읽어 반환.
    만료 여부는 Anthropic API가 401로 알려주므로 별도 체크 불필요.
    """
    creds_path = Path.home() / ".claude" / ".credentials.json"
    if not creds_path.exists():
        return None
    try:
        data = json.loads(creds_path.read_text())
        token = data.get("claudeAiOauth", {}).get("accessToken")
        if token:
            logger.info("Using Claude CLI OAuth token from ~/.claude/.credentials.json")
        return token
    except Exception as e:
        logger.warning(f"Failed to read Claude CLI credentials: {e}")
        return None


def _resolve_anthropic_api_key() -> str | None:
    """API 키 해석 우선순위:
    1. ANTHROPIC_API_KEY 환경변수
    2. Claude CLI OAuth 토큰 (~/.claude/.credentials.json)
    """
    return os.getenv("ANTHROPIC_API_KEY") or _get_claude_cli_token()


class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str = "") -> str:
        ...


class ClaudeClient(LLMClient):
    def __init__(self, config: Config):
        import anthropic
        api_key = _resolve_anthropic_api_key()
        if not api_key:
            raise RuntimeError(
                "No Anthropic API key found. Set ANTHROPIC_API_KEY env var "
                "or log in with Claude CLI (`claude` command)."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = config.claude_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        messages = [{"role": "user", "content": prompt}]
        kwargs = {"model": self._model, "max_tokens": 4096, "messages": messages}
        if system:
            kwargs["system"] = system
        for attempt in range(self._retry_count):
            try:
                response = self._client.messages.create(**kwargs)
                return response.content[0].text
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{self._retry_count}): {e}. Retrying..."
                )
                time.sleep(self._backoff * (2 ** attempt))


class OpenAIClient(LLMClient):
    def __init__(self, config: Config):
        import openai
        self._client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._model = config.openai_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        for attempt in range(self._retry_count):
            try:
                response = self._client.chat.completions.create(
                    model=self._model, messages=messages, max_tokens=4096
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{self._retry_count}): {e}. Retrying..."
                )
                time.sleep(self._backoff * (2 ** attempt))


class ClaudeCLIClient(LLMClient):
    """claude CLI 서브프로세스를 통해 호출 (Claude 구독 OAuth 사용)."""

    def __init__(self, config: Config):
        self._model = config.claude_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        cmd = [
            "claude", "-p", prompt,
            "--model", self._model,
            "--no-session-persistence",
        ]
        if system:
            cmd += ["--system-prompt", system]

        # ANTHROPIC_API_KEY가 환경에 있으면 claude CLI가 이를 API 키로 인식해 실패
        # → 해당 변수를 제거하고 CLI 자체 OAuth 인증을 사용하도록 함
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

        for attempt in range(self._retry_count):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=300,
                    shell=True,  # Windows에서 .cmd 파일 실행을 위해 필요
                    env=env,
                )
                if result.returncode != 0:
                    detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
                    raise RuntimeError(detail)
                return result.stdout.strip()
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                logger.warning(
                    f"CLI call failed (attempt {attempt + 1}/{self._retry_count}): {e}. Retrying..."
                )
                time.sleep(self._backoff * (2 ** attempt))


def get_client(config: Config | None = None) -> LLMClient:
    if config is None:
        config = Config()
    if config.provider == "openai":
        return OpenAIClient(config)
    # API 키가 없거나 OAuth 토큰이면 CLI 방식 사용
    api_key = _resolve_anthropic_api_key()
    if not api_key or api_key.startswith("sk-ant-oat"):
        logger.info("Using Claude CLI client (OAuth subscription mode)")
        return ClaudeCLIClient(config)
    return ClaudeClient(config)
