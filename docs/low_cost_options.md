# Low-Cost API Options

Claude is not essential to the core method. It is a third API-model sensitivity check.

Recommended cheaper replacements:

- `qwen-plus`: cheapest and usually sufficient for API sensitivity or sufficiency autorating.
- `kimi-k2`: stronger agent/coding-style model; still far cheaper than Claude Opus-class APIs.
- `deepseek-v4-flash`: very low-cost OpenAI-compatible option.

Use a model family different from the generator for sufficiency labels. For example:

- Generator: Llama / Mistral, autorater: Qwen or Kimi.
- Generator: Qwen, autorater: Kimi or DeepSeek.

Set the corresponding environment variables:

```bash
export DASHSCOPE_API_KEY=...
export DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export KIMI_API_KEY=...
export KIMI_BASE_URL=https://api.moonshot.cn/v1
export DEEPSEEK_API_KEY=...
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DNH_MAX_CONTEXT_CHARS=6000
```

Keep `DNH_MAX_CONTEXT_CHARS` at 6000 for smoke/full API runs unless you intentionally want
to spend more on long contexts.
