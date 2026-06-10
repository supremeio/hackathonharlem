"""
Thin OpenRouter client.

Uses the OpenAI-compatible Chat Completions endpoint that OpenRouter exposes, so
any model on OpenRouter works by changing OPENROUTER_MODEL. No SDK dependency —
just ``requests`` — to keep setup friction near zero.
"""

from __future__ import annotations

import json
from typing import Optional

import requests

from .config import LLM


class OpenRouterClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key if api_key is not None else LLM.API_KEY
        self.model = model or LLM.MODEL
        self.base_url = (base_url or LLM.BASE_URL).rstrip("/")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": LLM.APP_URL,
            "X-Title": LLM.APP_NAME,
        }

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = LLM.TEMPERATURE,
        max_tokens: int = LLM.MAX_TOKENS,
        json_mode: bool = False,
        timeout: int = 180,
    ) -> str:
        """Single-turn completion. Returns the assistant message text."""
        if not self.available:
            raise RuntimeError(
                "No OPENROUTER_API_KEY set. Either export it, or run in offline "
                "template mode (planner falls back automatically)."
            )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            data=json.dumps(payload),
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"OpenRouter returned no choices: {str(data)[:200]}")
        content = (choices[0].get("message") or {}).get("content")
        if not content:
            raise RuntimeError("OpenRouter returned an empty message.")
        return content

    def complete_json(self, prompt: str, system: Optional[str] = None, **kw) -> dict:
        """Completion that must return a JSON object. Robust to fenced output."""
        raw = self.complete(prompt, system=system, json_mode=True, **kw)
        return _extract_json(raw)


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model response, tolerating ``` fences and prose
    by grabbing the outermost {...} span."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in model output.")
    return json.loads(text[start : end + 1])
