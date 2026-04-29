# Low-Cost API Options

Claude is not essential to the core method. It is a third API-model sensitivity check.

Recommended cheaper replacements:

- `qwen-plus`: cheapest and usually sufficient for API sensitivity or sufficiency autorating.
- `kimi-k2`: stronger agent/coding-style model; still far cheaper than Claude Opus-class APIs.
- `deepseek-v4-flash`: very low-cost OpenAI-compatible option.
- `deepseek-v4-pro`: stronger DeepSeek V4 model for higher-quality sensitivity/pilot runs; use after smoke tests because it is materially more expensive than Flash.

Use a model family different from the generator for sufficiency labels. For example:

- Generator: Llama / Mistral, autorater: Qwen or Kimi.
- Generator: Qwen, autorater: Kimi or DeepSeek.

Set the corresponding environment variables:

```bash
export DASHSCOPE_API_KEY=...
export DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
export KIMI_API_KEY=...
export KIMI_BASE_URL=https://api.moonshot.cn/v1
export DEEPSEEK_API_KEY=...
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DNH_MAX_CONTEXT_CHARS=6000
```

Keep `DNH_MAX_CONTEXT_CHARS` at 6000 for smoke/full API runs unless you intentionally want
to spend more on long contexts.

DashScope OpenAI-compatible endpoints vary by region. Alibaba Cloud documents these base URLs:

- Beijing: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Singapore: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Virginia: `https://dashscope-us.aliyuncs.com/compatible-mode/v1`
- Hong Kong: `https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1`

Codex Cloud may be outside mainland China, so try Singapore or Virginia first if the Beijing endpoint returns proxy `403 Forbidden`.

DeepSeek V4 pricing from the official API docs:

- `deepseek-v4-flash`: input cache hit `$0.028` / 1M, input cache miss `$0.14` / 1M, output `$0.28` / 1M.
- `deepseek-v4-pro`: input cache hit `$0.145` / 1M, input cache miss `$1.74` / 1M, output `$3.48` / 1M.

For the 200-example RAGuard pilot, the prior `deepseek-chat` run estimated about 574k input tokens and 9k output tokens.
At V4-Pro rates this is roughly `$0.12` with full input cache hit, or about `$1.03` with full cache miss.
Full 2,648-example RAGuard k=5 sensitivity is roughly 13.24 times that scale, before prompt changes and tokenizer differences.
