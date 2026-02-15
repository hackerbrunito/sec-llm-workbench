# MCP (Model Context Protocol) Setup Guide

## Overview

This project uses Claude's MCP servers to access external tools and services. Currently, we use **Context7** for documentation queries.

## Supported MCP Servers

### Context7 - Documentation Query Server

**Purpose:** Query up-to-date documentation and code examples for any programming library.

**Used by:**
- code-implementer (Context7 MCP queries for library syntax)
- best-practices-enforcer (Context7 queries for standards)
- hallucination-detector (Context7 verification of APIs)

## Setup Instructions

### 1. Create `.mcp.json` from template

```bash
cp .mcp.json.example .mcp.json
```

### 2. Set CONTEXT7_API_KEY environment variable

The Context7 MCP server requires a Context7 API key. Set it in your shell:

```bash
export CONTEXT7_API_KEY="your-api-key-here"
```

Or add it to your `.env` file (this file is in .gitignore):

```bash
# .env (not in git)
CONTEXT7_API_KEY=your-api-key-here
```

#### Getting a Context7 API Key

1. Visit [Context7](https://context7.com)
2. Sign up and generate an API key
3. Add it to your `.env` file
4. Never commit this to git - keep it in `.env` only

### 3. Verify MCP is working

When Claude Code detects the .mcp.json file, it will automatically start the Context7 server.

Test by having an agent query Context7:
```python
# This should work without errors
from mcp__context7 import resolve_library_id, query_docs
```

## File Structure

```
.mcp.json            ← Local config (in .gitignore)
.mcp.json.example    ← Template (committed to git)
```

**Important:** Never commit `.mcp.json` with your actual API key. Always:
- Keep `.mcp.json` in `.gitignore` ✅
- Use `.mcp.json.example` as the template ✅
- Store actual key in `.env` ✅

## Configuration Reference

The `.mcp.json` file structure:

```json
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    }
  }
}
```

### Field Descriptions

| Field | Purpose |
|-------|---------|
| `type` | Protocol type (stdio for local execution) |
| `command` | NPM command to run the server |
| `args` | Arguments (installs latest Context7 package) |
| `env` | Environment variables (API key reference) |

## Troubleshooting

### Error: "CONTEXT7_API_KEY not found"

**Solution:** Make sure you've set the environment variable before running Claude Code:
```bash
export CONTEXT7_API_KEY="your-key"
```

### Error: "Context7 server failed to start"

**Solution:** Verify:
1. NPM is installed and working: `npm --version`
2. Internet connection (needs to download @upstash/context7-mcp)
3. API key is valid

### Error: "resolve-library-id tool not found"

**Solution:** MCP server may not have started. Restart Claude Code and check:
1. `.mcp.json` exists and is valid JSON
2. No syntax errors in `.mcp.json`

## Usage in Agents

Agents automatically use Context7 via these tools:
- `mcp__context7__resolve-library-id` - Find library ID
- `mcp__context7__query-docs` - Query documentation

### Example agent usage

```python
# Agent code (automatic, no manual calls needed)
library_id = resolve_library_id(query="pydantic", libraryName="pydantic")
docs = query_docs(libraryId=library_id, query="model_validator syntax v2")
```

## Security Notes

- **Never** commit `.mcp.json` with actual credentials
- **Always** use environment variables or `.env` (in .gitignore)
- Rotate API keys regularly
- Use scoped/limited tokens if Upstash provides that option

## Future Expansions

To add more MCP servers:

1. Update `.mcp.json.example` with new server config
2. Document in this file under "Supported MCP Servers"
3. Set required environment variables
4. Test with agents

Example adding a new server:
```json
{
  "mcpServers": {
    "context7": { ... },
    "new-server": {
      "type": "stdio",
      "command": "node",
      "args": ["./path/to/server.js"],
      "env": { ... }
    }
  }
}
```

