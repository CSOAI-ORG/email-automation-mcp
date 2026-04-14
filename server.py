#!/usr/bin/env python3
"""
Email Automation MCP Server
=============================
Send and read emails via standard SMTP/IMAP protocols. Works with any email
provider (Gmail, Outlook, Fastmail, self-hosted). Built-in safety: confirmation
before sending, rate limiting on outbound.

By MEOK AI Labs | https://meok.ai

Install: pip install mcp
Run:     python server.py

Environment variables (set before running):
    EMAIL_ADDRESS   - Your email address
    EMAIL_PASSWORD  - App password or SMTP password
    SMTP_HOST       - SMTP server (default: smtp.gmail.com)
    SMTP_PORT       - SMTP port (default: 587)
    IMAP_HOST       - IMAP server (default: imap.gmail.com)
    IMAP_PORT       - IMAP port (default: 993)
"""

import email
import email.utils
import imaplib
import json
import os
import re
import smtplib
from datetime import datetime, timedelta
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 20
FREE_SEND_LIMIT = 5  # Stricter limit for sending
_usage: dict[str, list[datetime]] = defaultdict(list)
_send_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit reached ({FREE_DAILY_LIMIT}/day). Upgrade to Pro: https://mcpize.com/email-automation-mcp/pro"
    _usage[caller].append(now)
    return None


def _check_send_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _send_usage[caller] = [t for t in _send_usage[caller] if t > cutoff]
    if len(_send_usage[caller]) >= FREE_SEND_LIMIT:
        return f"Send limit reached ({FREE_SEND_LIMIT}/day). Upgrade to Pro for higher limits: https://mcpize.com/email-automation-mcp/pro"
    _send_usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _get_config() -> dict:
    """Get email configuration from environment."""
    address = os.environ.get("EMAIL_ADDRESS", "")
    password = os.environ.get("EMAIL_PASSWORD", "")

    if not address or not password:
        raise ValueError(
            "EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set. "
            "For Gmail, use an App Password (not your regular password)."
        )

    # Auto-detect host from email domain
    domain = address.split("@")[-1].lower() if "@" in address else ""
    smtp_defaults = {
        "gmail.com": ("smtp.gmail.com", 587),
        "outlook.com": ("smtp.office365.com", 587),
        "hotmail.com": ("smtp.office365.com", 587),
        "yahoo.com": ("smtp.mail.yahoo.com", 587),
        "fastmail.com": ("smtp.fastmail.com", 587),
    }
    imap_defaults = {
        "gmail.com": ("imap.gmail.com", 993),
        "outlook.com": ("outlook.office365.com", 993),
        "hotmail.com": ("outlook.office365.com", 993),
        "yahoo.com": ("imap.mail.yahoo.com", 993),
        "fastmail.com": ("imap.fastmail.com", 993),
    }

    smtp_host, smtp_port = smtp_defaults.get(domain, ("smtp.gmail.com", 587))
    imap_host, imap_port = imap_defaults.get(domain, ("imap.gmail.com", 993))

    return {
        "address": address,
        "password": password,
        "smtp_host": os.environ.get("SMTP_HOST", smtp_host),
        "smtp_port": int(os.environ.get("SMTP_PORT", smtp_port)),
        "imap_host": os.environ.get("IMAP_HOST", imap_host),
        "imap_port": int(os.environ.get("IMAP_PORT", imap_port)),
    }


# ---------------------------------------------------------------------------
# IMAP helpers
# ---------------------------------------------------------------------------

def _decode_header_value(value: str) -> str:
    """Decode email header (handles encoded words)."""
    if not value:
        return ""
    decoded_parts = decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def _get_body(msg: email.message.Message) -> str:
    """Extract the text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
            elif ctype == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    html = payload.decode(charset, errors="replace")
                    # Strip HTML tags for plain text
                    text = re.sub(r'<[^>]+>', ' ', html)
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def _parse_email(msg: email.message.Message) -> dict:
    """Parse an email message into a dictionary."""
    return {
        "subject": _decode_header_value(msg.get("Subject", "")),
        "from": _decode_header_value(msg.get("From", "")),
        "to": _decode_header_value(msg.get("To", "")),
        "date": msg.get("Date", ""),
        "message_id": msg.get("Message-ID", ""),
        "body": _get_body(msg)[:3000],  # Limit body size
        "has_attachments": any(
            part.get_content_disposition() == "attachment"
            for part in msg.walk()
        ) if msg.is_multipart() else False,
    }


def _imap_connect(config: dict) -> imaplib.IMAP4_SSL:
    """Connect to IMAP server."""
    imap = imaplib.IMAP4_SSL(config["imap_host"], config["imap_port"])
    imap.login(config["address"], config["password"])
    return imap


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def _send_email(to: str, subject: str, body: str, html: bool = False, cc: str = "", bcc: str = "") -> dict:
    """Send an email via SMTP."""
    config = _get_config()

    msg = MIMEMultipart("alternative")
    msg["From"] = config["address"]
    msg["To"] = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc
    msg["Date"] = email.utils.formatdate(localtime=True)

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    # Build recipient list
    recipients = [addr.strip() for addr in to.split(",")]
    if cc:
        recipients.extend([addr.strip() for addr in cc.split(",")])
    if bcc:
        recipients.extend([addr.strip() for addr in bcc.split(",")])

    with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
        server.starttls()
        server.login(config["address"], config["password"])
        server.send_message(msg, to_addrs=recipients)

    return {
        "status": "sent",
        "from": config["address"],
        "to": to,
        "cc": cc,
        "subject": subject,
        "body_length": len(body),
        "timestamp": datetime.now().isoformat(),
    }


def _read_inbox(folder: str = "INBOX", limit: int = 10) -> dict:
    """Read recent emails from a folder."""
    config = _get_config()
    imap = _imap_connect(config)

    try:
        imap.select(folder, readonly=True)
        _, msg_nums = imap.search(None, "ALL")
        all_ids = msg_nums[0].split()

        # Get the most recent emails
        recent_ids = all_ids[-limit:] if all_ids else []
        recent_ids.reverse()  # Most recent first

        emails = []
        for msg_id in recent_ids:
            _, data = imap.fetch(msg_id, "(RFC822)")
            if data[0] is None:
                continue
            raw = data[0][1]
            msg = email.message_from_bytes(raw)
            emails.append(_parse_email(msg))

        return {
            "status": "ok",
            "folder": folder,
            "total_messages": len(all_ids),
            "returned": len(emails),
            "emails": emails,
        }
    finally:
        imap.logout()


def _search_emails(query: str, folder: str = "INBOX", limit: int = 10) -> dict:
    """Search emails using IMAP search criteria."""
    config = _get_config()
    imap = _imap_connect(config)

    try:
        imap.select(folder, readonly=True)

        # Build IMAP search criteria
        # Support common search patterns
        criteria_parts = []
        q = query.strip()

        if "@" in q:
            criteria_parts.append(f'FROM "{q}"')
        elif q.upper().startswith("SUBJECT:"):
            criteria_parts.append(f'SUBJECT "{q[8:].strip()}"')
        elif q.upper().startswith("FROM:"):
            criteria_parts.append(f'FROM "{q[5:].strip()}"')
        elif q.upper().startswith("TO:"):
            criteria_parts.append(f'TO "{q[3:].strip()}"')
        elif q.upper() == "UNSEEN" or q.upper() == "UNREAD":
            criteria_parts.append("UNSEEN")
        elif q.upper() == "FLAGGED" or q.upper() == "STARRED":
            criteria_parts.append("FLAGGED")
        else:
            # General text search
            criteria_parts.append(f'TEXT "{q}"')

        search_str = " ".join(criteria_parts) if criteria_parts else "ALL"
        _, msg_nums = imap.search(None, search_str)
        all_ids = msg_nums[0].split()

        recent_ids = all_ids[-limit:] if all_ids else []
        recent_ids.reverse()

        emails = []
        for msg_id in recent_ids:
            _, data = imap.fetch(msg_id, "(RFC822)")
            if data[0] is None:
                continue
            raw = data[0][1]
            msg = email.message_from_bytes(raw)
            emails.append(_parse_email(msg))

        return {
            "status": "ok",
            "query": query,
            "folder": folder,
            "results_found": len(all_ids),
            "returned": len(emails),
            "emails": emails,
        }
    finally:
        imap.logout()


def _create_draft(to: str, subject: str, body: str) -> dict:
    """Save an email as a draft (IMAP APPEND to Drafts folder)."""
    config = _get_config()

    msg = MIMEMultipart()
    msg["From"] = config["address"]
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg.attach(MIMEText(body, "plain"))

    imap = _imap_connect(config)
    try:
        # Try common draft folder names
        draft_folders = ["Drafts", "[Gmail]/Drafts", "INBOX.Drafts", "Draft"]
        saved = False
        used_folder = ""

        for folder in draft_folders:
            try:
                result = imap.append(folder, "\\Draft", None, msg.as_bytes())
                if result[0] == "OK":
                    saved = True
                    used_folder = folder
                    break
            except Exception:
                continue

        if not saved:
            return {"error": "Could not find Drafts folder. Try listing folders first."}

        return {
            "status": "draft_saved",
            "folder": used_folder,
            "to": to,
            "subject": subject,
            "body_length": len(body),
        }
    finally:
        imap.logout()


def _list_folders() -> dict:
    """List all IMAP folders/mailboxes."""
    config = _get_config()
    imap = _imap_connect(config)

    try:
        _, folder_data = imap.list()
        folders = []
        for item in folder_data:
            if isinstance(item, bytes):
                # Parse IMAP folder listing
                match = re.match(rb'\(([^)]*)\)\s+"([^"]*)"\s+"?([^"]*)"?', item)
                if match:
                    flags = match.group(1).decode()
                    delimiter = match.group(2).decode()
                    name = match.group(3).decode()
                    folders.append({
                        "name": name,
                        "flags": flags,
                        "delimiter": delimiter,
                    })
                else:
                    folders.append({"name": item.decode(errors="replace"), "flags": "", "delimiter": ""})

        return {
            "status": "ok",
            "folders": folders,
            "count": len(folders),
        }
    finally:
        imap.logout()


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Email Automation MCP",
    instructions="Email toolkit via SMTP/IMAP: send emails, read inbox, search, create drafts, and list folders. Works with Gmail, Outlook, Yahoo, Fastmail, and any standard provider. By MEOK AI Labs.")


@mcp.tool()
def send_email(to: str, subject: str, body: str, html: bool = False, cc: str = "", bcc: str = "", confirm: bool = True) -> dict:
    """Send an email via SMTP. Requires EMAIL_ADDRESS and EMAIL_PASSWORD env vars.

    Safety: Set confirm=False to actually send. When confirm=True (default),
    returns a preview without sending so the user can verify before dispatch.

    Args:
        to: Recipient email address (comma-separated for multiple)
        subject: Email subject line
        body: Email body (plain text or HTML)
        html: Set True if body is HTML
        cc: CC recipients (comma-separated)
        bcc: BCC recipients (comma-separated)
        confirm: If True, preview only (does not send). Set False to send.
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    send_err = _check_send_limit()
    if send_err:
        return {"error": send_err}

    if confirm:
        return {
            "status": "preview",
            "message": "Email NOT sent. Review the details below and call again with confirm=False to send.",
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "subject": subject,
            "body_preview": body[:500],
            "html": html,
        }

    try:
        return _send_email(to, subject, body, html, cc, bcc)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def read_inbox(folder: str = "INBOX", limit: int = 10) -> dict:
    """Read recent emails from a mailbox folder. Returns subject, from, date,
    and body preview for each message.

    Args:
        folder: IMAP folder name (default: INBOX)
        limit: Max emails to return (default: 10, max: 25)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _read_inbox(folder, min(limit, 25))
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def search_emails(query: str, folder: str = "INBOX", limit: int = 10) -> dict:
    """Search emails in a folder. Supports these query formats:
    - Email address: searches FROM field
    - 'subject:keyword': searches subject
    - 'from:name': searches sender
    - 'to:name': searches recipient
    - 'unread' or 'unseen': unread messages only
    - 'flagged' or 'starred': flagged messages
    - Any other text: full-text search

    Args:
        query: Search query
        folder: IMAP folder to search (default: INBOX)
        limit: Max results (default: 10, max: 25)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _search_emails(query, folder, min(limit, 25))
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_draft(to: str, subject: str, body: str) -> dict:
    """Save an email as a draft without sending it. The draft appears in
    your Drafts folder and can be sent later from your email client.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _create_draft(to, subject, body)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_folders() -> dict:
    """List all mailbox folders (INBOX, Sent, Drafts, etc.) available
    on the IMAP server. Useful for discovering folder names before
    reading or searching."""
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _list_folders()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
