# VSCode 本地运行流程

这套流程适合在本机 VSCode 中跑数据处理、国产 API 小样本、router 训练和论文表格生成。
本机 8GB 显存不适合直接跑 Llama/Mistral 7B/8B 全量推理；开源大模型全量推理建议放到 AutoDL/租卡服务器。

## 1. 打开仓库

在 VSCode 中打开仓库根目录：

```text
D:\proposal\7454939164195160320-proposal-202604290247\agents\ideation\finalized_research_proposals\do-no-harm-retrieval-routing
```

安装推荐扩展：

- Python
- GitLens（可选）
- LaTeX Workshop（写论文时可选）

## 2. 创建 `.env`

复制 `.env.example` 为 `.env`，至少填 DeepSeek 或 Qwen 其中一个。

DeepSeek 示例：

```text
DEEPSEEK_API_KEY=你的DeepSeekKey
DEEPSEEK_BASE_URL=https://api.deepseek.com
DNH_MAX_CONTEXT_CHARS=6000
```

Qwen 示例：

```text
DASHSCOPE_API_KEY=你的阿里百炼Key
DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
DNH_MAX_CONTEXT_CHARS=6000
```

`.env` 已经在 `.gitignore` 中，不要提交。

## 3. 安装依赖

在 VSCode 里按 `Ctrl+Shift+P`，选择：

```text
Tasks: Run Task
```

运行：

```text
Setup: create venv and install deps
```

如果你更喜欢终端：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

## 4. 检查环境

运行 VSCode task：

```text
Check: environment
```

重点看：

- `external_data/raguard/claims.csv` 是否存在；
- `external_data/raguard/documents.csv` 是否存在；
- `DEEPSEEK_API_KEY` 或 `DASHSCOPE_API_KEY` 是否显示 `<set>`；
- `DNH_MAX_CONTEXT_CHARS` 是否为 `6000`。

## 5. 跑本地无 API 测试

运行：

```text
Test: unit tests
Smoke: local echo pipeline
```

也可以终端执行：

```powershell
.\.venv\Scripts\python.exe scripts\run_unit_tests.py
.\.venv\Scripts\python.exe scripts\smoke_test.py --run-id vscode-smoke
```

## 6. 生成 RAGuard JSONL

运行：

```text
Data: build RAGuard jsonl
```

或终端：

```powershell
.\.venv\Scripts\python.exe scripts\download_data.py --config configs\raguard.yaml --output data\raguard.jsonl
```

预期输出：`Wrote 2648 records to data\raguard.jsonl`

## 7. API 连通性测试

先只发 1 次请求。

DeepSeek：

```text
API: check DeepSeek
```

Qwen：

```text
API: check Qwen
```

成功时应看到 `raw_output`、`parsed_label`、`parsed_confidence`。
如果失败：

- `KeyError` / `<missing>`：`.env` 没填或 VSCode 没加载；
- `401`：API key 错；
- `403 ProxyError`：本地代理/网络拦截；
- `429`：限流或余额问题。

## 8. 20 条 API smoke

DeepSeek：

```text
API: DeepSeek 20-example smoke
```

终端等价命令：

```powershell
.\.venv\Scripts\python.exe scripts\download_data.py --config configs\raguard.yaml --output data\raguard.jsonl
.\.venv\Scripts\python.exe scripts\generate_candidates.py --input data\raguard.jsonl --output runs\deepseek-smoke\candidates\deepseek-chat-k5.jsonl --provider deepseek --model deepseek-chat --k 5 --limit 20 --batch-size 2
```

成功后检查：

```powershell
Get-Content runs\deepseek-smoke\candidates\deepseek-chat-k5.jsonl | Measure-Object -Line
```

应为 20 行。

## 9. 下一步扩量策略

不要从 20 条直接跳全量。建议：

1. 20 条 API smoke；
2. 200 条 API pilot；
3. 全量 RAGuard API sensitivity；
4. 租卡跑 Llama/Mistral 开源模型。

200 条示例：

```powershell
.\.venv\Scripts\python.exe scripts\generate_candidates.py --input data\raguard.jsonl --output runs\deepseek-pilot\candidates\deepseek-chat-k5.jsonl --provider deepseek --model deepseek-chat --k 5 --limit 200 --batch-size 2
```

## 10. 结果训练和表格

有 candidates 后：

```powershell
.\.venv\Scripts\python.exe scripts\train_router.py --candidates runs\deepseek-smoke\candidates\deepseek-chat-k5.jsonl --output runs\deepseek-smoke\metrics\router.json --folds 2
.\.venv\Scripts\python.exe scripts\make_tables.py --metrics runs\deepseek-smoke\metrics\router.json --output runs\deepseek-smoke\tables\router.tex
.\.venv\Scripts\python.exe scripts\summarize_results.py --run-dir runs\deepseek-smoke
```

Smoke 阶段结果不用于论文，只用于确认链路。
