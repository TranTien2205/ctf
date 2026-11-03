"""Provider adapters: one per API dialect, plus two CLI agents and a mock."""
from __future__ import annotations

from .base import Completion, Message, Provider, ToolCall      # noqa: F401

_REGISTRY = {
    "anthropic": ("argus.runtime.providers.anthropic_api", "AnthropicProvider"),
    "openai": ("argus.runtime.providers.openai_api", "OpenAIProvider"),
    "deepseek": ("argus.runtime.providers.openai_api", "DeepSeekProvider"),
    "openrouter": ("argus.runtime.providers.openai_api", "OpenRouterProvider"),
    "google": ("argus.runtime.providers.google_api", "GoogleProvider"),
    "opencode": ("argus.runtime.providers.opencode_cli", "OpenCodeProvider"),
    "claude_cli": ("argus.runtime.providers.claude_cli", "ClaudeCliProvider"),
    "mock": ("argus.runtime.providers.mock", "MockProvider"),
}


def get(name: str, **kwargs) -> Provider:
    if name not in _REGISTRY:
        raise KeyError(f"no provider {name!r}; known: {sorted(_REGISTRY)}")
    module_name, class_name = _REGISTRY[name]
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)(**kwargs)


def names() -> list[str]:
    return sorted(_REGISTRY)
