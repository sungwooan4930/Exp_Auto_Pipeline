import os
import time
from abc import ABC, abstractmethod
from pipeline.config import Config


class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str = "") -> str:
        ...


class ClaudeClient(LLMClient):
    def __init__(self, config: Config):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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
                time.sleep(self._backoff * (2 ** attempt))


def get_client(config: Config | None = None) -> LLMClient:
    if config is None:
        config = Config()
    if config.provider == "openai":
        return OpenAIClient(config)
    return ClaudeClient(config)
