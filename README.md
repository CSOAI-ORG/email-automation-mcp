# Email Automation MCP Server
**By MEOK AI Labs** | [meok.ai](https://meok.ai)

Send and read emails via standard SMTP/IMAP protocols. Works with any email provider -- Gmail, Outlook, Yahoo, Fastmail, or self-hosted. Built-in safety: preview before sending, rate-limited outbound, no stored credentials.

## Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send an email (with preview/confirm safety gate) |
| `read_inbox` | Read recent emails from any folder |
| `search_emails` | Search by sender, subject, text, or status |
| `create_draft` | Save a draft without sending |
| `list_folders` | List all mailbox folders (INBOX, Sent, Drafts, etc.) |

## Installation

```bash
pip install mcp
```

No additional dependencies -- uses Python's built-in `smtplib` and `imaplib`.

## Configuration

Set environment variables before running:

```bash
export EMAIL_ADDRESS="you@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

**For Gmail**: You must use an [App Password](https://myaccount.google.com/apppasswords), not your regular password.

Optional overrides (auto-detected from your email domain):

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export IMAP_HOST="imap.gmail.com"
export IMAP_PORT="993"
```

### Auto-detected providers

| Provider | SMTP | IMAP |
|----------|------|------|
| Gmail | smtp.gmail.com:587 | imap.gmail.com:993 |
| Outlook/Hotmail | smtp.office365.com:587 | outlook.office365.com:993 |
| Yahoo | smtp.mail.yahoo.com:587 | imap.mail.yahoo.com:993 |
| Fastmail | smtp.fastmail.com:587 | imap.fastmail.com:993 |

## Usage

### Run the server

```bash
EMAIL_ADDRESS="you@gmail.com" EMAIL_PASSWORD="xxxx-xxxx-xxxx" python server.py
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/path/to/email-automation-mcp/server.py"],
      "env": {
        "EMAIL_ADDRESS": "you@gmail.com",
        "EMAIL_PASSWORD": "your-app-password"
      }
    }
  }
}
```

### Example calls

**Send an email (preview first):**
```
Tool: send_email
Input: {"to": "colleague@company.com", "subject": "Q2 Report", "body": "Hi, please find the Q2 report attached."}
Output: {"status": "preview", "message": "Email NOT sent. Review and call again with confirm=False to send."}
```

**Actually send after review:**
```
Tool: send_email
Input: {"to": "colleague@company.com", "subject": "Q2 Report", "body": "Hi, please find the Q2 report attached.", "confirm": false}
Output: {"status": "sent", "to": "colleague@company.com", "timestamp": "2026-04-13T14:30:22"}
```

**Read inbox:**
```
Tool: read_inbox
Input: {"limit": 5}
Output: {"total_messages": 342, "returned": 5, "emails": [{"subject": "Meeting tomorrow", "from": "boss@company.com", "date": "...", "body": "..."}]}
```

**Search emails:**
```
Tool: search_emails
Input: {"query": "subject:invoice"}
Output: {"results_found": 12, "emails": [...]}
```

**Create a draft:**
```
Tool: create_draft
Input: {"to": "client@example.com", "subject": "Proposal", "body": "Dear Client, ..."}
Output: {"status": "draft_saved", "folder": "Drafts"}
```

**List folders:**
```
Tool: list_folders
Output: {"folders": [{"name": "INBOX"}, {"name": "[Gmail]/Sent Mail"}, {"name": "[Gmail]/Drafts"}, ...], "count": 8}
```

## Safety Features

- **Send confirmation**: Emails are previewed by default. Must explicitly set `confirm=False` to send
- **Send rate limit**: Max 5 outbound emails/day on free tier
- **Read rate limit**: Max 20 operations/day on free tier
- **No credential storage**: Email/password read from environment per session
- **Read-only by default**: Inbox operations use IMAP readonly mode

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 20 reads/day + 5 sends/day | $0 |
| Pro | Unlimited + attachments + HTML templates | $9/mo |
| Enterprise | Custom + multi-account + audit trail | Contact us |

## License

MIT
