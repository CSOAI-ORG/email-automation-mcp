<!-- mcp-name: io.github.CSOAI-ORG/email-automation-mcp -->
[![MCP Scorecard: 86/100](https://img.shields.io/badge/proofof.ai-86%2F100-5b21b6)](https://proofof.ai/scorecard/email-automation-mcp.html)

# Email Automation MCP

[![MEOK AI Labs](https://img.shields.io/badge/MEOK-AI%20Labs-667eea)](https://meok.ai)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Install-3775a9)](https://pypi.org/project/email_automation_mcp/)

> Email toolkit via SMTP/IMAP: send emails, read inbox, search, create drafts, and list folders

Email toolkit via SMTP/IMAP: send emails, read inbox, search, create drafts, and list folders. Works with Gmail, Outlook, Yahoo, Fastmail, and any standard provider. By MEOK AI Labs.

---

## 🚀 Quick Start

```bash
# Install via pip
pip install email_automation_mcp

# Or install via Smithery
npx -y @smithery/cli@latest install email-automation-mcp --client claude
```

## ✨ Features

- MCP protocol compliant
- Easy installation
- Well-documented API
- Production-ready
- Active maintenance

## 📖 Documentation

- [Full Documentation](https://docs.meok.ai/email-automation-mcp)
- [API Reference](https://api.meok.ai)
- [EU AI Act Compliance Guide](https://councilof.ai/compliance)

## 🛡️ Compliance

This MCP server is built with **EU AI Act compliance** built-in:

- ✅ Article 9 — Risk Management System
- ✅ Article 13 — Transparency & Instructions for Use
- ✅ Article 15 — Bias Detection & Testing
- ✅ Article 26 — FRIA Support (where applicable)
- ✅ Article 50 — AI Content Watermarking (where applicable)

Need help getting compliant? **[Book a free 15-min diagnostic →](https://cal.com/csoai/august-audit)**

## How MEOK charges

MEOK has no subscriptions and no tiers. You pay per job, and only when the agreed artifact has been delivered to you. There is no public price list. See <https://meok.ai/pricing>.

This repository's source is MIT-licensed and free to self-host.

## 🤝 Part of the MEOK Ecosystem

This server is part of the **[MEOK AI Labs](https://meok.ai)** ecosystem — 300+ MCP servers for sovereign AI governance.

| Domain | Purpose |
|--------|---------|
| [councilof.ai](https://councilof.ai) | EU AI Act compliance marketplace |
| [safetyof.ai](https://safetyof.ai) | AI safety & monitoring |
| [meok.ai](https://meok.ai) | Sovereign AI platform |
| [cobolbridge.ai](https://cobolbridge.ai) | Legacy modernization |

## 📜 License

MIT © [CSOAI-ORG](https://github.com/CSOAI-ORG)

---

<p align="center">
  <sub>Built with 💜 by <a href="https://meok.ai">MEOK AI Labs</a> · UK Companies House 16939677</sub>
</p>
MIT © [MEOK AI Labs](https://meok.ai)

<!-- meok-moat-footer-v1 -->
---

## Pairs with MEOK Governance Suite

Build something that touches users? You need compliance. MEOK ships 38 governance MCPs that drop in alongside this tool — EU AI Act, DORA, NIS2, CRA, GDPR, ISO 42001, FDA SaMD, MDR, Basel, MiFID II, MiCA, COPPA, and more.

```bash
# One-shot install of the governance pack
npx meok-setup --pack governance
```


→ Full catalogue: [councilof.ai](https://councilof.ai)
→ MEOK AI Labs: [meok.ai](https://meok.ai)




## Configuration

Add to your `claude_desktop_config.json` (Claude Desktop) or your MCP client config:

```json
{
  "mcpServers": {
    "email-automation-mcp": {
      "command": "uvx",
      "args": ["email-automation-mcp"]
    }
  }
}
```

Or: `pip install email-automation-mcp` then run the `email-automation-mcp` command (stdio transport).

## Examples

Once configured, ask your assistant, for example:
- "Use `send_email` to …"
- "Use `read_inbox` to …"
- "Use `search_emails` to …"

## See also

MEOK compliance MCP fleet:
[`email-validator-ai-mcp`](https://github.com/CSOAI-ORG/email-validator-ai-mcp)
