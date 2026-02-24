# Harness MCP Setup (Sourcegraph)

This guide shows how to attach the Sourcegraph MCP server to common agent tools/harnesses used for local ablations.

## Common Sourcegraph MCP values

```bash
export SOURCEGRAPH_URL="https://sourcegraph.com"   # or your enterprise instance
export SOURCEGRAPH_ACCESS_TOKEN="<your-token>"

# Many clients/examples use these names for the local MCP server process:
export SRC_ENDPOINT="$SOURCEGRAPH_URL"
export SRC_ACCESS_TOKEN="$SOURCEGRAPH_ACCESS_TOKEN"
```

Sourcegraph supports both:

- **Local stdio MCP server** (`npx -y @sourcegraph/mcp-server`)
- **Remote HTTP MCP endpoint** (`$SOURCEGRAPH_URL/mcp` with Bearer auth)

Use the mode your harness supports best.

## Amp (Sourcegraph Amp)

Use Amp’s MCP CLI to register the Sourcegraph server (stdio):

```bash
amp mcp add sourcegraph -- npx -y @sourcegraph/mcp-server
amp mcp list
```

If Amp supports env-scoped MCP config in your setup, ensure `SRC_ENDPOINT` and `SRC_ACCESS_TOKEN` are present in the environment before starting Amp.

## Claude Code (Anthropic)

### Local stdio MCP server

```bash
claude mcp add sourcegraph \
  --env SRC_ENDPOINT=$SOURCEGRAPH_URL \
  --env SRC_ACCESS_TOKEN=$SOURCEGRAPH_ACCESS_TOKEN \
  -- npx -y @sourcegraph/mcp-server

claude mcp list
```

### Remote HTTP MCP endpoint

```bash
claude mcp add --transport http sourcegraph "$SOURCEGRAPH_URL/mcp" \
  --header "Authorization: Bearer $SOURCEGRAPH_ACCESS_TOKEN"

claude mcp list
```

Harness auth: export `ANTHROPIC_API_KEY` (and any Anthropic-required CLI auth state).

## Codex (OpenAI Codex CLI)

### Local stdio MCP server

```bash
codex mcp add sourcegraph -- npx -y @sourcegraph/mcp-server
codex mcp list
```

### Remote HTTP MCP endpoint

```bash
codex mcp add --transport streamable-http sourcegraph "$SOURCEGRAPH_URL/mcp" \
  --header "Authorization: Bearer $SOURCEGRAPH_ACCESS_TOKEN"

codex mcp list
```

Harness auth: export `OPENAI_API_KEY`.

## Cursor

Cursor supports MCP via `mcp.json` configuration. A Sourcegraph stdio config (from Sourcegraph docs) looks like:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "npx",
      "args": ["-y", "@sourcegraph/mcp-server"],
      "env": {
        "SRC_ENDPOINT": "https://sourcegraph.com",
        "SRC_ACCESS_TOKEN": "<your-token>"
      }
    }
  }
}
```

Place it in your Cursor MCP config location (commonly `~/.cursor/mcp.json`) and restart Cursor / Cursor agent mode as needed.

Harness auth: Cursor is usually authenticated via the Cursor app/session (plus provider credentials depending your configuration).

## Copilot (GitHub)

There are two common ways to use MCP with Copilot tooling:

### GitHub Copilot Coding Agent (GitHub.com)

GitHub supports MCP server configuration in repository/org settings. Important constraints:

- Environment variables and secrets for MCP config must use the `COPILOT_MCP_` prefix.
- Remote MCP servers that require OAuth are not supported (use bearer/header auth or stdio where applicable).

Use GitHub’s MCP settings UI/JSON config for your repo/org and provide the Sourcegraph endpoint + auth accordingly.

### Copilot in VS Code / Agent mode

VS Code-based agent flows can use `.vscode/mcp.json` style config. Sourcegraph docs provide a working Sourcegraph stdio example (same schema as other `mcpServers` JSON configs).

Harness auth: sign in with GitHub/Copilot; additional provider auth may be required depending workflow.

## Gemini (Google Gemini CLI / Gemini Code Assist)

### Local stdio MCP server

```bash
gemini mcp add sourcegraph -- npx -y @sourcegraph/mcp-server
gemini mcp list
```

### Remote HTTP MCP endpoint

```bash
gemini mcp add --transport http sourcegraph "$SOURCEGRAPH_URL/mcp" \
  --header "Authorization: Bearer $SOURCEGRAPH_ACCESS_TOKEN"

gemini mcp list
```

Gemini also supports MCP config in `~/.gemini/settings.json`; Sourcegraph docs include a JSON example using the `mcpServers` schema.

Harness auth: `GOOGLE_API_KEY` or `GEMINI_API_KEY` depending your Gemini setup.

## OpenHands

OpenHands includes CLI support for MCP server registration and stores config in `~/.openhands/mcp.json`.

### Local stdio MCP server

```bash
openhands mcp add sourcegraph \
  --type stdio \
  --command npx \
  --args -y,@sourcegraph/mcp-server \
  --env SRC_ENDPOINT=$SOURCEGRAPH_URL \
  --env SRC_ACCESS_TOKEN=$SOURCEGRAPH_ACCESS_TOKEN

openhands mcp list
```

### Remote HTTP MCP endpoint

```bash
openhands mcp add sourcegraph \
  --type streamable_http \
  --url "$SOURCEGRAPH_URL/mcp" \
  --header "Authorization: Bearer $SOURCEGRAPH_ACCESS_TOKEN"

openhands mcp list
```

Harness auth: configure your OpenHands LLM provider credentials/model as usual (OpenAI/Anthropic/etc.).

## Verification checklist (all harnesses)

Before running a task:

1. Confirm your harness sees the `sourcegraph` MCP server.
2. Run a simple test query/tool call (e.g., list repos or a keyword search) before starting the benchmark task.
3. Save raw trace/log exports for both baseline and MCP runs so the scripts in `scripts/` can compare usage.

## References

- Sourcegraph MCP client setup docs: https://sourcegraph.com/docs/clients/modelcontextprotocol
- Anthropic Claude Code MCP docs: https://docs.anthropic.com/en/docs/claude-code/mcp
- OpenAI Codex MCP docs: https://platform.openai.com/docs/guides/tools-remote-mcp
- OpenAI Codex CLI docs (MCP examples): https://developers.openai.com/codex/mcp
- GitHub Copilot MCP docs: https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp
- GitHub Copilot coding agent MCP setup: https://docs.github.com/en/enterprise-cloud%40latest/copilot/concepts/about-mcp-for-copilot-coding-agent
- Google Gemini CLI config / MCP docs: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md
- OpenHands MCP overview: https://docs.all-hands.dev/openhands/usage/how-to/mcp
- OpenHands MCP server management (CLI): https://docs.all-hands.dev/openhands/usage/how-to/mcp/server-management
- OpenHands MCP settings file: https://docs.all-hands.dev/openhands/usage/how-to/mcp/settings
- Cursor MCP docs (CLI): https://docs.cursor.com/cli/mcp
