from unittest.mock import MagicMock, patch
from pipeline.config import Config
from pipeline.llm import get_client, ClaudeClient, OpenAIClient


def test_get_client_returns_claude_by_default():
    config = Config(provider="claude")
    with patch("anthropic.Anthropic"):
        client = get_client(config)
    assert isinstance(client, ClaudeClient)


def test_get_client_returns_openai_when_set():
    config = Config(provider="openai")
    with patch("openai.OpenAI"):
        client = get_client(config)
    assert isinstance(client, OpenAIClient)


def test_claude_complete_returns_text():
    config = Config(provider="claude")
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="test response")]
        mock_anthropic.return_value.messages.create.return_value = mock_msg
        client = ClaudeClient(config)
        result = client.complete("hello")
    assert result == "test response"


def test_claude_complete_retries_on_failure():
    config = Config(provider="claude", api_retry_count=2, api_retry_backoff=0.0)
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="ok")]
        mock_anthropic.return_value.messages.create.side_effect = [
            Exception("rate limit"), mock_msg
        ]
        client = ClaudeClient(config)
        result = client.complete("hello")
    assert result == "ok"
