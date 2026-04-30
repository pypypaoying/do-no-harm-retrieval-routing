# Local Codex Worker MCP

This project uses the official Codex CLI MCP server as a local worker backend.

## Preflight Results

- Project root: `D:/proposal/7454939164195160320-proposal-202604290247/agents/ideation/finalized_research_proposals/do-no-harm-retrieval-routing`
- Git repository: yes.
- Codex CLI: `codex-cli 0.126.0-alpha.8`
- Codex command: `C:\Users\26698\AppData\Local\OpenAI\Codex\bin\codex.exe`
- Official MCP server command: `codex mcp-server`
- MCP management command: `codex mcp`

`codex mcp-server --help` works locally. `codex mcp list` currently fails on this machine with
`failed to load configuration: Access denied`; this appears to be a local Codex/Windows config
loading issue, not a missing `mcp-server` command.

## Project Config

The project-level config is in `.codex/config.toml`.

It registers:

```toml
[mcp_servers.local_codex_worker]
command = "codex"
args = ["mcp-server"]
cwd = "D:/proposal/7454939164195160320-proposal-202604290247/agents/ideation/finalized_research_proposals/do-no-harm-retrieval-routing"
startup_timeout_sec = 20
tool_timeout_sec = 3600
enabled = true
required = true
```

Project defaults:

```toml
sandbox_mode = "workspace-write"
approval_policy = "never"
```

No global `~/.codex/config.toml` changes are required.

## Expected Tools

The official Codex MCP server is expected to expose:

- `codex`: start a local Codex worker session.
- `codex-reply`: continue an existing worker session.

## How To Use

Restart the Codex app after this config is committed. In a coordinator prompt, ask it to use the
`local_codex_worker` MCP server for a bounded task in this repository, for example:

```text
Use local_codex_worker.codex to inspect the router scripts and report whether the DeepSeek pilot
outputs are ready for a 1000-example run. Do not read .env or secrets.
```

Keep worker tasks bounded and explicit. Do not ask workers to access files outside this repository.
