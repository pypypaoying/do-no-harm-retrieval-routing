from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable, Protocol


class TextProvider(Protocol):
    def generate(self, prompts: list[str]) -> list[str]:
        ...


@dataclass
class EchoProvider:
    label: str = "unknown"

    def generate(self, prompts: list[str]) -> list[str]:
        import hashlib

        labels = ["true", "false", "unknown"]
        outputs = []
        for prompt in prompts:
            if self.label != "auto":
                label = self.label
                confidence = 0.5
            else:
                digest = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16)
                label = labels[digest % len(labels)]
                confidence = 0.45 + ((digest // 7) % 50) / 100.0
            outputs.append(f'{{"answer": "{label}", "confidence": {min(confidence, 0.99):.2f}}}')
        return outputs


@dataclass
class AnthropicProvider:
    model: str
    max_tokens: int = 64
    temperature: float = 0.0
    retries: int = 5

    def generate(self, prompts: list[str]) -> list[str]:
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        outputs = []
        for prompt in prompts:
            for attempt in range(self.retries):
                try:
                    message = client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    outputs.append("".join(block.text for block in message.content if hasattr(block, "text")))
                    break
                except Exception:
                    if attempt + 1 == self.retries:
                        raise
                    time.sleep(2 ** attempt)
        return outputs


@dataclass
class GoogleProvider:
    model: str
    retries: int = 5

    def generate(self, prompts: list[str]) -> list[str]:
        from google import genai

        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        outputs = []
        for prompt in prompts:
            for attempt in range(self.retries):
                try:
                    response = client.models.generate_content(model=self.model, contents=prompt)
                    outputs.append(response.text or "")
                    break
                except Exception:
                    if attempt + 1 == self.retries:
                        raise
                    time.sleep(2 ** attempt)
        return outputs


@dataclass
class OpenAICompatibleProvider:
    model: str
    api_key_env: str
    base_url_env: str
    max_tokens: int = 64
    temperature: float = 0.0
    retries: int = 5

    def generate(self, prompts: list[str]) -> list[str]:
        from openai import OpenAI

        api_key = os.environ[self.api_key_env]
        base_url = os.environ[self.base_url_env]
        client = OpenAI(api_key=api_key, base_url=base_url)
        outputs = []
        for prompt in prompts:
            for attempt in range(self.retries):
                try:
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                    outputs.append(response.choices[0].message.content or "")
                    break
                except Exception:
                    if attempt + 1 == self.retries:
                        raise
                    time.sleep(2 ** attempt)
        return outputs


@dataclass
class VLLMProvider:
    model: str
    max_tokens: int = 64
    temperature: float = 0.0
    tensor_parallel_size: int = 1

    def __post_init__(self) -> None:
        from vllm import LLM, SamplingParams

        self._sampling_params = SamplingParams(max_tokens=self.max_tokens, temperature=self.temperature)
        self._llm = LLM(model=self.model, tensor_parallel_size=self.tensor_parallel_size)

    def generate(self, prompts: list[str]) -> list[str]:
        outputs = self._llm.generate(prompts, self._sampling_params)
        return [item.outputs[0].text for item in outputs]


def batched(items: list[str], batch_size: int) -> Iterable[list[str]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def make_provider(provider: str, model: str, **kwargs) -> TextProvider:
    provider = provider.lower()
    if provider == "echo":
        return EchoProvider(label=kwargs.get("label", "unknown"))
    if provider == "anthropic":
        return AnthropicProvider(model=model, max_tokens=kwargs.get("max_tokens", 64), temperature=kwargs.get("temperature", 0.0))
    if provider == "google":
        return GoogleProvider(model=model)
    if provider in {"openai_compatible", "kimi", "qwen", "deepseek"}:
        if provider == "kimi":
            api_key_env = "KIMI_API_KEY"
            base_url_env = "KIMI_BASE_URL"
        elif provider == "qwen":
            api_key_env = "DASHSCOPE_API_KEY"
            base_url_env = "DASHSCOPE_BASE_URL"
        elif provider == "deepseek":
            api_key_env = "DEEPSEEK_API_KEY"
            base_url_env = "DEEPSEEK_BASE_URL"
        else:
            api_key_env = kwargs.get("api_key_env", "OPENAI_COMPATIBLE_API_KEY")
            base_url_env = kwargs.get("base_url_env", "OPENAI_COMPATIBLE_BASE_URL")
        return OpenAICompatibleProvider(
            model=model,
            api_key_env=api_key_env,
            base_url_env=base_url_env,
            max_tokens=kwargs.get("max_tokens", 64),
            temperature=kwargs.get("temperature", 0.0),
        )
    if provider == "vllm":
        return VLLMProvider(
            model=model,
            max_tokens=kwargs.get("max_tokens", 64),
            temperature=kwargs.get("temperature", 0.0),
            tensor_parallel_size=kwargs.get("tensor_parallel_size", 1),
        )
    raise ValueError(f"Unknown provider: {provider}")
