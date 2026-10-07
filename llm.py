"""Thin client for an OpenAI-compatible chat completions API.

Works with OpenAI, OpenRouter, Groq, or any endpoint that follows the
``/chat/completions`` schema. If no API key is configured, the client runs in
**mock mode** so the app and its tests work out of the box.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


class LLMError(RuntimeError):
    """Raised when the upstream API returns an error."""


class LLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("LLM_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.getenv("LLM_MODEL") or DEFAULT_MODEL
        self.timeout = timeout

    @property
    def mock_mode(self) -> bool:
        return not self.api_key

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send *messages* and return the assistant's reply text."""
        if self.mock_mode:
            return self._mock_reply(messages)

        payload = json.dumps({"model": self.model, "messages": messages}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # pragma: no cover - network path
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"Upstream API error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network path
            raise LLMError(f"Could not reach the LLM API: {exc.reason}") from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected API response: {json.dumps(data)[:300]}") from exc

    def _mock_mode_reply(self, messages: list[dict]) -> str:
        last = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        return (
            "[mock mode] No LLM_API_KEY configured, so this is a canned reply. "
            f"You said: {last!r}. Set LLM_API_KEY to get real responses."
        )

    # Alias kept for readability in tests.
    _mock_reply = _mock_mode_reply