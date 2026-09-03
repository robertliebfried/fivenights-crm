import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from email_server.database import (
    init_db, get_settings, update_settings, get_all_templates,
    get_template_by_id, create_template, get_all_campaigns,
    get_campaign_by_id, get_campaign_leads, create_campaign,
    get_recent_logs, get_system_stats, get_db
)
from email_server.crm_database import (
    init_crm_db, get_all_mailboxes, get_mailbox_by_id,
    save_mailbox, delete_mailbox, import_reengagement_clients,
    get_all_agents, get_agent_by_id, save_agent, delete_agent,
    import_contacts_from_csv_list, create_single_contact,
    update_contact, delete_contact,
    get_contact_notes, add_contact_note, update_contact_note, delete_contact_note
)
from email_server.leads_loader import (
    get_loaded_leads, search_leads, get_countries_summary,
    verify_email_domain
)
from email_server.email_service import (
    render_email_content, test_smtp_connection, test_mailbox_smtp,
    send_single_email, send_single_email_via_mailbox,
    start_campaign_task, pause_campaign_task
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite database, CRM tables & pre-load leads
    await init_db()
    await init_crm_db()
    get_loaded_leads()
    print("FiveNights CRM & Outreach Server started successfully on http://localhost:8000")
    yield
    # Shutdown

app = FastAPI(title="FiveNights CRM — Multi-Domain Outreach & Dispatch Server", lifespan=lifespan)

# Pydantic Schemas
class AgentModel(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    role: str = "Outreach Specialist"
    avatar_color: str = "#2563eb"
    signature: Optional[str] = ""
    is_active: bool = True

class MailboxModel(BaseModel):
    id: Optional[int] = None
    name: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = ""
    smtp_password: Optional[str] = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    sender_name: str
    sender_email: str
    daily_limit: int = 100
    assigned_agent_id: Optional[int] = None
    provider: Optional[str] = "google_workspace"
    is_active: bool = True

class CSVImportModel(BaseModel):
    contacts: List[dict]
    default_tags: Optional[str] = "csv_import"
    assigned_agent_id: Optional[int] = None

class SingleContactModel(BaseModel):
    name: Optional[str] = ""
    contact_person: Optional[str] = ""
    company: Optional[str] = ""
    company_name: Optional[str] = ""
    email: str
    phone: Optional[str] = ""
    country: Optional[str] = "Global"
    city: Optional[str] = ""
    deal_value: Optional[float] = 0.0
    notes: Optional[str] = ""
    tags: Optional[str] = "manual_entry"
    assigned_agent_id: Optional[int] = None
    stage_id: Optional[int] = 1

class ReengagementImportModel(BaseModel):
    clients: List[dict]
    default_site: Optional[str] = "fivenights.fun"

class SettingsModel(BaseModel):
    smtp_host: str
    smtp_port: int = 587
    smtp_user: Optional[str] = ""
    smtp_password: Optional[str] = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    sender_name: str
    sender_email: str
    reply_to: Optional[str] = ""
    daily_limit: int = 50
    delay_min: int = 10
    delay_max: int = 25
    dry_run_mode: bool = True

class TemplateCreateModel(BaseModel):
    name: str
    category: str
    subject: str
    body_html: str
    body_text: str

class CampaignCreateModel(BaseModel):
    name: str
    template_id: Optional[int] = None
    custom_subject: str
    custom_body_html: str
    custom_body_text: str
    leads: List[dict]

class TestEmailModel(BaseModel):
    to_email: str
    subject: Optional[str] = "Test Email from Outreach Server"
    body_html: Optional[str] = "<p>This is a test email confirming your SMTP server configuration works!</p>"
    body_text: Optional[str] = "This is a test email confirming your SMTP server configuration works!"

class PreviewModel(BaseModel):
    subject: str
    body_html: str
    body_text: str
    lead: Optional[dict] = None

# API Endpoints
@app.get("/api/stats")
async def get_stats():
    db_stats = await get_system_stats()
    leads = get_loaded_leads()
    with_email_count = sum(1 for l in leads if l["has_email"])
    return {
        "total_leads_in_db": len(leads),
        "leads_with_email": with_email_count,
        "leads_without_email": len(leads) - with_email_count,
        **db_stats
    }

@app.get("/api/leads")
async def get_leads_api(
    query: str = "",
    country: str = "All",
    priority: str = "All",
    relevance: str = "All",
    only_with_email: bool = False,
    page: int = 1,
    page_size: int = 50
):
    return search_leads(
        query=query,
        country=country,
        priority=priority,
        relevance=relevance,
        only_with_email=only_with_email,
        page=page,
        page_size=page_size
    )

@app.get("/api/leads/countries")
async def get_countries_api():
    return get_countries_summary()

@app.post("/api/leads/verify-email")
async def verify_email_api(payload: dict):
    email = payload.get("email", "").strip()
    return verify_email_domain(email)

@app.get("/api/templates")
async def get_templates_api():
    return await get_all_templates()

@app.post("/api/templates")
async def create_template_api(payload: TemplateCreateModel):
    template_id = await create_template(
        name=payload.name,
        category=payload.category,
        subject=payload.subject,
        body_html=payload.body_html,
        body_text=payload.body_text
    )
    return {"success": True, "template_id": template_id}

@app.post("/api/preview")
async def preview_template_api(payload: PreviewModel):
    settings = await get_settings()
    sample_lead = payload.lead
    if not sample_lead:
        leads = get_loaded_leads()
        sample_lead = next((l for l in leads if l["has_email"]), leads[0] if leads else {})

    rendered_subject = render_email_content(payload.subject, sample_lead, settings)
    rendered_html = render_email_content(payload.body_html, sample_lead, settings)
    rendered_text = render_email_content(payload.body_text, sample_lead, settings)

    return {
        "sample_lead": sample_lead,
        "rendered_subject": rendered_subject,
        "rendered_html": rendered_html,
        "rendered_text": rendered_text
    }

@app.get("/api/campaigns")
async def get_campaigns_api():
    return await get_all_campaigns()

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign_detail_api(campaign_id: int):
    campaign = await get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    leads = await get_campaign_leads(campaign_id, limit=300)
    return {
        "campaign": campaign,
        "leads": leads
    }

@app.post("/api/campaigns")
async def create_campaign_api(payload: CampaignCreateModel):
    if not payload.leads:
        raise HTTPException(status_code=400, detail="No leads selected for campaign")

    campaign_id = await create_campaign(
        name=payload.name,
        template_id=payload.template_id,
        custom_subject=payload.custom_subject,
        custom_body_html=payload.custom_body_html,
        custom_body_text=payload.custom_body_text,
        leads=payload.leads
    )
    return {"success": True, "campaign_id": campaign_id}

@app.post("/api/campaigns/{campaign_id}/start")
async def start_campaign_api(campaign_id: int):
    campaign = await get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    started = start_campaign_task(campaign_id)
    return {"success": started, "message": "Campaign worker started in background"}

@app.post("/api/campaigns/{campaign_id}/pause")
async def pause_campaign_api(campaign_id: int):
    db = await get_db()
    await db.execute("UPDATE campaigns SET status = 'paused' WHERE id = ?", (campaign_id,))
    await db.commit()
    await db.close()
    paused = pause_campaign_task(campaign_id)
    return {"success": True, "message": "Campaign paused"}

@app.get("/api/settings")
async def get_settings_api():
    settings = await get_settings()
    # Mask password for security in UI response if set
    masked = dict(settings)
    if masked.get("smtp_password"):
        masked["smtp_password_configured"] = True
    else:
        masked["smtp_password_configured"] = False
    return masked

@app.post("/api/settings")
async def update_settings_api(payload: SettingsModel):
    current = await get_settings()
    data = payload.model_dump()
    # Preserve existing password if not provided
    if not data.get("smtp_password") and current.get("smtp_password"):
        data["smtp_password"] = current["smtp_password"]

    updated = await update_settings(data)
    return {"success": True, "settings": updated}

@app.post("/api/test-connection")
async def test_connection_api(payload: Optional[SettingsModel] = None):
    if payload:
        current = await get_settings()
        settings = payload.model_dump()
        if not settings.get("smtp_password") and current.get("smtp_password"):
            settings["smtp_password"] = current["smtp_password"]
    else:
        settings = await get_settings()
    return await test_smtp_connection(settings)

@app.post("/api/send-test")
async def send_test_email_api(payload: TestEmailModel):
    settings = await get_settings()
    res = await send_single_email(
        to_email=payload.to_email,
        subject=payload.subject,
        body_html=payload.body_html,
        body_text=payload.body_text,
        settings=settings
    )
    return res

@app.get("/api/logs")
async def get_logs_api(limit: int = 100):
    return await get_recent_logs(limit=limit)

# 5-Domain Multi-Mailbox API Routes
@app.get("/api/mailboxes")
async def get_mailboxes_api(agent_id: Optional[int] = None):
    return await get_all_mailboxes(agent_id=agent_id)

@app.get("/api/mailboxes/{mailbox_id}")
async def get_mailbox_detail_api(mailbox_id: int):
    mb = await get_mailbox_by_id(mailbox_id)
    if not mb:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    return mb

@app.post("/api/mailboxes")
async def save_mailbox_api(payload: MailboxModel):
    mb_id = await save_mailbox(payload.model_dump())
    return {"success": True, "mailbox_id": mb_id}

@app.post("/api/mailboxes/{mailbox_id}/test")
async def test_mailbox_api(mailbox_id: int):
    return await test_mailbox_smtp(mailbox_id)

@app.delete("/api/mailboxes/{mailbox_id}")
async def delete_mailbox_api(mailbox_id: int):
    res = await delete_mailbox(mailbox_id)
    return {"success": res}

# Inactive Client Re-engagement Import Route
@app.post("/api/reengagement/import")
async def import_reengagement_clients_api(payload: ReengagementImportModel):
    res = await import_reengagement_clients(payload.clients, default_site=payload.default_site or "fivenights.fun")
    return {"success": True, **res}

# CSV Leads / Contacts Bulk Import API Route
@app.post("/api/contacts/import-csv")
async def import_contacts_csv_api(payload: CSVImportModel):
    res = await import_contacts_from_csv_list(
        payload.contacts,
        default_tags=payload.default_tags or "csv_import",
        assigned_agent_id=payload.assigned_agent_id
    )
    return {"success": True, **res}

# Single Contact Manual Creation Route (Agents & Admin)
@app.post("/api/contacts")
async def create_single_contact_api(payload: SingleContactModel):
    contact_id = await create_single_contact(payload.model_dump())
    return {"success": True, "contact_id": contact_id}

# Contact Update Route (Admin: all fields; Agent: notes/comments only)
@app.put("/api/contacts/{contact_id}")
async def update_contact_api(contact_id: int, payload: dict, is_admin: bool = False):
    res = await update_contact(contact_id, payload, is_admin=is_admin)
    return {"success": res}

# Contact Delete Route (Admin only)
@app.delete("/api/contacts/{contact_id}")
async def delete_contact_api(contact_id: int):
    res = await delete_contact(contact_id)
    return {"success": res}

# Contact Notes & Comments Routes (Enforcing: agent can edit only notes he added)
@app.get("/api/contacts/{contact_id}/notes")
async def get_contact_notes_api(contact_id: int):
    return await get_contact_notes(contact_id)

@app.post("/api/contacts/{contact_id}/notes")
async def add_contact_note_api(contact_id: int, payload: dict):
    content = payload.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    author = payload.get("author", "Agent")
    author_id = payload.get("author_id")
    note_id = await add_contact_note(contact_id, content, author=author, author_id=author_id)
    return {"success": True, "note_id": note_id}

@app.put("/api/notes/{note_id}")
async def update_contact_note_api(note_id: int, payload: dict, agent_id: Optional[int] = None, is_admin: bool = False):
    content = payload.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    ok, msg = await update_contact_note(note_id, content, agent_id=agent_id, is_admin=is_admin)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)
    return {"success": True, "message": msg}

@app.delete("/api/notes/{note_id}")
async def delete_contact_note_api(note_id: int, agent_id: Optional[int] = None, is_admin: bool = False):
    ok, msg = await delete_contact_note(note_id, agent_id=agent_id, is_admin=is_admin)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)
    return {"success": True, "message": msg}

# Team Agents API Routes (Max, Fred, Chriss)
@app.get("/api/agents")
async def get_agents_api():
    return await get_all_agents()

@app.get("/api/agents/{agent_id}")
async def get_agent_detail_api(agent_id: int):
    agent = await get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/api/agents")
async def save_agent_api(payload: AgentModel):
    agent_id = await save_agent(payload.model_dump())
    return {"success": True, "agent_id": agent_id}

@app.delete("/api/agents/{agent_id}")
async def delete_agent_api(agent_id: int):
    res = await delete_agent(agent_id)
    return {"success": res}

# Static UI Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
