<div align="center">

# Email Automation MCP

**MCP server for email automation mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-email-automation-mcp)](https://pypi.org/project/meok-email-automation-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Email Automation MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send an email via SMTP. Requires EMAIL_ADDRESS and EMAIL_PASSWORD env vars. |
| `read_inbox` | Read recent emails from a mailbox folder. Returns subject, from, date, |
| `search_emails` | Search emails in a folder. Supports these query formats: |
| `create_draft` | Save an email as a draft without sending it. The draft appears in |
| `list_folders` | List all mailbox folders (INBOX, Sent, Drafts, etc.) available |

## Installation

```bash
pip install meok-email-automation-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "email-automation-mcp": {
      "command": "python",
      "args": ["-m", "meok_email_automation_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
