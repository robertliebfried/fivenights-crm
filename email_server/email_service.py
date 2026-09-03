import asyncio
import random
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from jinja2 import Template
import aiosmtplib

from email_server.database import (
    get_settings, log_email_action, get_campaign_by_id,
    get_campaign_leads, get_db
)
from email_server.crm_database import (
    get_all_mailboxes, get_mailbox_by_id, increment_mailbox_sent
)
from email_server.leads_loader import verify_email_domain

# Global background worker state
_ACTIVE_CAMPAIGNS = {} # campaign_id -> asyncio.Task

def render_email_content(template_str: str, lead_data: dict, settings: dict) -> str:
    """Safely render Jinja2 placeholders with lead data and settings"""
    try:
        tmpl = Template(template_str)
        company = lead_data.get("company_name") or lead_data.get("name", "")
        contact_name = lead_data.get("name") or lead_data.get("contact_person") or company or "Valued Client"
        site_name = lead_data.get("site_name") or settings.get("site_name", "fivenights.fun")
        last_active = lead_data.get("last_active", "several months ago")

        context = {
            "company_name": company,
            "contact_name": contact_name,
            "site_name": site_name,
            "last_active": last_active,
            "country": lead_data.get("country", ""),
            "organization_type": lead_data.get("organization_type", ""),
            "regulator": lead_data.get("regulator", ""),
            "licence_number": lead_data.get("licence_number", ""),
            "relevance": lead_data.get("relevance", ""),
            "city": lead_data.get("city", "") or lead_data.get("country", ""),
            "sender_name": settings.get("sender_name", "FiveNights Team"),
            "sender_email": settings.get("sender_email", "")
        }
        return tmpl.render(**context)
    except Exception as e:
        print(f"Error rendering template: {e}")
        return template_str

async def test_smtp_connection(settings: dict) -> dict:
    """Test connecting and authenticating to the configured SMTP server"""
    host = settings.get("smtp_host", "").strip()
    port = int(settings.get("smtp_port", 587))
    user = settings.get("smtp_user", "").strip()
    password = settings.get("smtp_password", "")
    use_tls = bool(settings.get("smtp_use_tls", True))
    use_ssl = bool(settings.get("smtp_use_ssl", False))

    if not host or host == "smtp.yourdomain.com":
        return {"success": False, "message": "SMTP host is empty or unconfigured"}

    try:
        smtp = aiosmtplib.SMTP(
            hostname=host,
            port=port,
            use_tls=use_ssl,
            start_tls=use_tls and not use_ssl,
            timeout=10
        )
        await smtp.connect()
        if user and password:
            await smtp.login(user, password)
        await smtp.quit()
        return {"success": True, "message": f"Connected & authenticated successfully to {host}:{port}!"}
    except Exception as e:
        return {"success": False, "message": f"SMTP Connection Failed: {str(e)}"}

async def test_mailbox_smtp(mailbox_id: int) -> dict:
    """Test SMTP connection for a specific mailbox from database"""
    mb = await get_mailbox_by_id(mailbox_id, include_password=True)
    if not mb:
        return {"success": False, "message": f"Mailbox #{mailbox_id} not found"}
    return await test_smtp_connection(mb)

async def send_single_email_via_mailbox(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str,
    mailbox: dict,
    is_dry_run: bool = True
) -> dict:
    """Send an individual email via a specific domain mailbox or record dry-run"""
    sender_name = mailbox.get("sender_name", "FiveNights Support")
    sender_email = mailbox.get("sender_email", "")
    mb_name = mailbox.get("name", "Domain")

    # Check recipient MX validity
    mx_check = verify_email_domain(to_email)
    if not mx_check.get("valid", False):
        return {
            "success": False,
            "error": f"Recipient domain validation failed: {mx_check.get('reason')}",
            "is_dry_run": is_dry_run,
            "mailbox_used": mb_name
        }

    if is_dry_run:
        return {
            "success": True,
            "message": f"[DRY-RUN via {mb_name}] Email prepared for {to_email} from {sender_email}. (No real email sent)",
            "is_dry_run": True,
            "mailbox_used": mb_name
        }

    # Live dispatch
    host = mailbox.get("smtp_host", "").strip()
    port = int(mailbox.get("smtp_port", 587))
    user = mailbox.get("smtp_user", "").strip()
    password = mailbox.get("smtp_password", "")
    use_tls = bool(mailbox.get("smtp_use_tls", True))
    use_ssl = bool(mailbox.get("smtp_use_ssl", False))

    if not host or not sender_email:
        return {
            "success": False,
            "error": f"Mailbox {mb_name} is missing SMTP host or sender email",
            "is_dry_run": False
        }

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="fivenights.fun")

    if body_text:
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=host,
            port=port,
            username=user if user else None,
            password=password if password else None,
            use_tls=use_ssl,
            start_tls=use_tls and not use_ssl,
            timeout=15
        )
        if mailbox.get("id"):
            await increment_mailbox_sent(mailbox["id"])
        return {"success": True, "message": "Dispatched successfully", "is_dry_run": False, "mailbox_used": mb_name}
    except Exception as e:
        return {"success": False, "error": str(e), "is_dry_run": False, "mailbox_used": mb_name}

async def send_single_email(to_email: str, subject: str, body_html: str, body_text: str, settings: dict) -> dict:
    """Legacy wrapper for single send using global settings"""
    is_dry_run = bool(settings.get("dry_run_mode", True))
    return await send_single_email_via_mailbox(
        to_email=to_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        mailbox=settings,
        is_dry_run=is_dry_run
    )

async def run_campaign_worker(campaign_id: int):
    """Background task for processing campaign leads with 5-domain round-robin rotation"""
    print(f"Starting campaign worker for Campaign #{campaign_id}...")
    
    db = await get_db()
    try:
        # Mark campaign as running
        await db.execute(
            "UPDATE campaigns SET status = 'running', started_at = CURRENT_TIMESTAMP WHERE id = ?",
            (campaign_id,)
        )
        await db.commit()

        campaign = await get_campaign_by_id(campaign_id)
        if not campaign:
            return

        settings = await get_settings()
        delay_min = int(settings.get("delay_min", 10))
        delay_max = int(settings.get("delay_max", 25))
        is_dry_run = bool(settings.get("dry_run_mode", True))

        # Fetch all available active mailboxes for 5-domain round-robin
        all_mb = await get_all_mailboxes()
        active_mailboxes = [m for m in all_mb if m.get("is_active")]
        if not active_mailboxes:
            # Fallback to primary settings
            active_mailboxes = [settings]

        # Get pending leads
        async with db.execute(
            "SELECT * FROM campaign_leads WHERE campaign_id = ? AND status = 'pending' ORDER BY id ASC",
            (campaign_id,)
        ) as cursor:
            pending_leads = [dict(r) for r in await cursor.fetchall()]

        template_subject = campaign.get("custom_subject", "")
        template_body_html = campaign.get("custom_body_html", "")
        template_body_text = campaign.get("custom_body_text", "")

        mb_index = 0

        for lead in pending_leads:
            # Check if campaign was paused/cancelled
            async with db.execute("SELECT status FROM campaigns WHERE id = ?", (campaign_id,)) as c:
                cur_status = (await c.fetchone())[0]
                if cur_status in ['paused', 'cancelled']:
                    print(f"Campaign #{campaign_id} {cur_status}. Stopping worker.")
                    break

            to_email = lead.get("email", "").strip()
            company_name = lead.get("company_name", "")

            # Select mailbox using round-robin rotation across active domains
            # Find next mailbox that hasn't reached daily limit
            selected_mb = None
            for _ in range(len(active_mailboxes)):
                cand = active_mailboxes[mb_index % len(active_mailboxes)]
                mb_index += 1
                daily_limit = int(cand.get("daily_limit", 50))
                sent_today = int(cand.get("sent_today", 0))
                if is_dry_run or sent_today < daily_limit:
                    selected_mb = cand
                    break

            if not selected_mb:
                selected_mb = active_mailboxes[0]

            # Render content with selected sender information
            sender_override = dict(settings)
            sender_override["sender_name"] = selected_mb.get("sender_name", settings.get("sender_name"))
            sender_override["sender_email"] = selected_mb.get("sender_email", settings.get("sender_email"))
            sender_override["site_name"] = "fivenights.fun"

            subject = render_email_content(template_subject, lead, sender_override)
            body_html = render_email_content(template_body_html, lead, sender_override)
            body_text = render_email_content(template_body_text, lead, sender_override)

            # Send or Dry-Run via selected domain mailbox
            full_mb = await get_mailbox_by_id(selected_mb.get("id", 1), include_password=True) or selected_mb
            res = await send_single_email_via_mailbox(to_email, subject, body_html, body_text, full_mb, is_dry_run)

            mb_label = res.get("mailbox_used", selected_mb.get("name", "Domain"))

            if res.get("success"):
                status_code = f"DRY_RUN_{mb_label}" if is_dry_run else f"SENT_{mb_label}"
                await db.execute(
                    "UPDATE campaign_leads SET status = 'sent', sent_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (lead["id"],)
                )
                await db.execute(
                    "UPDATE campaigns SET sent_count = sent_count + 1 WHERE id = ?",
                    (campaign_id,)
                )
                await log_email_action(
                    campaign_id=campaign_id,
                    recipient=to_email,
                    company_name=company_name,
                    subject=subject,
                    status=status_code,
                    error_details=f"Dispatched via {mb_label}",
                    is_dry_run=is_dry_run
                )
            else:
                err_msg = res.get("error", "Unknown error")
                await db.execute(
                    "UPDATE campaign_leads SET status = 'failed', error_msg = ? WHERE id = ?",
                    (f"[{mb_label}] {err_msg}", lead["id"])
                )
                await db.execute(
                    "UPDATE campaigns SET failed_count = failed_count + 1 WHERE id = ?",
                    (campaign_id,)
                )
                await log_email_action(
                    campaign_id=campaign_id,
                    recipient=to_email,
                    company_name=company_name,
                    subject=subject,
                    status="FAILED",
                    error_details=f"[{mb_label}] {err_msg}",
                    is_dry_run=is_dry_run
                )

            await db.commit()

            # Random anti-spam jitter delay between emails (fast in dry-run)
            delay = random.uniform(delay_min, delay_max) if not is_dry_run else 0.15
            await asyncio.sleep(delay)

        # Check if all leads are processed
        async with db.execute(
            "SELECT COUNT(*) FROM campaign_leads WHERE campaign_id = ? AND status = 'pending'",
            (campaign_id,)
        ) as cursor:
            rem = (await cursor.fetchone())[0]
            if rem == 0:
                await db.execute(
                    "UPDATE campaigns SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (campaign_id,)
                )
                await db.commit()
                print(f"Campaign #{campaign_id} completed all dispatches!")

    except Exception as e:
        print(f"Error in campaign worker #{campaign_id}: {e}")
    finally:
        await db.close()
        if campaign_id in _ACTIVE_CAMPAIGNS:
            del _ACTIVE_CAMPAIGNS[campaign_id]

def start_campaign_task(campaign_id: int):
    if campaign_id not in _ACTIVE_CAMPAIGNS or _ACTIVE_CAMPAIGNS[campaign_id].done():
        task = asyncio.create_task(run_campaign_worker(campaign_id))
        _ACTIVE_CAMPAIGNS[campaign_id] = task
        return True
    return False

def pause_campaign_task(campaign_id: int):
    if campaign_id in _ACTIVE_CAMPAIGNS:
        task = _ACTIVE_CAMPAIGNS[campaign_id]
        task.cancel()
        del _ACTIVE_CAMPAIGNS[campaign_id]
        return True
    return False

