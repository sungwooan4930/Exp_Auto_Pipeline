import json
import logging
import os
import re
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from pipeline.config import Config

logger = logging.getLogger(__name__)


def _get_claude_cli_token() -> str | None:
    """~/.claude/.credentials.json 에서 Claude CLI OAuth 토큰을 읽어 반환."""
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
            raise RuntimeError("No Anthropic API key found.")
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
                logger.warning(f"LLM call failed: {e}. Retrying...")
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
                logger.warning(f"LLM call failed: {e}. Retrying...")
                time.sleep(self._backoff * (2 ** attempt))


class GeminiRESTClient(LLMClient):
    """Gemini REST API 직접 호출 (인코딩/에이전트 문제 없음)."""
    def __init__(self, config: Config, api_key: str):
        self._api_key = api_key
        self._model = config.gemini_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff
        import httpx
        self._http = httpx.Client(timeout=120.0)

    def complete(self, prompt: str, system: str = "") -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": 4096,
                "temperature": 0.7,
            }
        }
        if system:
            payload["system_instruction"] = {"parts": [{"text": system}]}

        for attempt in range(self._retry_count):
            try:
                resp = self._http.post(url, json=payload)
                if resp.status_code == 429:
                    wait_time = 20.0  # 기본 20초 대기
                    try:
                        data = resp.json()
                        # 에러 메시지에서 대기 시간 추출 시도
                        msg = data.get("error", {}).get("message", "")
                        match = re.search(r"retry in ([\d\.]+)s", msg)
                        if match:
                            wait_time = float(match.group(1)) + 1.0
                    except Exception:
                        pass
                    
                    if attempt < self._retry_count - 1:
                        logger.warning(f"Gemini API Quota reached (429). Waiting {wait_time}s and retrying...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"Gemini API Quota exhausted: {resp.text}")

                if resp.status_code != 200:
                    raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text}")
                
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                logger.warning(f"Gemini REST API failed: {e}. Retrying...")
                time.sleep(self._backoff * (2 ** attempt))


class GeminiClient(LLMClient):
    """google-generativeai 패키지 사용."""
    def __init__(self, config: Config, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self._model_name = config.gemini_model
        self._client = genai.GenerativeModel(self._model_name)
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        for attempt in range(self._retry_count):
            try:
                response = self._client.generate_content(full_prompt)
                return response.text
            except Exception as e:
                if attempt == self._retry_count - 1:
                    raise
                logger.warning(f"LLM call failed: {e}. Retrying...")
                time.sleep(self._backoff * (2 ** attempt))


class GeminiCLIClient(LLMClient):
    """gemini CLI 서브프로세스 호출 (최후의 보루)."""
    def __init__(self, config: Config):
        self._model = config.gemini_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        full_prompt = f"System Instruction: {system}\n\nUser Question: {prompt}" if system else prompt
        full_prompt += "\n\nCRITICAL: Return ONLY raw content, no agent chatter or tool use plans."
        
        cmd = ["gemini", "--model", self._model, "--prompt", "-"]
        for attempt in range(self._retry_count):
            try:
                result = subprocess.run(
                    cmd, input=full_prompt, capture_output=True,
                    text=False, timeout=180, shell=True
                )
                # 인코딩 시도 (utf-8 -> cp949)
                try:
                    output = result.stdout.decode('utf-8')
                except UnicodeDecodeError:
                    output = result.stdout.decode('cp949', errors='replace')
                
                if result.returncode != 0:
                    raise RuntimeError(output or "CLI error")
                
                # 에이전트 로그 및 메타데이터 제거
                clean_lines = []
                for line in output.splitlines():
                    if any(x in line for x in ["Loaded cached", "Gemini CLI", "I will", "Checking for"]):
                        continue
                    clean_lines.append(line)
                return "\n".join(clean_lines).strip()
            except Exception as e:
                if attempt == self._retry_count - 1: raise
                logger.warning(f"CLI failed: {e}. Retrying...")
                time.sleep(self._backoff)


class ClaudeCLIClient(LLMClient):
    def __init__(self, config: Config):
        self._model = config.claude_model
        self._retry_count = config.api_retry_count
        self._backoff = config.api_retry_backoff

    def complete(self, prompt: str, system: str = "") -> str:
        cmd = ["claude", "-p", prompt, "--model", self._model, "--no-session-persistence"]
        if system: cmd += ["--system-prompt", system]
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        for attempt in range(self._retry_count):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300, shell=True, env=env)
                if result.returncode != 0: raise RuntimeError(result.stderr or result.stdout)
                return result.stdout.strip()
            except Exception as e:
                if attempt == self._retry_count - 1: raise
                logger.warning(f"CLI failed: {e}. Retrying...")
                time.sleep(self._backoff)


def get_client(config: Config | None = None) -> LLMClient:
    if config is None: config = Config()
    provider = config.provider.lower()
    
    if provider == "openai":
        return OpenAIClient(config)

    if provider == "claude-cli":
        return ClaudeCLIClient(config)
    
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("AIza"):
            logger.info("Using Gemini REST API client")
            return GeminiRESTClient(config, api_key)
        logger.info("No Gemini API key found, falling back to CLI")
        return GeminiCLIClient(config)

    return ClaudeClient(config)
