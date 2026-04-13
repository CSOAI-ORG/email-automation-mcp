# Email Automation MCP Server

> **By [MEOK AI Labs](https://meok.ai)** — Sovereign AI tools for everyone.

Send and read emails via standard SMTP/IMAP protocols. Works with any email provider -- Gmail, Outlook, Yahoo, Fastmail, or self-hosted. Built-in safety: preview before sending, rate-limited outbound, no stored credentials.

[![MCPize](https://img.shields.io/badge/MCPize-Listed-blue)](https://mcpize.com/mcp/email-automation)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-255+_servers-purple)](https://meok.ai)

## Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send an email via SMTP |
| `read_inbox` | Read recent emails from a mailbox folder |
| `search_emails` | Search emails in a folder by query |
| `create_draft` | Save an email as a draft without sending |
| `list_folders` | List all mailbox folders |

## Quick Start

```bash
pip install mcp
git clone https://github.com/CSOAI-ORG/email-automation-mcp.git
cd email-automation-mcp
python server.py
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "email-automation": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/email-automation-mcp"
    }
  }
}
```

## Pricing

| Plan | Price | Requests |
|------|-------|----------|
| Free | $0/mo | 20 reads/day + 5 sends/day |
| Pro | $9/mo | Unlimited + attachments + HTML templates |
| Enterprise | Contact us | Custom + multi-account + audit trail |

[Get on MCPize](https://mcpize.com/mcp/email-automation)

## Part of MEOK AI Labs

This is one of 255+ MCP servers by MEOK AI Labs. Browse all at [meok.ai](https://meok.ai) or [GitHub](https://github.com/CSOAI-ORG).

---
**MEOK AI Labs** | [meok.ai](https://meok.ai) | nicholas@meok.ai | United Kingdom
